#!/usr/bin/env python3
"""
NBA Game Outcome Prediction Model - Simplified Version
=====================================================

A simplified machine learning pipeline for predicting NBA game outcomes
using historical data from Kaggle.

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

class NBADataExplorer:
    """Class for exploring and understanding NBA dataset structure"""
    
    def __init__(self, data_path: str):
        self.data_path = data_path
        self.datasets = {}
        
    def load_datasets(self):
        """Load all CSV files from the dataset directory"""
        try:
            csv_files = [f for f in os.listdir(self.data_path) if f.endswith('.csv')]
            logger.info(f"Found {len(csv_files)} CSV files: {csv_files}")
            
            for file in csv_files:
                file_path = os.path.join(self.data_path, file)
                df_name = file.replace('.csv', '')
                try:
                    self.datasets[df_name] = pd.read_csv(file_path)
                    logger.info(f"Loaded {df_name}: {self.datasets[df_name].shape}")
                except Exception as e:
                    logger.warning(f"Failed to load {file}: {e}")
                    
        except Exception as e:
            logger.error(f"Error loading datasets: {e}")
            
    def explore_dataset_structure(self):
        """Explore the structure of each dataset"""
        for name, df in self.datasets.items():
            print(f"\n{'='*80}")
            print(f"Dataset: {name}")
            print(f"{'='*80}")
            print(f"Shape: {df.shape}")
            print(f"Columns ({len(df.columns)}): {list(df.columns)}")
            print("\nData Types:")
            print(df.dtypes)
            print("\nFirst few rows:")
            print(df.head())
            print("\nMissing values:")
            missing = df.isnull().sum()
            if missing.any():
                print(missing[missing > 0])
            else:
                print("No missing values")
            
    def identify_game_tables(self):
        """Identify tables relevant for game outcome prediction"""
        game_related_keywords = ['game', 'match', 'result', 'score', 'team', 'stat']
        
        game_tables = {}
        for name, df in self.datasets.items():
            # Check if table name or columns suggest game-related data
            name_lower = name.lower()
            columns_lower = [col.lower() for col in df.columns]
            
            relevance_score = 0
            for keyword in game_related_keywords:
                if keyword in name_lower:
                    relevance_score += 2
                relevance_score += sum(1 for col in columns_lower if keyword in col)
            
            if relevance_score > 0:
                game_tables[name] = {
                    'dataframe': df,
                    'relevance_score': relevance_score,
                    'shape': df.shape
                }
                
        # Sort by relevance
        sorted_tables = sorted(game_tables.items(), key=lambda x: x[1]['relevance_score'], reverse=True)
        
        print(f"\n{'='*80}")
        print("GAME-RELATED TABLES (sorted by relevance)")
        print(f"{'='*80}")
        for name, info in sorted_tables:
            print(f"{name}: Relevance Score={info['relevance_score']}, Shape={info['shape']}")
            
        return dict(sorted_tables)

class NBADataAnalyzer:
    """Class for analyzing NBA data and creating visualizations"""
    
    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()
        
    def create_basic_visualizations(self):
        """Create basic visualizations for data understanding"""
        plt.style.use('seaborn-v0_8')
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('NBA Dataset Analysis', fontsize=16, fontweight='bold')
        
        # 1. Home vs Away wins distribution
        if 'home_score' in self.df.columns and 'away_score' in self.df.columns:
            self.df['home_win'] = (self.df['home_score'] > self.df['away_score']).astype(int)
            home_wins = self.df['home_win'].value_counts()
            
            axes[0,0].pie(home_wins.values, labels=['Away Win', 'Home Win'], autopct='%1.1f%%', 
                         colors=['lightcoral', 'lightblue'])
            axes[0,0].set_title('Home vs Away Win Distribution')
        
        # 2. Score distribution
        if 'home_score' in self.df.columns and 'away_score' in self.df.columns:
            axes[0,1].hist(self.df['home_score'].dropna(), bins=30, alpha=0.7, label='Home Score', color='blue')
            axes[0,1].hist(self.df['away_score'].dropna(), bins=30, alpha=0.7, label='Away Score', color='red')
            axes[0,1].set_xlabel('Score')
            axes[0,1].set_ylabel('Frequency')
            axes[0,1].set_title('Score Distribution')
            axes[0,1].legend()
        
        # 3. Games per season (if season data available)
        season_cols = [col for col in self.df.columns if 'season' in col.lower() or 'year' in col.lower()]
        if season_cols:
            season_col = season_cols[0]
            games_per_season = self.df.groupby(season_col).size()
            axes[1,0].bar(games_per_season.index, games_per_season.values)
            axes[1,0].set_xlabel('Season')
            axes[1,0].set_ylabel('Number of Games')
            axes[1,0].set_title('Games per Season')
            axes[1,0].tick_params(axis='x', rotation=45)
        
        # 4. Missing data heatmap
        if self.df.isnull().sum().sum() > 0:
            missing_data = self.df.isnull().sum()
            missing_data = missing_data[missing_data > 0]
            if not missing_data.empty:
                axes[1,1].bar(range(len(missing_data)), missing_data.values)
                axes[1,1].set_xticks(range(len(missing_data)))
                axes[1,1].set_xticklabels(missing_data.index, rotation=45)
                axes[1,1].set_ylabel('Missing Values Count')
                axes[1,1].set_title('Missing Data by Column')
        
        plt.tight_layout()
        plt.savefig('/Users/adamnouri/Downloads/first-website/ml-service/data/processed/nba_analysis.png', 
                   dpi=300, bbox_inches='tight')
        plt.show()
        
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
        if 'home_team' in df.columns:
            all_teams.update(df['home_team'].dropna().unique())
        if 'away_team' in df.columns:
            all_teams.update(df['away_team'].dropna().unique())
        
        # Initialize ratings
        for team in all_teams:
            team_ratings[team] = initial_rating
        
        # Calculate ratings game by game
        for _, game in df.iterrows():
            if (pd.notna(game.get('home_score')) and pd.notna(game.get('away_score')) and
                pd.notna(game.get('home_team')) and pd.notna(game.get('away_team'))):
                
                home_team = game['home_team']
                away_team = game['away_team']
                
                if home_team in team_ratings and away_team in team_ratings:
                    home_rating = team_ratings[home_team]
                    away_rating = team_ratings[away_team]
                    
                    expected_home = 1 / (1 + 10**((away_rating - home_rating) / 400))
                    
                    actual_home = 1 if game['home_score'] > game['away_score'] else 0
                    
                    new_home_rating = home_rating + k_factor * (actual_home - expected_home)
                    new_away_rating = away_rating + k_factor * ((1 - actual_home) - (1 - expected_home))
                    
                    team_ratings[home_team] = new_home_rating
                    team_ratings[away_team] = new_away_rating
        
        return team_ratings
    
    def engineer_features(self) -> pd.DataFrame:
        """Main feature engineering pipeline"""
        df = self.games_df.copy()
        
        # Ensure we have required columns
        required_cols = ['home_team', 'away_team']
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            logger.error(f"Missing required columns: {missing_cols}")
            return None
            
        # Create target variable (1 if home team wins, 0 otherwise)
        if 'home_score' in df.columns and 'away_score' in df.columns:
            df['home_win'] = (df['home_score'] > df['away_score']).astype(int)
            df['score_difference'] = df['home_score'] - df['away_score']
            df['total_score'] = df['home_score'] + df['away_score']
        
        # Calculate team strength ratings
        team_ratings = self.calculate_team_strength(df)
        df['home_team_rating'] = df['home_team'].map(team_ratings)
        df['away_team_rating'] = df['away_team'].map(team_ratings)
        df['rating_difference'] = df['home_team_rating'] - df['away_team_rating']
        
        # Add home advantage feature
        df['home_advantage'] = 1
        
        # Convert categorical variables to numeric if needed
        label_encoder = LabelEncoder()
        
        # Encode team names
        if 'home_team' in df.columns:
            df['home_team_encoded'] = label_encoder.fit_transform(df['home_team'].fillna('Unknown'))
        if 'away_team' in df.columns:
            df['away_team_encoded'] = label_encoder.fit_transform(df['away_team'].fillna('Unknown'))
        
        # Create interaction features
        if 'home_team_rating' in df.columns and 'away_team_rating' in df.columns:
            df['rating_product'] = df['home_team_rating'] * df['away_team_rating']
            df['rating_sum'] = df['home_team_rating'] + df['away_team_rating']
        
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
        exclude_cols = ['home_win', 'home_score', 'away_score', 'score_difference', 'total_score']
        feature_cols = [col for col in numeric_cols if col not in exclude_cols and not col.endswith('_id')]
        
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
                
            except Exception as e:
                logger.error(f"Error training {name}: {e}")
        
        self.models = results
        self.is_fitted = True
        return results
    
    def predict_game(self, home_team: str, away_team: str, 
                    team_ratings: Dict[str, float]) -> Dict[str, float]:
        """Predict outcome for a specific game"""
        if not self.is_fitted:
            raise ValueError("Models must be trained first")
        
        # Create feature vector for prediction
        home_rating = team_ratings.get(home_team, 1500)
        away_rating = team_ratings.get(away_team, 1500)
        
        # Create basic features
        features = {
            'home_team_rating': home_rating,
            'away_team_rating': away_rating,
            'rating_difference': home_rating - away_rating,
            'home_advantage': 1,
            'home_team_encoded': 0,  # Would need proper encoding
            'away_team_encoded': 1,  # Would need proper encoding
            'rating_product': home_rating * away_rating,
            'rating_sum': home_rating + away_rating
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
            'home_team': home_team,
            'away_team': away_team,
            'home_win_probability': home_win_prob,
            'away_win_probability': 1 - home_win_prob,
            'predicted_winner': home_team if home_win_prob > 0.5 else away_team,
            'confidence': max(home_win_prob, 1 - home_win_prob)
        }

def main():
    """Main execution function"""
    logger.info("Starting NBA Game Outcome Prediction Model (Simplified Version)")
    
    # Download dataset
    logger.info("Downloading NBA dataset from Kaggle...")
    try:
        path = kagglehub.dataset_download("eoinamoore/historical-nba-data-and-player-box-scores")
        logger.info(f"Dataset downloaded to: {path}")
    except Exception as e:
        logger.error(f"Error downloading dataset: {e}")
        logger.info("Please ensure you have Kaggle API configured")
        return
    
    # Initialize data explorer
    explorer = NBADataExplorer(path)
    explorer.load_datasets()
    
    if not explorer.datasets:
        logger.error("No datasets loaded successfully")
        return
    
    # Explore dataset structure
    print("\n" + "="*80)
    print("NBA DATASET EXPLORATION")
    print("="*80)
    explorer.explore_dataset_structure()
    
    # Identify game-related tables
    game_tables = explorer.identify_game_tables()
    
    if not game_tables:
        logger.error("No game-related tables found in dataset")
        return
    
    # Use the most relevant table for modeling
    primary_table_name = list(game_tables.keys())[0]
    games_df = game_tables[primary_table_name]['dataframe']
    
    logger.info(f"Using '{primary_table_name}' as primary games dataset")
    
    # Data analysis and visualization
    analyzer = NBADataAnalyzer(games_df)
    analyzer.create_basic_visualizations()
    
    # Feature engineering
    logger.info("Starting feature engineering...")
    feature_engineer = NBAFeatureEngine(games_df)
    features_df = feature_engineer.engineer_features()
    
    if features_df is None:
        logger.error("Feature engineering failed")
        return
    
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
    if 'home_team' in features_df.columns and 'away_team' in features_df.columns:
        # Get a sample matchup
        sample_idx = features_df.dropna(subset=['home_team', 'away_team']).index[0]
        sample_game = features_df.loc[sample_idx]
        team_ratings = feature_engineer.calculate_team_strength(features_df)
        
        prediction = predictor.predict_game(
            sample_game['home_team'], 
            sample_game['away_team'], 
            team_ratings
        )
        
        if prediction:
            print("\n" + "="*80)
            print("SAMPLE PREDICTION")
            print("="*80)
            print(f"Matchup: {prediction['home_team']} vs {prediction['away_team']}")
            print(f"Predicted Winner: {prediction['predicted_winner']}")
            print(f"Confidence: {prediction['confidence']:.1%}")
            print(f"Home Win Probability: {prediction['home_win_probability']:.1%}")
            print(f"Away Win Probability: {prediction['away_win_probability']:.1%}")
    
    logger.info("NBA prediction model pipeline completed successfully!")

if __name__ == "__main__":
    main()