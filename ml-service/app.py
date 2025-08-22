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
from services.playoff_predictor import PlayoffPredictor
from services.championship_calculator import ChampionshipCalculator
from services.background_processor import initialize_background_processor
from services.s3_prediction_storage import S3PredictionStorage

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
s3_storage = S3PredictionStorage(s3_service)
playoff_predictor = PlayoffPredictor(prediction_service, s3_service)
championship_calculator = ChampionshipCalculator(prediction_service, playoff_predictor, s3_service)

# Initialize background processing
background_processor = initialize_background_processor(prediction_service, s3_service)

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "timestamp": datetime.now().isoformat()})

@app.route('/storage/status', methods=['GET'])
def storage_status():
    """Get S3 storage and background processing status"""
    try:
        storage_stats = s3_storage.get_storage_stats()
        processing_status = background_processor.get_processing_status()
        
        return jsonify({
            "storage": storage_stats,
            "background_processing": processing_status,
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Storage status error: {e}")
        return jsonify({"error": "Failed to get storage status"}), 500

@app.route('/storage/cleanup', methods=['POST'])
def cleanup_storage():
    """Clean up expired predictions from S3"""
    try:
        deleted_count = s3_storage.cleanup_expired_predictions()
        
        return jsonify({
            "message": "Storage cleanup completed",
            "deleted_predictions": deleted_count,
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Storage cleanup error: {e}")
        return jsonify({"error": "Failed to cleanup storage"}), 500

@app.route('/storage/list', methods=['GET'])
def list_stored_predictions():
    """List stored predictions in S3"""
    try:
        operation = request.args.get('operation')
        limit = int(request.args.get('limit', 100))
        
        predictions = s3_storage.list_stored_predictions(operation, limit)
        
        return jsonify({
            "predictions": predictions,
            "count": len(predictions),
            "operation_filter": operation,
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"List predictions error: {e}")
        return jsonify({"error": "Failed to list predictions"}), 500

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

# ============================================================================
# PLAYOFF PREDICTION ENDPOINTS
# ============================================================================

@app.route('/playoffs/conference-standings', methods=['GET'])
def get_conference_standings():
    """Generate predicted conference standings"""
    try:
        conference = request.args.get('conference', 'both').lower()
        simulations = int(request.args.get('simulations', 1000))
        
        standings = playoff_predictor.simulate_season_standings(simulations)
        
        if conference == 'eastern':
            result = {'Eastern': standings['Eastern']}
        elif conference == 'western':
            result = {'Western': standings['Western']}
        else:
            result = standings
        
        return jsonify({
            "standings": result,
            "simulations": simulations,
            "generated_at": datetime.now().isoformat(),
            "status": "success"
        })
        
    except Exception as e:
        logger.error(f"Conference standings error: {str(e)}")
        return jsonify({"error": "Failed to generate conference standings"}), 500

@app.route('/playoffs/bracket', methods=['GET'])
def generate_playoff_bracket():
    """Generate complete playoff bracket"""
    try:
        # Check if we should use existing standings or generate new ones
        use_cached = request.args.get('use_cached', 'false').lower() == 'true'
        
        if use_cached:
            # For demo purposes, generate new bracket each time
            # In production, you might cache this
            bracket = playoff_predictor.generate_playoff_bracket()
        else:
            bracket = playoff_predictor.generate_playoff_bracket()
        
        return jsonify({
            "bracket": bracket,
            "status": "success",
            "note": "Complete playoff bracket with predictions"
        })
        
    except Exception as e:
        logger.error(f"Playoff bracket error: {str(e)}")
        return jsonify({"error": "Failed to generate playoff bracket"}), 500

@app.route('/playoffs/championship-odds', methods=['GET'])
def get_championship_odds():
    """Calculate comprehensive championship odds"""
    try:
        simulations = int(request.args.get('simulations', 5000))
        
        odds = championship_calculator.calculate_comprehensive_odds(simulations=simulations)
        
        return jsonify({
            "odds": odds,
            "status": "success"
        })
        
    except Exception as e:
        logger.error(f"Championship odds error: {str(e)}")
        return jsonify({"error": "Failed to calculate championship odds"}), 500

@app.route('/playoffs/series-prediction', methods=['POST'])
def predict_playoff_series():
    """Predict a specific playoff series"""
    try:
        data = request.get_json()
        
        if 'team1_id' not in data or 'team2_id' not in data:
            return jsonify({"error": "Missing team IDs"}), 400
        
        team1_id = data['team1_id']
        team2_id = data['team2_id']
        round_name = data.get('round', 'first_round')
        series_length = int(data.get('series_length', 7))
        
        # Create basic team info for prediction
        team1_info = {
            'team_id': team1_id,
            'team_name': prediction_service._get_team_name_from_api(team1_id),
            'team_abbreviation': prediction_service._get_team_abbreviation_from_api(team1_id),
            'rank': 1  # Default rank
        }
        
        team2_info = {
            'team_id': team2_id,
            'team_name': prediction_service._get_team_name_from_api(team2_id),
            'team_abbreviation': prediction_service._get_team_abbreviation_from_api(team2_id),
            'rank': 2  # Default rank
        }
        
        series_prediction = playoff_predictor._predict_series(team1_info, team2_info, series_length)
        
        # Add game-by-game breakdown
        game_predictions = []
        for game_num in range(1, series_prediction.get('predicted_games', 7) + 1):
            game_pred = prediction_service.predict_game(team1_id, team2_id, 'playoff')
            game_predictions.append({
                'game': game_num,
                'home_team': team1_info if game_num % 2 == 1 else team2_info,
                'away_team': team2_info if game_num % 2 == 1 else team1_info,
                'prediction': {
                    'winner_probability': game_pred.get('home_win_probability', 0.5),
                    'predicted_score_home': game_pred.get('team1_predicted_score', 108),
                    'predicted_score_away': game_pred.get('team2_predicted_score', 105)
                }
            })
        
        return jsonify({
            "series_prediction": series_prediction,
            "game_breakdown": game_predictions,
            "round": round_name,
            "series_length": series_length,
            "generated_at": datetime.now().isoformat(),
            "status": "success"
        })
        
    except Exception as e:
        logger.error(f"Series prediction error: {str(e)}")
        return jsonify({"error": "Failed to predict series"}), 500

@app.route('/playoffs/simulate-tournament', methods=['POST'])
def simulate_full_tournament():
    """Simulate complete playoff tournament"""
    try:
        data = request.get_json() or {}
        simulations = int(data.get('simulations', 1000))
        include_play_in = data.get('include_play_in', True)
        
        # Generate standings if not provided
        standings = data.get('standings')
        if not standings:
            standings = playoff_predictor.simulate_season_standings()
        
        # Run tournament simulation
        tournament_results = []
        champion_counts = {}
        
        for _ in range(simulations):
            bracket = playoff_predictor.generate_playoff_bracket(standings)
            
            # For demo, just track most likely champions from championship odds
            for team_odds in bracket.get('championship_odds', []):
                team_name = team_odds.get('team_name', 'Unknown')
                champion_counts[team_name] = champion_counts.get(team_name, 0) + team_odds.get('championship_odds', 0)
        
        # Convert to probabilities
        total_probability = sum(champion_counts.values())
        if total_probability > 0:
            for team in champion_counts:
                champion_counts[team] = champion_counts[team] / total_probability
        
        # Sort by probability
        sorted_champions = sorted(champion_counts.items(), key=lambda x: x[1], reverse=True)
        
        return jsonify({
            "tournament_simulation": {
                "simulations_run": simulations,
                "champion_probabilities": [
                    {"team": team, "probability": round(prob, 4)}
                    for team, prob in sorted_champions[:10]  # Top 10
                ],
                "most_likely_champion": sorted_champions[0] if sorted_champions else None,
                "bracket_used": standings is not None
            },
            "generated_at": datetime.now().isoformat(),
            "status": "success"
        })
        
    except Exception as e:
        logger.error(f"Tournament simulation error: {str(e)}")
        return jsonify({"error": "Failed to simulate tournament"}), 500

@app.route('/playoffs/team-odds/<int:team_id>', methods=['GET'])
def get_team_playoff_odds(team_id):
    """Get detailed playoff odds for a specific team"""
    try:
        # Get comprehensive odds
        odds = championship_calculator.calculate_comprehensive_odds()
        
        # Find team in results
        team_odds = None
        for team_data in odds.get('championship_odds', []):
            if team_data.get('team_id') == team_id:
                team_odds = team_data
                break
        
        if not team_odds:
            return jsonify({"error": "Team not found in odds calculation"}), 404
        
        # Get round probabilities
        round_probs = odds.get('round_probabilities', {}).get(str(team_id), {})
        
        return jsonify({
            "team_odds": team_odds,
            "round_probabilities": round_probs,
            "team_id": team_id,
            "calculated_at": odds.get('last_updated'),
            "status": "success"
        })
        
    except Exception as e:
        logger.error(f"Team odds error: {str(e)}")
        return jsonify({"error": "Failed to get team odds"}), 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_ENV') == 'development'
    app.run(host='0.0.0.0', port=port, debug=debug)