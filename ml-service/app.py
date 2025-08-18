from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv
import pandas as pd
import numpy as np
from datetime import datetime
import logging

# Import our services
from services.enhanced_prediction_service import EnhancedNBAPredictionService as PredictionService
from services.s3_service import S3Service
from services.chart_service import ChartService

load_dotenv()

app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize services
s3_service = S3Service()
prediction_service = PredictionService(s3_service)
chart_service = ChartService()

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "timestamp": datetime.now().isoformat()})

@app.route('/predict', methods=['POST'])
def predict_game():
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['team1_id', 'team2_id']
        if not all(field in data for field in required_fields):
            return jsonify({"error": "Missing required fields: team1_id, team2_id"}), 400
        
        team1_id = data['team1_id']
        team2_id = data['team2_id']
        game_date = data.get('game_date', datetime.now().strftime('%Y-%m-%d'))
        
        # Get prediction from service
        prediction_result = prediction_service.predict_game(team1_id, team2_id, game_date)
        
        # Generate chart data
        chart_data = chart_service.generate_chart_data(prediction_result, team1_id, team2_id)
        
        response = {
            "prediction": prediction_result,
            "chart_data": chart_data,
            "timestamp": datetime.now().isoformat()
        }
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Prediction error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/model/retrain', methods=['POST'])
def retrain_model():
    try:
        result = prediction_service.retrain_model()
        return jsonify(result)
    except Exception as e:
        logger.error(f"Retrain error: {str(e)}")
        return jsonify({"error": "Failed to retrain model"}), 500

@app.route('/teams/<int:team_id>/stats', methods=['GET'])
def get_team_stats(team_id):
    try:
        stats = prediction_service.get_team_stats(team_id)
        return jsonify(stats)
    except Exception as e:
        logger.error(f"Team stats error: {str(e)}")
        return jsonify({"error": "Failed to get team stats"}), 500

@app.route('/model/info', methods=['GET'])
def get_model_info():
    """Get information about the current ML models"""
    try:
        model_info = {
            "is_trained": prediction_service.is_trained,
            "models_available": list(prediction_service.models.keys()),
            "feature_count": len(prediction_service.feature_columns),
            "team_ratings_count": len(prediction_service.team_ratings),
            "last_updated": datetime.now().isoformat(),
            "model_version": "2.0_enhanced"
        }
        return jsonify(model_info)
    except Exception as e:
        logger.error(f"Model info error: {str(e)}")
        return jsonify({"error": "Failed to get model info"}), 500

@app.route('/teams/rankings', methods=['GET'])
def get_team_rankings():
    """Get team rankings based on ML ratings"""
    try:
        if not prediction_service.team_ratings:
            return jsonify({"error": "Team ratings not available"}), 404
        
        # Sort teams by rating
        sorted_teams = sorted(
            prediction_service.team_ratings.items(), 
            key=lambda x: x[1], 
            reverse=True
        )
        
        rankings = [
            {
                "rank": i + 1,
                "team_id": team_id,
                "rating": round(rating, 1)
            }
            for i, (team_id, rating) in enumerate(sorted_teams)
        ]
        
        return jsonify({
            "rankings": rankings,
            "last_updated": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Rankings error: {str(e)}")
        return jsonify({"error": "Failed to get team rankings"}), 500

@app.route('/predict/batch', methods=['POST'])
def predict_batch():
    """Predict multiple games at once"""
    try:
        data = request.get_json()
        
        if 'games' not in data:
            return jsonify({"error": "Missing 'games' field"}), 400
        
        results = []
        for game in data['games']:
            if 'team1_id' not in game or 'team2_id' not in game:
                results.append({"error": "Missing team IDs"})
                continue
                
            try:
                prediction = prediction_service.predict_game(
                    game['team1_id'], 
                    game['team2_id'], 
                    game.get('game_date')
                )
                results.append(prediction)
            except Exception as e:
                results.append({"error": str(e)})
        
        return jsonify({
            "predictions": results,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Batch prediction error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_ENV') == 'development'
    app.run(host='0.0.0.0', port=port, debug=debug)