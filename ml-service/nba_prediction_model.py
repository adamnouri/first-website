#!/usr/bin/env python3
"""
NBA Game Outcome Prediction Model
=================================

A comprehensive machine learning pipeline for predicting NBA game outcomes
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
import plotly.express as px
import plotly.graph_objects as go

from sklearn.model_selection import train_test_split, TimeSeriesSplit, cross_val_score
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, roc_auc_score, log_loss
import xgboost as xgb
import lightgbm as lgb
import shap

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
                self.datasets[df_name] = pd.read_csv(file_path)
                logger.info(f"Loaded {df_name}: {self.datasets[df_name].shape}")
                
        except Exception as e:
            logger.error(f"Error loading datasets: {e}")
            
    def explore_dataset_structure(self):
        """Explore the structure of each dataset"""
        for name, df in self.datasets.items():
            print(f"\n{'='*50}")
            print(f"Dataset: {name}")
            print(f"{'='*50}")
            print(f"Shape: {df.shape}")
            print(f"Columns: {list(df.columns)}")
            print("\nData Types:")
            print(df.dtypes)
            print("\nFirst few rows:")
            print(df.head())
            print("\nMissing values:")
            print(df.isnull().sum())
            
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
        
        print(f"\n{'='*50}")
        print("GAME-RELATED TABLES (sorted by relevance)")
        print(f"{'='*50}")
        for name, info in sorted_tables:
            print(f"{name}: Score={info['relevance_score']}, Shape={info['shape']}")
            
        return dict(sorted_tables)

class NBAFeatureEngine:
    """Class for feature engineering NBA data"""
    
    def __init__(self, games_df: pd.DataFrame, team_stats_df: Optional[pd.DataFrame] = None):
        self.games_df = games_df.copy()
        self.team_stats_df = team_stats_df.copy() if team_stats_df is not None else None
        self.features_df = None
        
    def create_rolling_averages(self, df: pd.DataFrame, team_col: str, 
                              stat_cols: List[str], windows: List[int] = [5, 10, 15]) -> pd.DataFrame:
        """Create rolling averages for team statistics"""
        df_sorted = df.sort_values(['date', team_col])
        
        for window in windows:
            for stat in stat_cols:
                if stat in df.columns:
                    df_sorted[f'{stat}_rolling_{window}'] = (
                        df_sorted.groupby(team_col)[stat]
                        .rolling(window, min_periods=1)
                        .mean()
                        .reset_index(0, drop=True)
                    )
        return df_sorted
    
    def calculate_team_strength(self, df: pd.DataFrame) -> Dict[str, float]:
        """Calculate Elo-like team strength ratings"""
        team_ratings = {}
        initial_rating = 1500
        k_factor = 32
        
        for team in df['home_team'].unique():
            if pd.notna(team):
                team_ratings[team] = initial_rating
        
        for team in df['away_team'].unique():
            if pd.notna(team) and team not in team_ratings:
                team_ratings[team] = initial_rating
        
        for _, game in df.iterrows():
            if pd.notna(game.get('home_score')) and pd.notna(game.get('away_score')):
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
        required_cols = ['date', 'home_team', 'away_team']
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            logger.error(f"Missing required columns: {missing_cols}")
            return None
            
        # Convert date column
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'])
            
        # Create target variable (1 if home team wins, 0 otherwise)
        if 'home_score' in df.columns and 'away_score' in df.columns:
            df['home_win'] = (df['home_score'] > df['away_score']).astype(int)
        
        # Calculate team strength ratings
        team_ratings = self.calculate_team_strength(df)
        df['home_team_rating'] = df['home_team'].map(team_ratings)
        df['away_team_rating'] = df['away_team'].map(team_ratings)
        df['rating_difference'] = df['home_team_rating'] - df['away_team_rating']
        
        # Add home advantage feature (generally teams win ~55% at home)
        df['home_advantage'] = 1
        
        # Create head-to-head features
        h2h_wins = {}
        for _, game in df.iterrows():
            key = f"{game['home_team']}_vs_{game['away_team']}"
            reverse_key = f"{game['away_team']}_vs_{game['home_team']}"
            
            if key not in h2h_wins:
                h2h_wins[key] = {'home_wins': 0, 'away_wins': 0, 'total_games': 0}
            if reverse_key not in h2h_wins:
                h2h_wins[reverse_key] = {'home_wins': 0, 'away_wins': 0, 'total_games': 0}
        
        # Calculate rest days (if we have date information)
        if 'date' in df.columns:
            df_sorted = df.sort_values('date')
            for team_col in ['home_team', 'away_team']:
                df_sorted[f'{team_col}_rest_days'] = (
                    df_sorted.groupby(team_col)['date'].diff().dt.days.fillna(5)
                )
            df = df_sorted
        
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
        exclude_cols = ['home_win', 'home_score', 'away_score', 'game_id']
        feature_cols = [col for col in numeric_cols if col not in exclude_cols]
        
        X = df[feature_cols].fillna(0)
        y = df['home_win'] if 'home_win' in df.columns else None
        
        self.feature_columns = feature_cols
        
        return X.values, y.values if y is not None else None
    
    def train_models(self, X: np.ndarray, y: np.ndarray):
        """Train multiple models for comparison"""
        # Split data chronologically for time series
        split_idx = int(len(X) * 0.8)
        X_train, X_test = X[:split_idx], X[split_idx:]
        y_train, y_test = y[:split_idx], y[split_idx:]
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Initialize models
        models_config = {
            'logistic_regression': LogisticRegression(random_state=42, max_iter=1000),
            'random_forest': RandomForestClassifier(n_estimators=100, random_state=42),
            'xgboost': xgb.XGBClassifier(random_state=42, eval_metric='logloss'),
            'lightgbm': lgb.LGBMClassifier(random_state=42, verbosity=-1)
        }
        
        results = {}
        
        for name, model in models_config.items():
            logger.info(f"Training {name}...")
            
            try:
                if name in ['logistic_regression']:
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
        features = np.array([
            team_ratings.get(home_team, 1500),
            team_ratings.get(away_team, 1500), 
            team_ratings.get(home_team, 1500) - team_ratings.get(away_team, 1500),
            1,  # home advantage
            5,  # default rest days
            5   # default rest days
        ] + [0] * (len(self.feature_columns) - 6)).reshape(1, -1)
        
        # Get predictions from best model (assuming XGBoost)
        if 'xgboost' in self.models:
            model = self.models['xgboost']['model']
            home_win_prob = model.predict_proba(features)[0, 1]
        else:
            # Fallback to first available model
            model = list(self.models.values())[0]['model']
            home_win_prob = model.predict_proba(features)[0, 1]
        
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
    logger.info("Starting NBA Game Outcome Prediction Model")
    
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
    
    # Explore dataset structure
    print("\n" + "="*60)
    print("NBA DATASET EXPLORATION")
    print("="*60)
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
    
    # Print results summary
    print("\n" + "="*60)
    print("MODEL PERFORMANCE SUMMARY")
    print("="*60)
    for name, result in results.items():
        print(f"{name:20} | Accuracy: {result['accuracy']:.4f} | AUC: {result['auc']:.4f} | Log Loss: {result['log_loss']:.4f}")
    
    # Example prediction
    if 'home_team' in features_df.columns and 'away_team' in features_df.columns:
        sample_teams = features_df[['home_team', 'away_team']].dropna().iloc[0]
        team_ratings = feature_engineer.calculate_team_strength(features_df)
        
        prediction = predictor.predict_game(
            sample_teams['home_team'], 
            sample_teams['away_team'], 
            team_ratings
        )
        
        print("\n" + "="*60)
        print("SAMPLE PREDICTION")
        print("="*60)
        print(f"Matchup: {prediction['home_team']} vs {prediction['away_team']}")
        print(f"Predicted Winner: {prediction['predicted_winner']}")
        print(f"Confidence: {prediction['confidence']:.1%}")
        print(f"Home Win Probability: {prediction['home_win_probability']:.1%}")
    
    logger.info("NBA prediction model pipeline completed successfully!")

if __name__ == "__main__":
    main()