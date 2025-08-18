#!/usr/bin/env python3
"""
NBA Game Outcome Prediction Model - Fixed Version
================================================

Fixed to work with the actual column names in the Kaggle dataset.

Author: Claude Code
Date: 2025-08-18
"""

import os
import sys
import warnings
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.model_selection import train_test_split, TimeSeriesSplit, cross_val_score
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, roc_auc_score, log_loss

import kagglehub

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Suppress warnings for cleaner output
warnings.filterwarnings('ignore')

class NBADataAnalyzer:
    """Class for analyzing NBA data and creating visualizations"""
    
    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()
        
    def create_basic_visualizations(self):
        """Create basic visualizations for data understanding"""
        plt.style.use('default')
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('NBA Dataset Analysis', fontsize=16, fontweight='bold')
        
        # 1. Home vs Away wins distribution
        if 'winner' in self.df.columns:
            # winner = 1 means home team won, 0 means away team won
            home_wins = self.df['winner'].value_counts().sort_index()
            labels = ['Away Win', 'Home Win'] if len(home_wins) == 2 else [f'Winner {i}' for i in home_wins.index]
            
            axes[0,0].pie(home_wins.values, labels=labels[:len(home_wins)], autopct='%1.1f%%', 
                         colors=['lightcoral', 'lightblue'])
            axes[0,0].set_title('Home vs Away Win Distribution')
        
        # 2. Score distribution
        if 'homeScore' in self.df.columns and 'awayScore' in self.df.columns:
            axes[0,1].hist(self.df['homeScore'].dropna(), bins=30, alpha=0.7, label='Home Score', color='blue')
            axes[0,1].hist(self.df['awayScore'].dropna(), bins=30, alpha=0.7, label='Away Score', color='red')
            axes[0,1].set_xlabel('Score')
            axes[0,1].set_ylabel('Frequency')
            axes[0,1].set_title('Score Distribution')
            axes[0,1].legend()
        
        # 3. Score difference distribution
        if 'homeScore' in self.df.columns and 'awayScore' in self.df.columns:
            score_diff = self.df['homeScore'] - self.df['awayScore']
            axes[1,0].hist(score_diff.dropna(), bins=40, alpha=0.7, color='green')
            axes[1,0].axvline(x=0, color='red', linestyle='--', label='Tie')
            axes[1,0].set_xlabel('Score Difference (Home - Away)')
            axes[1,0].set_ylabel('Frequency')
            axes[1,0].set_title('Score Difference Distribution')
            axes[1,0].legend()
        
        # 4. Average scores by game type
        if 'gameType' in self.df.columns and 'homeScore' in self.df.columns:
            avg_scores = self.df.groupby('gameType')[['homeScore', 'awayScore']].mean()
            x_pos = np.arange(len(avg_scores))
            width = 0.35
            
            axes[1,1].bar(x_pos - width/2, avg_scores['homeScore'], width, 
                         label='Home Score', alpha=0.7, color='blue')
            axes[1,1].bar(x_pos + width/2, avg_scores['awayScore'], width, 
                         label='Away Score', alpha=0.7, color='red')
            axes[1,1].set_xlabel('Game Type')
            axes[1,1].set_ylabel('Average Score')
            axes[1,1].set_title('Average Scores by Game Type')
            axes[1,1].set_xticks(x_pos)
            axes[1,1].set_xticklabels(avg_scores.index, rotation=45)
            axes[1,1].legend()
        
        plt.tight_layout()
        
        # Create directory if it doesn't exist
        os.makedirs('/Users/adamnouri/Downloads/first-website/ml-service/data/processed', exist_ok=True)
        plt.savefig('/Users/adamnouri/Downloads/first-website/ml-service/data/processed/nba_analysis.png', 
                   dpi=300, bbox_inches='tight')
        plt.show()
        
        # Print some key statistics
        print("\nKEY STATISTICS:")
        print("=" * 50)
        if 'winner' in self.df.columns:
            home_win_rate = self.df['winner'].mean()
            print(f"Home team win rate: {home_win_rate:.1%}")
        
        if 'homeScore' in self.df.columns and 'awayScore' in self.df.columns:
            avg_home_score = self.df['homeScore'].mean()
            avg_away_score = self.df['awayScore'].mean()
            print(f"Average home score: {avg_home_score:.1f}")
            print(f"Average away score: {avg_away_score:.1f}")
            
            score_diff = self.df['homeScore'] - self.df['awayScore']
            avg_margin = abs(score_diff).mean()
            print(f"Average winning margin: {avg_margin:.1f} points")
        
        if 'attendance' in self.df.columns:
            avg_attendance = self.df['attendance'].mean()
            print(f"Average attendance: {avg_attendance:,.0f}")
        
        return fig

class NBAFeatureEngine:
    """Class for feature engineering NBA data"""
    
    def __init__(self, games_df: pd.DataFrame):
        self.games_df = games_df.copy()
        self.features_df = None
        
    def calculate_team_strength(self, df: pd.DataFrame) -> Dict[str, float]:
        """Calculate Elo-like team strength ratings"""
        team_ratings = {}
        initial_rating = 1500
        k_factor = 32
        
        # Get unique teams
        all_teams = set()
        if 'hometeamId' in df.columns:
            all_teams.update(df['hometeamId'].dropna().unique())
        if 'awayteamId' in df.columns:
            all_teams.update(df['awayteamId'].dropna().unique())
        
        # Initialize ratings
        for team in all_teams:
            team_ratings[team] = initial_rating
        
        # Sort by date for chronological processing
        df_sorted = df.copy()
        if 'gameDate' in df_sorted.columns:
            df_sorted['gameDate'] = pd.to_datetime(df_sorted['gameDate'])
            df_sorted = df_sorted.sort_values('gameDate')
        
        # Calculate ratings game by game
        for _, game in df_sorted.iterrows():
            if (pd.notna(game.get('homeScore')) and pd.notna(game.get('awayScore')) and
                pd.notna(game.get('hometeamId')) and pd.notna(game.get('awayteamId'))):
                
                home_team = game['hometeamId']
                away_team = game['awayteamId']
                
                if home_team in team_ratings and away_team in team_ratings:
                    home_rating = team_ratings[home_team]
                    away_rating = team_ratings[away_team]
                    
                    expected_home = 1 / (1 + 10**((away_rating - home_rating) / 400))
                    
                    actual_home = 1 if game['homeScore'] > game['awayScore'] else 0
                    
                    new_home_rating = home_rating + k_factor * (actual_home - expected_home)
                    new_away_rating = away_rating + k_factor * ((1 - actual_home) - (1 - expected_home))
                    
                    team_ratings[home_team] = new_home_rating
                    team_ratings[away_team] = new_away_rating
        
        return team_ratings
    
    def calculate_rolling_stats(self, df: pd.DataFrame, team_stats_df: pd.DataFrame = None) -> pd.DataFrame:
        """Calculate rolling statistics for teams"""
        df_enhanced = df.copy()
        
        if team_stats_df is not None:
            # Aggregate team statistics
            team_avg_stats = team_stats_df.groupby('teamId').agg({
                'teamScore': 'mean',
                'assists': 'mean',
                'reboundsTotal': 'mean',
                'fieldGoalsPercentage': 'mean',
                'threePointersPercentage': 'mean',
                'turnovers': 'mean'
            }).reset_index()
            
            # Merge with games data
            df_enhanced = df_enhanced.merge(
                team_avg_stats.add_prefix('home_'), 
                left_on='hometeamId', 
                right_on='home_teamId', 
                how='left'
            )
            df_enhanced = df_enhanced.merge(
                team_avg_stats.add_prefix('away_'), 
                left_on='awayteamId', 
                right_on='away_teamId', 
                how='left'
            )
        
        return df_enhanced
    
    def engineer_features(self, team_stats_df: pd.DataFrame = None) -> pd.DataFrame:
        """Main feature engineering pipeline"""
        df = self.games_df.copy()
        
        # Ensure we have required columns
        required_cols = ['hometeamId', 'awayteamId', 'homeScore', 'awayScore']
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            logger.error(f"Missing required columns: {missing_cols}")
            return None
        
        # Convert date column
        if 'gameDate' in df.columns:
            df['gameDate'] = pd.to_datetime(df['gameDate'])
            
        # Create target variable (winner column should already exist, but let's be sure)
        df['home_win'] = (df['homeScore'] > df['awayScore']).astype(int)
        df['score_difference'] = df['homeScore'] - df['awayScore']
        df['total_score'] = df['homeScore'] + df['awayScore']
        
        # Calculate team strength ratings
        team_ratings = self.calculate_team_strength(df)
        df['home_team_rating'] = df['hometeamId'].map(team_ratings)
        df['away_team_rating'] = df['awayteamId'].map(team_ratings)
        df['rating_difference'] = df['home_team_rating'] - df['away_team_rating']
        
        # Add home advantage feature
        df['home_advantage'] = 1
        
        # Calculate rolling stats if team stats are available
        if team_stats_df is not None:
            df = self.calculate_rolling_stats(df, team_stats_df)
        
        # Create interaction features
        if 'home_team_rating' in df.columns and 'away_team_rating' in df.columns:
            df['rating_product'] = df['home_team_rating'] * df['away_team_rating']
            df['rating_sum'] = df['home_team_rating'] + df['away_team_rating']
        
        # Add game type features if available
        if 'gameType' in df.columns:
            df['is_playoff'] = (df['gameType'] == 'Playoff').astype(int)
            df['is_regular_season'] = (df['gameType'] == 'Regular Season').astype(int)
        
        # Add attendance feature if available
        if 'attendance' in df.columns:
            df['attendance_filled'] = df['attendance'].fillna(df['attendance'].median())
            # Normalize attendance
            max_attendance = df['attendance'].max()
            if max_attendance > 0:
                df['attendance_normalized'] = df['attendance_filled'] / max_attendance
        
        self.features_df = df
        return df

class NBAPredictor:
    """Main NBA game outcome prediction class"""
    
    def __init__(self):
        self.models = {}
        self.feature_columns = []
        self.scaler = StandardScaler()
        self.is_fitted = False
        
    def prepare_features(self, df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
        """Prepare features for model training"""
        # Select numeric features for modeling
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        
        # Remove target and identifier columns
        exclude_cols = [
            'home_win', 'homeScore', 'awayScore', 'score_difference', 'total_score',
            'gameId', 'hometeamId', 'awayteamId', 'winner', 'arenaId',
            'home_teamId', 'away_teamId'  # From merged data
        ]
        feature_cols = [col for col in numeric_cols if col not in exclude_cols]
        
        # Ensure we have features
        if not feature_cols:
            logger.error("No suitable features found")
            return None, None
        
        X = df[feature_cols].fillna(0)
        y = df['home_win'] if 'home_win' in df.columns else None
        
        self.feature_columns = feature_cols
        logger.info(f"Using {len(feature_cols)} features: {feature_cols}")
        
        return X.values, y.values if y is not None else None
    
    def train_models(self, X: np.ndarray, y: np.ndarray):
        """Train multiple models for comparison"""
        if X is None or y is None:
            logger.error("Cannot train models with null data")
            return None
            
        # Split data chronologically for time series
        split_idx = int(len(X) * 0.8)
        X_train, X_test = X[:split_idx], X[split_idx:]
        y_train, y_test = y[:split_idx], y[split_idx:]
        
        logger.info(f"Training set: {X_train.shape}, Test set: {X_test.shape}")
        logger.info(f"Home win rate in training: {y_train.mean():.1%}")
        logger.info(f"Home win rate in test: {y_test.mean():.1%}")
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Initialize models
        models_config = {
            'logistic_regression': LogisticRegression(random_state=42, max_iter=1000),
            'random_forest': RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
        }
        
        results = {}
        
        for name, model in models_config.items():
            logger.info(f"Training {name}...")
            
            try:
                if name == 'logistic_regression':
                    model.fit(X_train_scaled, y_train)
                    y_pred = model.predict(X_test_scaled)
                    y_pred_proba = model.predict_proba(X_test_scaled)[:, 1]
                else:
                    model.fit(X_train, y_train)
                    y_pred = model.predict(X_test)
                    y_pred_proba = model.predict_proba(X_test)[:, 1]
                
                # Calculate metrics
                accuracy = accuracy_score(y_test, y_pred)
                auc = roc_auc_score(y_test, y_pred_proba)
                logloss = log_loss(y_test, y_pred_proba)
                
                results[name] = {
                    'model': model,
                    'accuracy': accuracy,
                    'auc': auc,
                    'log_loss': logloss,
                    'predictions': y_pred,
                    'probabilities': y_pred_proba
                }
                
                logger.info(f"{name} - Accuracy: {accuracy:.4f}, AUC: {auc:.4f}, Log Loss: {logloss:.4f}")
                
                # Print classification report
                print(f"\n{name.upper()} Classification Report:")
                print(classification_report(y_test, y_pred, target_names=['Away Win', 'Home Win']))
                
                # Feature importance for Random Forest
                if name == 'random_forest' and hasattr(model, 'feature_importances_'):
                    feature_importance = pd.DataFrame({
                        'feature': self.feature_columns,
                        'importance': model.feature_importances_
                    }).sort_values('importance', ascending=False)
                    
                    print(f"\nTop 10 Most Important Features for {name.upper()}:")
                    print(feature_importance.head(10))
                
            except Exception as e:
                logger.error(f"Error training {name}: {e}")
        
        self.models = results
        self.is_fitted = True
        return results
    
    def predict_game(self, home_team_id: int, away_team_id: int, 
                    team_ratings: Dict[int, float]) -> Dict[str, float]:
        """Predict outcome for a specific game"""
        if not self.is_fitted:
            raise ValueError("Models must be trained first")
        
        # Create feature vector for prediction
        home_rating = team_ratings.get(home_team_id, 1500)
        away_rating = team_ratings.get(away_team_id, 1500)
        
        # Create basic features (must match training features)
        features = {
            'home_team_rating': home_rating,
            'away_team_rating': away_rating,
            'rating_difference': home_rating - away_rating,
            'home_advantage': 1,
            'rating_product': home_rating * away_rating,
            'rating_sum': home_rating + away_rating,
            'is_playoff': 0,  # Default to regular season
            'is_regular_season': 1,
            'attendance_normalized': 0.8  # Default attendance
        }
        
        # Create feature vector matching training features
        feature_vector = []
        for col in self.feature_columns:
            feature_vector.append(features.get(col, 0))
        
        feature_array = np.array(feature_vector).reshape(1, -1)
        
        # Get predictions from best model (Random Forest if available)
        if 'random_forest' in self.models:
            model = self.models['random_forest']['model']
            home_win_prob = model.predict_proba(feature_array)[0, 1]
        elif 'logistic_regression' in self.models:
            model = self.models['logistic_regression']['model']
            feature_array_scaled = self.scaler.transform(feature_array)
            home_win_prob = model.predict_proba(feature_array_scaled)[0, 1]
        else:
            return None
        
        return {
            'home_team_id': home_team_id,
            'away_team_id': away_team_id,
            'home_win_probability': home_win_prob,
            'away_win_probability': 1 - home_win_prob,
            'predicted_winner': home_team_id if home_win_prob > 0.5 else away_team_id,
            'confidence': max(home_win_prob, 1 - home_win_prob)
        }

def main():
    """Main execution function"""
    logger.info("Starting NBA Game Outcome Prediction Model (Fixed Version)")
    
    # Download dataset
    logger.info("Downloading NBA dataset from Kaggle...")
    try:
        path = kagglehub.dataset_download("eoinamoore/historical-nba-data-and-player-box-scores")
        logger.info(f"Dataset downloaded to: {path}")
    except Exception as e:
        logger.error(f"Error downloading dataset: {e}")
        logger.info("Please ensure you have Kaggle API configured")
        return
    
    # Load the Games dataset (most relevant for our task)
    games_file = os.path.join(path, "Games.csv")
    team_stats_file = os.path.join(path, "TeamStatistics.csv")
    
    if not os.path.exists(games_file):
        logger.error(f"Games.csv not found in {path}")
        return
    
    logger.info("Loading Games dataset...")
    games_df = pd.read_csv(games_file)
    logger.info(f"Loaded Games dataset: {games_df.shape}")
    
    logger.info("Loading Team Statistics dataset...")
    team_stats_df = pd.read_csv(team_stats_file) if os.path.exists(team_stats_file) else None
    if team_stats_df is not None:
        logger.info(f"Loaded Team Statistics dataset: {team_stats_df.shape}")
    
    # Data analysis and visualization
    print("\n" + "="*80)
    print("DATA ANALYSIS AND VISUALIZATION")
    print("="*80)
    analyzer = NBADataAnalyzer(games_df)
    analyzer.create_basic_visualizations()
    
    # Feature engineering
    logger.info("Starting feature engineering...")
    feature_engineer = NBAFeatureEngine(games_df)
    features_df = feature_engineer.engineer_features(team_stats_df)
    
    if features_df is None:
        logger.error("Feature engineering failed")
        return
    
    logger.info(f"Feature engineering completed. Dataset shape: {features_df.shape}")
    
    # Model training and evaluation
    logger.info("Training predictive models...")
    predictor = NBAPredictor()
    
    X, y = predictor.prepare_features(features_df)
    
    if X is None or y is None:
        logger.error("Failed to prepare features")
        return
    
    results = predictor.train_models(X, y)
    
    if not results:
        logger.error("Model training failed")
        return
    
    # Print results summary
    print("\n" + "="*80)
    print("MODEL PERFORMANCE SUMMARY")
    print("="*80)
    for name, result in results.items():
        print(f"{name:20} | Accuracy: {result['accuracy']:.4f} | AUC: {result['auc']:.4f} | Log Loss: {result['log_loss']:.4f}")
    
    # Example prediction
    if 'hometeamId' in features_df.columns and 'awayteamId' in features_df.columns:
        # Get a sample matchup
        sample_idx = features_df.dropna(subset=['hometeamId', 'awayteamId']).index[0]
        sample_game = features_df.loc[sample_idx]
        team_ratings = feature_engineer.calculate_team_strength(features_df)
        
        prediction = predictor.predict_game(
            sample_game['hometeamId'], 
            sample_game['awayteamId'], 
            team_ratings
        )
        
        if prediction:
            print("\n" + "="*80)
            print("SAMPLE PREDICTION")
            print("="*80)
            print(f"Home Team ID: {prediction['home_team_id']}")
            print(f"Away Team ID: {prediction['away_team_id']}")
            print(f"Predicted Winner: Team {prediction['predicted_winner']}")
            print(f"Confidence: {prediction['confidence']:.1%}")
            print(f"Home Win Probability: {prediction['home_win_probability']:.1%}")
            print(f"Away Win Probability: {prediction['away_win_probability']:.1%}")
    
    # Save feature importance and model metrics
    if 'random_forest' in results:
        feature_importance = pd.DataFrame({
            'feature': predictor.feature_columns,
            'importance': results['random_forest']['model'].feature_importances_
        }).sort_values('importance', ascending=False)
        
        # Create output directory
        os.makedirs('/Users/adamnouri/Downloads/first-website/ml-service/data/processed', exist_ok=True)
        feature_importance.to_csv(
            '/Users/adamnouri/Downloads/first-website/ml-service/data/processed/feature_importance.csv', 
            index=False
        )
        logger.info("Feature importance saved to feature_importance.csv")
    
    logger.info("NBA prediction model pipeline completed successfully!")

if __name__ == "__main__":
    main()