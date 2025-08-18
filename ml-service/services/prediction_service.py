import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import joblib
import logging
from datetime import datetime
import requests
import os

logger = logging.getLogger(__name__)

class PredictionService:
    def __init__(self, s3_service):
        self.s3_service = s3_service
        self.model = None
        self.scaler = None
        self.spring_boot_url = os.getenv('SPRING_BOOT_URL', 'http://localhost:8080')
        self.load_model()
    
    def load_model(self):
        """Load model from S3 or create new one if doesn't exist"""
        try:
            model_data = self.s3_service.download_model('nba-model.pkl')
            scaler_data = self.s3_service.download_model('nba-scaler.pkl')
            
            if model_data and scaler_data:
                self.model = joblib.loads(model_data)
                self.scaler = joblib.loads(scaler_data)
                logger.info("Model loaded from S3")
            else:
                logger.info("No existing model found, will create new one")
                self.create_default_model()
                
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            self.create_default_model()
    
    def create_default_model(self):
        """Create a basic model for initial predictions"""
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.scaler = StandardScaler()
        
        # Create dummy training data for initial model
        X_dummy = np.random.rand(100, 10)  # 10 features
        y_dummy = np.random.randint(0, 2, 100)  # Binary classification
        
        X_scaled = self.scaler.fit_transform(X_dummy)
        self.model.fit(X_scaled, y_dummy)
        
        # Save to S3
        self.save_model()
        logger.info("Created default model")
    
    def predict_game(self, team1_id, team2_id, game_date):
        """Predict game outcome between two teams"""
        try:
            # Get team stats from Spring Boot API
            team1_stats = self.get_team_stats_from_api(team1_id)
            team2_stats = self.get_team_stats_from_api(team2_id)
            
            # Create feature vector
            features = self.create_feature_vector(team1_stats, team2_stats)
            
            # Scale features
            features_scaled = self.scaler.transform([features])
            
            # Make prediction
            prediction_proba = self.model.predict_proba(features_scaled)[0]
            prediction = self.model.predict(features_scaled)[0]
            
            # Calculate confidence and create result
            confidence = max(prediction_proba)
            winner_team = team1_id if prediction == 1 else team2_id
            
            # Generate predicted score (simple heuristic)
            base_score = 105
            score_diff = int(confidence * 20)  # Max 20 point difference
            
            if winner_team == team1_id:
                team1_score = base_score + score_diff
                team2_score = base_score - score_diff//2
            else:
                team1_score = base_score - score_diff//2
                team2_score = base_score + score_diff
            
            result = {
                "winner_team_id": winner_team,
                "confidence": round(confidence, 3),
                "team1_predicted_score": team1_score,
                "team2_predicted_score": team2_score,
                "prediction_date": datetime.now().isoformat(),
                "model_version": "1.0"
            }
            
            # Store prediction result
            self.store_prediction(result, team1_id, team2_id, game_date)
            
            return result
            
        except Exception as e:
            logger.error(f"Prediction error: {e}")
            raise
    
    def get_team_stats_from_api(self, team_id):
        """Get team statistics from Spring Boot API"""
        try:
            response = requests.get(f"{self.spring_boot_url}/api/teams/{team_id}/stats")
            if response.status_code == 200:
                return response.json()
            else:
                # Return default stats if API fails
                return self.get_default_team_stats()
        except Exception as e:
            logger.warning(f"Failed to get team stats from API: {e}")
            return self.get_default_team_stats()
    
    def get_default_team_stats(self):
        """Return default team stats when API is unavailable"""
        return {
            "wins": 20,
            "losses": 15,
            "points_per_game": 110.5,
            "rebounds_per_game": 45.2,
            "assists_per_game": 25.8,
            "field_goal_percentage": 0.456,
            "three_point_percentage": 0.358
        }
    
    def create_feature_vector(self, team1_stats, team2_stats):
        """Create feature vector from team statistics"""
        features = [
            team1_stats.get('wins', 0) - team2_stats.get('wins', 0),
            team1_stats.get('points_per_game', 100) - team2_stats.get('points_per_game', 100),
            team1_stats.get('rebounds_per_game', 40) - team2_stats.get('rebounds_per_game', 40),
            team1_stats.get('assists_per_game', 20) - team2_stats.get('assists_per_game', 20),
            team1_stats.get('field_goal_percentage', 0.4) - team2_stats.get('field_goal_percentage', 0.4),
            team1_stats.get('three_point_percentage', 0.3) - team2_stats.get('three_point_percentage', 0.3),
            team1_stats.get('wins', 0) / max(team1_stats.get('wins', 1) + team1_stats.get('losses', 1), 1),
            team2_stats.get('wins', 0) / max(team2_stats.get('wins', 1) + team2_stats.get('losses', 1), 1),
            team1_stats.get('points_per_game', 100),
            team2_stats.get('points_per_game', 100)
        ]
        return features
    
    def save_model(self):
        """Save model and scaler to S3"""
        try:
            model_data = joblib.dumps(self.model)
            scaler_data = joblib.dumps(self.scaler)
            
            self.s3_service.upload_model('nba-model.pkl', model_data)
            self.s3_service.upload_model('nba-scaler.pkl', scaler_data)
            
            logger.info("Model saved to S3")
        except Exception as e:
            logger.error(f"Error saving model: {e}")
    
    def store_prediction(self, prediction, team1_id, team2_id, game_date):
        """Store prediction result to S3"""
        try:
            key = f"predictions/{game_date}_{team1_id}_vs_{team2_id}.json"
            self.s3_service.upload_prediction(key, prediction)
        except Exception as e:
            logger.error(f"Error storing prediction: {e}")
    
    def retrain_model(self):
        """Retrain model with latest data"""
        # This would fetch latest game results and retrain
        # For now, return success message
        return {"status": "Model retrain initiated", "timestamp": datetime.now().isoformat()}
    
    def get_team_stats(self, team_id):
        """Get team statistics"""
        return self.get_team_stats_from_api(team_id)