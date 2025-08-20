from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
import uuid

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

@app.route('/batch/generate-predictions', methods=['POST'])
def generate_batch_predictions():
    """Generate predictions for multiple matchups and store in S3"""
    try:
        data = request.get_json()
        matchups = data.get('matchups', [])
        
        if not matchups:
            return jsonify({"error": "No matchups provided"}), 400
        
        # Generate predictions with charts
        batch_results = []
        for matchup in matchups:
            try:
                prediction_uuid = str(uuid.uuid4())
                team1_id = matchup['team1_id']
                team2_id = matchup['team2_id']
                game_date = datetime.strptime(matchup.get('game_date', datetime.now().strftime('%Y-%m-%d')), '%Y-%m-%d').date()
                
                # Get prediction
                prediction_result = prediction_service.predict_game(team1_id, team2_id, game_date.strftime('%Y-%m-%d'))
                
                # Get team names
                teams_data = prediction_service._get_all_teams_from_api()
                team1_name = teams_data.get(team1_id, {}).get('fullName', f'Team {team1_id}')
                team2_name = teams_data.get(team2_id, {}).get('fullName', f'Team {team2_id}')
                
                # Generate chart image
                chart_image = chart_service.generate_prediction_chart_image(prediction_result, team1_name, team2_name)
                
                # Prepare S3 prediction data
                s3_prediction_data = {
                    "prediction_id": prediction_uuid,
                    "timestamp": datetime.now().isoformat(),
                    "matchup": {
                        "team1": {"id": team1_id, "name": team1_name},
                        "team2": {"id": team2_id, "name": team2_name}
                    },
                    "prediction": prediction_result,
                    "model_metadata": {
                        "model_version": "v2.0_enhanced",
                        "training_data_cutoff": datetime.now().strftime('%Y-%m-%d')
                    }
                }
                
                # Upload to S3
                success, pred_path, chart_path = s3_service.upload_prediction_with_chart(
                    prediction_uuid, game_date, s3_prediction_data, chart_image
                )
                
                batch_results.append({
                    "prediction_uuid": prediction_uuid,
                    "team1_id": team1_id,
                    "team2_id": team2_id,
                    "team1_name": team1_name,
                    "team2_name": team2_name,
                    "game_date": game_date.isoformat(),
                    "s3_success": success,
                    "prediction_path": pred_path,
                    "chart_path": chart_path,
                    "prediction": prediction_result
                })
                
            except Exception as e:
                logger.error(f"Failed to process matchup {matchup}: {e}")
                batch_results.append({
                    "error": str(e),
                    "matchup": matchup
                })
        
        return jsonify({
            "status": "completed",
            "total_matchups": len(matchups),
            "successful": sum(1 for r in batch_results if r.get('s3_success')),
            "failed": sum(1 for r in batch_results if 'error' in r),
            "results": batch_results,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Batch generation error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/batch/upcoming-games', methods=['POST'])  
def generate_upcoming_games_predictions():
    """Generate predictions for all upcoming games (next 7-14 days)"""
    try:
        days_ahead = request.json.get('days_ahead', 7) if request.is_json else 7
        
        # Mock upcoming games - in real implementation, fetch from NBA API
        upcoming_games = []
        teams_data = prediction_service._get_all_teams_from_api()
        team_ids = list(teams_data.keys())
        
        # Generate sample matchups for next week
        for day in range(1, days_ahead + 1):
            game_date = datetime.now() + timedelta(days=day)
            
            # Create 3-5 random matchups per day
            import random
            num_games = random.randint(3, 5)
            selected_teams = random.sample(team_ids, num_games * 2)
            
            for i in range(0, len(selected_teams), 2):
                upcoming_games.append({
                    "team1_id": selected_teams[i],
                    "team2_id": selected_teams[i + 1],
                    "game_date": game_date.strftime('%Y-%m-%d')
                })
        
        # Generate predictions for all upcoming games
        result = generate_batch_predictions()
        
        # Update the request data for the nested call
        request.json = {"matchups": upcoming_games}
        
        return jsonify({
            "message": f"Generated predictions for upcoming {days_ahead} days",
            "total_games": len(upcoming_games),
            "status": "processing",
            "note": "Check /batch/generate-predictions endpoint for detailed results"
        })
        
    except Exception as e:
        logger.error(f"Upcoming games generation error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/teams', methods=['GET'])
def get_teams():
    """Get all NBA teams for frontend dropdown"""
    try:
        teams_data = prediction_service._get_all_teams_from_api()
        
        # Convert to list format for frontend
        teams_list = []
        for nba_id, team_info in teams_data.items():
            teams_list.append({
                "nbaApiId": nba_id,
                "name": team_info["name"],
                "city": team_info["city"],
                "abbreviation": team_info["abbreviation"],
                "fullName": team_info["fullName"]
            })
        
        # Sort by full name for better UX
        teams_list.sort(key=lambda x: x["fullName"])
        
        return jsonify({
            "teams": teams_list,
            "count": len(teams_list),
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Teams error: {str(e)}")
        return jsonify({"error": "Failed to get teams"}), 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_ENV') == 'development'
    app.run(host='0.0.0.0', port=port, debug=debug)