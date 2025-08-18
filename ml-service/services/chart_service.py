import logging
from datetime import datetime, timedelta
import random

logger = logging.getLogger(__name__)

class ChartService:
    def __init__(self):
        pass
    
    def generate_chart_data(self, prediction_result, team1_id, team2_id):
        """Generate chart data for frontend visualization"""
        try:
            chart_data = {
                "confidence_chart": self.generate_confidence_chart(prediction_result),
                "score_comparison": self.generate_score_comparison(prediction_result, team1_id, team2_id),
                "team_comparison": self.generate_team_comparison(team1_id, team2_id),
                "trend_analysis": self.generate_trend_analysis(team1_id, team2_id),
                "win_probability": self.generate_win_probability_chart(prediction_result)
            }
            return chart_data
        except Exception as e:
            logger.error(f"Error generating chart data: {e}")
            return self.get_default_chart_data()
    
    def generate_confidence_chart(self, prediction_result):
        """Generate confidence level visualization data"""
        confidence = prediction_result.get('confidence', 0.5)
        
        return {
            "type": "gauge",
            "data": {
                "value": round(confidence * 100, 1),
                "min": 0,
                "max": 100,
                "title": "Prediction Confidence",
                "color": self.get_confidence_color(confidence)
            }
        }
    
    def generate_score_comparison(self, prediction_result, team1_id, team2_id):
        """Generate predicted score comparison chart"""
        team1_score = prediction_result.get('team1_predicted_score', 105)
        team2_score = prediction_result.get('team2_predicted_score', 105)
        
        return {
            "type": "bar",
            "data": {
                "labels": [f"Team {team1_id}", f"Team {team2_id}"],
                "datasets": [{
                    "label": "Predicted Score",
                    "data": [team1_score, team2_score],
                    "backgroundColor": ["#3B82F6", "#EF4444"],
                    "borderColor": ["#1D4ED8", "#DC2626"],
                    "borderWidth": 2
                }]
            },
            "options": {
                "responsive": True,
                "plugins": {
                    "title": {
                        "display": True,
                        "text": "Predicted Final Score"
                    }
                },
                "scales": {
                    "y": {
                        "beginAtZero": True,
                        "max": 140
                    }
                }
            }
        }
    
    def generate_team_comparison(self, team1_id, team2_id):
        """Generate team statistics comparison radar chart"""
        # Mock data - in real implementation, fetch from database
        team1_stats = self.get_mock_team_stats(team1_id)
        team2_stats = self.get_mock_team_stats(team2_id)
        
        return {
            "type": "radar",
            "data": {
                "labels": ["Offense", "Defense", "Rebounding", "3-Point", "Free Throws", "Turnovers"],
                "datasets": [
                    {
                        "label": f"Team {team1_id}",
                        "data": [
                            team1_stats['offense'],
                            team1_stats['defense'], 
                            team1_stats['rebounding'],
                            team1_stats['three_point'],
                            team1_stats['free_throws'],
                            team1_stats['turnovers']
                        ],
                        "backgroundColor": "rgba(59, 130, 246, 0.2)",
                        "borderColor": "#3B82F6",
                        "pointBackgroundColor": "#3B82F6"
                    },
                    {
                        "label": f"Team {team2_id}",
                        "data": [
                            team2_stats['offense'],
                            team2_stats['defense'],
                            team2_stats['rebounding'], 
                            team2_stats['three_point'],
                            team2_stats['free_throws'],
                            team2_stats['turnovers']
                        ],
                        "backgroundColor": "rgba(239, 68, 68, 0.2)",
                        "borderColor": "#EF4444",
                        "pointBackgroundColor": "#EF4444"
                    }
                ]
            },
            "options": {
                "responsive": True,
                "plugins": {
                    "title": {
                        "display": True,
                        "text": "Team Performance Comparison"
                    }
                },
                "scales": {
                    "r": {
                        "beginAtZero": True,
                        "max": 100
                    }
                }
            }
        }
    
    def generate_trend_analysis(self, team1_id, team2_id):
        """Generate recent performance trend chart"""
        # Generate last 10 games mock data
        dates = []
        team1_scores = []
        team2_scores = []
        
        for i in range(10, 0, -1):
            date = datetime.now() - timedelta(days=i*3)
            dates.append(date.strftime('%m/%d'))
            team1_scores.append(random.randint(95, 125))
            team2_scores.append(random.randint(95, 125))
        
        return {
            "type": "line",
            "data": {
                "labels": dates,
                "datasets": [
                    {
                        "label": f"Team {team1_id} Recent Performance",
                        "data": team1_scores,
                        "borderColor": "#3B82F6",
                        "backgroundColor": "rgba(59, 130, 246, 0.1)",
                        "tension": 0.4
                    },
                    {
                        "label": f"Team {team2_id} Recent Performance", 
                        "data": team2_scores,
                        "borderColor": "#EF4444",
                        "backgroundColor": "rgba(239, 68, 68, 0.1)",
                        "tension": 0.4
                    }
                ]
            },
            "options": {
                "responsive": True,
                "plugins": {
                    "title": {
                        "display": True,
                        "text": "Recent Performance Trend (Last 10 Games)"
                    }
                },
                "scales": {
                    "y": {
                        "beginAtZero": False,
                        "min": 90,
                        "max": 130
                    }
                }
            }
        }
    
    def generate_win_probability_chart(self, prediction_result):
        """Generate win probability pie chart"""
        confidence = prediction_result.get('confidence', 0.5)
        winner_prob = round(confidence * 100, 1)
        loser_prob = round((1 - confidence) * 100, 1)
        
        return {
            "type": "doughnut",
            "data": {
                "labels": ["Winner", "Underdog"],
                "datasets": [{
                    "data": [winner_prob, loser_prob],
                    "backgroundColor": ["#10B981", "#F59E0B"],
                    "borderColor": ["#059669", "#D97706"],
                    "borderWidth": 2
                }]
            },
            "options": {
                "responsive": True,
                "plugins": {
                    "title": {
                        "display": True,
                        "text": "Win Probability"
                    },
                    "legend": {
                        "position": "bottom"
                    }
                }
            }
        }
    
    def get_mock_team_stats(self, team_id):
        """Generate mock team statistics"""
        random.seed(team_id)  # Consistent data for same team
        return {
            "offense": random.randint(60, 95),
            "defense": random.randint(65, 90),
            "rebounding": random.randint(55, 85),
            "three_point": random.randint(70, 95),
            "free_throws": random.randint(75, 95),
            "turnovers": random.randint(60, 85)
        }
    
    def get_confidence_color(self, confidence):
        """Get color based on confidence level"""
        if confidence >= 0.8:
            return "#10B981"  # Green
        elif confidence >= 0.6:
            return "#F59E0B"  # Yellow
        else:
            return "#EF4444"  # Red
    
    def get_default_chart_data(self):
        """Return default chart data when generation fails"""
        return {
            "confidence_chart": {"type": "gauge", "data": {"value": 50}},
            "score_comparison": {"type": "bar", "data": {"labels": [], "datasets": []}},
            "team_comparison": {"type": "radar", "data": {"labels": [], "datasets": []}},
            "trend_analysis": {"type": "line", "data": {"labels": [], "datasets": []}},
            "win_probability": {"type": "doughnut", "data": {"labels": [], "datasets": []}}
        }