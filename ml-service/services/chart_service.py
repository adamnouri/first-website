import logging
from datetime import datetime, timedelta
import random
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import numpy as np
from io import BytesIO
import seaborn as sns
from typing import Dict, Any

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
    
    def generate_prediction_chart_image(self, prediction_result: Dict[Any, Any], 
                                      team1_name: str, team2_name: str) -> bytes:
        """Generate a comprehensive prediction chart as PNG image for S3 storage"""
        try:
            # Set up the matplotlib style
            plt.style.use('default')
            sns.set_palette("husl")
            
            # Create figure with subplots
            fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
            fig.suptitle(f'NBA Game Prediction: {team1_name} vs {team2_name}', 
                        fontsize=20, fontweight='bold', y=0.98)
            
            # 1. Score Comparison Bar Chart
            self._create_score_comparison_chart(ax1, prediction_result, team1_name, team2_name)
            
            # 2. Confidence Gauge (simplified as bar)
            self._create_confidence_chart(ax2, prediction_result)
            
            # 3. Team Stats Radar (simplified as bar chart)
            self._create_team_stats_chart(ax3, team1_name, team2_name)
            
            # 4. Win Probability Pie Chart
            self._create_win_probability_chart(ax4, prediction_result, team1_name, team2_name)
            
            # Adjust layout
            plt.tight_layout()
            plt.subplots_adjust(top=0.93)
            
            # Save to bytes
            img_buffer = BytesIO()
            plt.savefig(img_buffer, format='PNG', dpi=300, bbox_inches='tight', 
                       facecolor='white', edgecolor='none')
            img_buffer.seek(0)
            image_bytes = img_buffer.getvalue()
            img_buffer.close()
            
            # Clean up
            plt.close(fig)
            
            return image_bytes
            
        except Exception as e:
            logger.error(f"Error generating prediction chart image: {e}")
            return self._generate_error_chart_image()
    
    def _create_score_comparison_chart(self, ax, prediction_result, team1_name, team2_name):
        """Create predicted score comparison bar chart"""
        team1_score = prediction_result.get('team1_predicted_score', 105)
        team2_score = prediction_result.get('team2_predicted_score', 105)
        
        teams = [team1_name, team2_name]
        scores = [team1_score, team2_score]
        colors = ['#3B82F6', '#EF4444']
        
        bars = ax.bar(teams, scores, color=colors, alpha=0.8)
        ax.set_title('Predicted Final Scores', fontsize=14, fontweight='bold')
        ax.set_ylabel('Points', fontsize=12)
        ax.set_ylim(80, 130)
        
        # Add score labels on bars
        for bar, score in zip(bars, scores):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1, 
                   str(score), ha='center', va='bottom', fontweight='bold', fontsize=12)
        
        ax.grid(axis='y', alpha=0.3)
    
    def _create_confidence_chart(self, ax, prediction_result):
        """Create confidence level visualization"""
        confidence = prediction_result.get('confidence', 0.5) * 100
        winner = prediction_result.get('predicted_winner', 'Team')
        
        # Create a horizontal bar chart
        colors = ['#10B981' if confidence >= 75 else '#F59E0B' if confidence >= 60 else '#EF4444']
        bars = ax.barh(['Confidence'], [confidence], color=colors, alpha=0.8)
        
        ax.set_title('Prediction Confidence', fontsize=14, fontweight='bold')
        ax.set_xlabel('Confidence Level (%)', fontsize=12)
        ax.set_xlim(0, 100)
        
        # Add percentage label
        ax.text(confidence + 2, 0, f'{confidence:.1f}%', 
               va='center', ha='left', fontweight='bold', fontsize=12)
        
        # Add winner text
        ax.text(50, -0.3, f'Predicted Winner: {winner}', 
               ha='center', va='top', fontsize=11, style='italic')
        
        ax.grid(axis='x', alpha=0.3)
    
    def _create_team_stats_chart(self, ax, team1_name, team2_name):
        """Create team statistics comparison"""
        # Mock team stats
        categories = ['Offense', 'Defense', 'Rebounding', '3-Point', 'FT%']
        team1_stats = [random.randint(60, 95) for _ in range(5)]
        team2_stats = [random.randint(60, 95) for _ in range(5)]
        
        x = np.arange(len(categories))
        width = 0.35
        
        bars1 = ax.bar(x - width/2, team1_stats, width, label=team1_name, 
                      color='#3B82F6', alpha=0.8)
        bars2 = ax.bar(x + width/2, team2_stats, width, label=team2_name, 
                      color='#EF4444', alpha=0.8)
        
        ax.set_title('Team Statistics Comparison', fontsize=14, fontweight='bold')
        ax.set_ylabel('Rating', fontsize=12)
        ax.set_xticks(x)
        ax.set_xticklabels(categories, rotation=45, ha='right')
        ax.legend()
        ax.set_ylim(0, 100)
        ax.grid(axis='y', alpha=0.3)
    
    def _create_win_probability_chart(self, ax, prediction_result, team1_name, team2_name):
        """Create win probability pie chart"""
        confidence = prediction_result.get('confidence', 0.5)
        winner = prediction_result.get('predicted_winner', team1_name)
        
        if winner == team1_name:
            team1_prob = confidence * 100
            team2_prob = (1 - confidence) * 100
        else:
            team1_prob = (1 - confidence) * 100
            team2_prob = confidence * 100
        
        sizes = [team1_prob, team2_prob]
        labels = [f'{team1_name}\n{team1_prob:.1f}%', f'{team2_name}\n{team2_prob:.1f}%']
        colors = ['#3B82F6', '#EF4444']
        
        wedges, texts, autotexts = ax.pie(sizes, labels=labels, colors=colors, 
                                         autopct='', startangle=90, 
                                         textprops={'fontsize': 10})
        
        ax.set_title('Win Probability', fontsize=14, fontweight='bold')
        
        # Highlight the favorite
        if team1_prob > team2_prob:
            wedges[0].set_edgecolor('black')
            wedges[0].set_linewidth(2)
        else:
            wedges[1].set_edgecolor('black')
            wedges[1].set_linewidth(2)
    
    def _generate_error_chart_image(self) -> bytes:
        """Generate a simple error chart when main chart generation fails"""
        try:
            fig, ax = plt.subplots(figsize=(8, 6))
            ax.text(0.5, 0.5, 'Chart Generation Error\nUsing Default View', 
                   ha='center', va='center', fontsize=16, 
                   bbox=dict(boxstyle="round,pad=0.3", facecolor="lightcoral"))
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.axis('off')
            
            img_buffer = BytesIO()
            plt.savefig(img_buffer, format='PNG', dpi=150, bbox_inches='tight')
            img_buffer.seek(0)
            image_bytes = img_buffer.getvalue()
            img_buffer.close()
            plt.close(fig)
            
            return image_bytes
        except Exception:
            # Return minimal error image as bytes
            return b'PNG_ERROR_PLACEHOLDER'
    
    def generate_batch_charts(self, predictions_data: list) -> dict:
        """Generate multiple chart images for batch processing"""
        chart_results = {}
        
        for prediction in predictions_data:
            try:
                prediction_uuid = prediction.get('prediction_uuid')
                prediction_result = prediction.get('prediction_result', {})
                team1_name = prediction.get('team1_name', 'Team 1')
                team2_name = prediction.get('team2_name', 'Team 2')
                
                chart_image = self.generate_prediction_chart_image(
                    prediction_result, team1_name, team2_name
                )
                
                chart_results[prediction_uuid] = {
                    'success': True,
                    'image_bytes': chart_image,
                    'size_kb': len(chart_image) / 1024
                }
                
            except Exception as e:
                logger.error(f"Failed to generate chart for {prediction.get('prediction_uuid')}: {e}")
                chart_results[prediction.get('prediction_uuid')] = {
                    'success': False,
                    'error': str(e),
                    'image_bytes': self._generate_error_chart_image()
                }
        
        return chart_results