"""
NBA Playoff Prediction Service
=============================

Core playoff simulation and prediction logic that integrates with the existing
enhanced prediction service.
"""

import numpy as np
import pandas as pd
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import logging
import random
from collections import defaultdict
from .s3_prediction_storage import S3PredictionStorage, s3_cached_prediction

logger = logging.getLogger(__name__)

class PlayoffPredictor:
    """Core playoff prediction and simulation service"""
    
    def __init__(self, prediction_service, s3_service=None):
        self.prediction_service = prediction_service
        self.s3_service = s3_service
        self.s3_storage = S3PredictionStorage(s3_service) if s3_service else S3PredictionStorage()
        self.conference_teams = self._initialize_conference_teams()
        
    def _initialize_conference_teams(self) -> Dict[str, List[int]]:
        """Initialize teams by conference based on NBA API IDs"""
        return {
            'Eastern': [
                1610612737,  # Atlanta Hawks
                1610612738,  # Boston Celtics
                1610612751,  # Brooklyn Nets
                1610612766,  # Charlotte Hornets
                1610612741,  # Chicago Bulls
                1610612739,  # Cleveland Cavaliers
                1610612765,  # Detroit Pistons
                1610612754,  # Indiana Pacers
                1610612748,  # Miami Heat
                1610612749,  # Milwaukee Bucks
                1610612752,  # New York Knicks
                1610612753,  # Orlando Magic
                1610612755,  # Philadelphia 76ers
                1610612761,  # Toronto Raptors
                1610612764   # Washington Wizards
            ],
            'Western': [
                1610612742,  # Dallas Mavericks
                1610612743,  # Denver Nuggets
                1610612744,  # Golden State Warriors
                1610612745,  # Houston Rockets
                1610612746,  # LA Clippers
                1610612747,  # Los Angeles Lakers
                1610612763,  # Memphis Grizzlies
                1610612750,  # Minnesota Timberwolves
                1610612740,  # New Orleans Pelicans
                1610612760,  # Oklahoma City Thunder
                1610612756,  # Phoenix Suns
                1610612757,  # Portland Trail Blazers
                1610612758,  # Sacramento Kings
                1610612759,  # San Antonio Spurs
                1610612762   # Utah Jazz
            ]
        }
    
    @s3_cached_prediction("conference_standings", ttl_hours=1)
    def simulate_season_standings(self, simulations: int = 1000) -> Dict[str, List[Dict]]:
        """
        Simulate remaining season to predict final conference standings
        
        Args:
            simulations: Number of Monte Carlo simulations to run
            
        Returns:
            Dictionary with Eastern and Western conference predicted standings
        """
        try:
            standings_results = {'Eastern': [], 'Western': []}
            
            for conference, teams in self.conference_teams.items():
                team_stats = self._simulate_conference_season(teams, simulations)
                
                # Sort by projected wins (descending)
                sorted_teams = sorted(team_stats.items(), key=lambda x: x[1]['projected_wins'], reverse=True)
                
                for rank, (team_id, stats) in enumerate(sorted_teams, 1):
                    team_name = self.prediction_service._get_team_name_from_api(team_id)
                    team_abbr = self.prediction_service._get_team_abbreviation_from_api(team_id)
                    
                    standings_results[conference].append({
                        'rank': rank,
                        'team_id': team_id,
                        'team_name': team_name,
                        'team_abbreviation': team_abbr,
                        'projected_wins': stats['projected_wins'],
                        'projected_losses': stats['projected_losses'],
                        'win_percentage': stats['win_percentage'],
                        'playoff_probability': stats['playoff_probability'],
                        'championship_odds': stats['championship_odds']
                    })
            
            logger.info(f"Generated season standings for both conferences")
            return standings_results
            
        except Exception as e:
            logger.error(f"Error simulating season standings: {e}")
            return self._get_default_standings()
    
    def _simulate_conference_season(self, teams: List[int], simulations: int) -> Dict[int, Dict]:
        """Simulate season for a conference"""
        team_stats = {}
        
        for team_id in teams:
            # Get current team rating
            team_rating = self.prediction_service.team_ratings.get(team_id, 1500)
            
            # Simulate games against all other teams
            total_wins = 0
            total_games = 82  # NBA regular season
            
            for _ in range(simulations):
                wins = self._simulate_team_season(team_id, team_rating, teams)
                total_wins += wins
            
            avg_wins = total_wins / simulations
            avg_losses = total_games - avg_wins
            
            # Calculate playoff probability (top 10 teams make playoffs in each conference)
            playoff_prob = self._calculate_playoff_probability(avg_wins, total_games)
            
            # Calculate championship odds based on team strength
            championship_odds = self._calculate_championship_odds(team_rating)
            
            team_stats[team_id] = {
                'projected_wins': round(avg_wins, 1),
                'projected_losses': round(avg_losses, 1),
                'win_percentage': round(avg_wins / total_games, 3),
                'playoff_probability': round(playoff_prob, 3),
                'championship_odds': round(championship_odds, 4)
            }
        
        return team_stats
    
    def _simulate_team_season(self, team_id: int, team_rating: float, conference_teams: List[int]) -> int:
        """Simulate a single team's season"""
        wins = 0
        games_per_team = 3  # Simplified: 3 games vs each conference opponent
        
        for opponent_id in conference_teams:
            if opponent_id == team_id:
                continue
                
            for _ in range(games_per_team):
                # Use existing prediction service to determine win probability
                # Use fast rating-based calculation for bulk simulations
                # (Reserve expensive ML predictions for individual user requests)
                opponent_rating = self.prediction_service.team_ratings.get(opponent_id, 1500)
                win_prob = 1 / (1 + 10**((opponent_rating - team_rating) / 400))
                
                if random.random() < win_prob:
                    wins += 1
        
        return wins
    
    def _calculate_playoff_probability(self, projected_wins: float, total_games: int) -> float:
        """Calculate probability of making playoffs based on projected wins"""
        win_percentage = projected_wins / total_games
        
        # Playoff threshold is typically around 0.500 (41 wins out of 82 games)
        if win_percentage >= 0.600:
            return 0.95
        elif win_percentage >= 0.550:
            return 0.80
        elif win_percentage >= 0.500:
            return 0.60
        elif win_percentage >= 0.450:
            return 0.30
        elif win_percentage >= 0.400:
            return 0.10
        else:
            return 0.05
    
    def _calculate_championship_odds(self, team_rating: float) -> float:
        """Calculate championship odds based on team rating"""
        # Normalize rating to probability (1400-1700 range typically)
        normalized_rating = max(0, min(1, (team_rating - 1400) / 300))
        
        # Championship odds scale from 0.001 to 0.25
        return 0.001 + (normalized_rating * 0.249)
    
    @s3_cached_prediction("playoff_bracket", ttl_hours=2)
    def generate_playoff_bracket(self, standings: Dict[str, List[Dict]] = None) -> Dict:
        """
        Generate playoff bracket based on conference standings
        
        Args:
            standings: Conference standings (if None, will generate new ones)
            
        Returns:
            Complete playoff bracket structure
        """
        try:
            if standings is None:
                standings = self.simulate_season_standings()
            
            # Generate all rounds
            play_in = self._create_play_in_tournament(standings)
            first_round = self._create_first_round(standings)
            conference_semifinals = self._create_conference_semifinals(first_round)
            conference_finals = self._create_conference_finals(conference_semifinals)
            nba_finals = self._create_nba_finals(conference_finals)
            
            bracket = {
                'generated_at': datetime.now().isoformat(),
                'play_in': play_in,
                'first_round': first_round,
                'conference_semifinals': conference_semifinals,
                'conference_finals': conference_finals,
                'nba_finals': nba_finals,
                'championship_odds': self._calculate_bracket_championship_odds(standings)
            }
            
            logger.info("Generated complete playoff bracket with all rounds")
            return bracket
            
        except Exception as e:
            logger.error(f"Error generating playoff bracket: {e}")
            return self._get_default_bracket()
    
    def _create_play_in_tournament(self, standings: Dict[str, List[Dict]]) -> Dict:
        """Create play-in tournament matchups (7-10 seeds)"""
        play_in = {'Eastern': {}, 'Western': {}}
        
        for conference, teams in standings.items():
            # Play-in teams are seeds 7-10
            play_in_teams = teams[6:10]  # 7th, 8th, 9th, 10th seeds
            
            if len(play_in_teams) >= 4:
                play_in[conference] = {
                    'game_1': {
                        'matchup': f"{play_in_teams[0]['team_abbreviation']} vs {play_in_teams[1]['team_abbreviation']}",
                        'teams': [play_in_teams[0], play_in_teams[1]],
                        'description': '7th seed vs 8th seed (winner gets 7th seed)'
                    },
                    'game_2': {
                        'matchup': f"{play_in_teams[2]['team_abbreviation']} vs {play_in_teams[3]['team_abbreviation']}",
                        'teams': [play_in_teams[2], play_in_teams[3]],
                        'description': '9th seed vs 10th seed (winner plays loser of Game 1)'
                    }
                }
        
        return play_in
    
    def _create_first_round(self, standings: Dict[str, List[Dict]]) -> Dict:
        """Create first round playoff matchups"""
        first_round = {'Eastern': [], 'Western': []}
        
        for conference, teams in standings.items():
            # Top 6 seeds get automatic playoff spots
            playoff_teams = teams[:6]
            
            # Add play-in winners (assume 7th and 8th seeds for now)
            if len(teams) >= 8:
                playoff_teams.extend(teams[6:8])
            
            # Create matchups: 1v8, 2v7, 3v6, 4v5
            if len(playoff_teams) >= 8:
                matchups = [
                    (playoff_teams[0], playoff_teams[7]),  # 1 vs 8
                    (playoff_teams[1], playoff_teams[6]),  # 2 vs 7
                    (playoff_teams[2], playoff_teams[5]),  # 3 vs 6
                    (playoff_teams[3], playoff_teams[4])   # 4 vs 5
                ]
                
                for higher_seed, lower_seed in matchups:
                    series_prediction = self._predict_series(higher_seed, lower_seed)
                    
                    first_round[conference].append({
                        'matchup': f"{higher_seed['team_abbreviation']} vs {lower_seed['team_abbreviation']}",
                        'higher_seed': higher_seed,
                        'lower_seed': lower_seed,
                        'series_prediction': series_prediction
                    })
        
        return first_round
    
    def _predict_series(self, team1: Dict, team2: Dict, series_length: int = 7) -> Dict:
        """Predict a playoff series between two teams"""
        try:
            team1_id = team1['team_id']
            team2_id = team2['team_id']
            
            # Use fast rating-based calculation for bulk simulations
            team1_rating = self.prediction_service.team_ratings.get(team1_id, 1500)
            team2_rating = self.prediction_service.team_ratings.get(team2_id, 1500)
            
            team1_game_win_prob = 1 / (1 + 10**((team2_rating - team1_rating) / 400))
            team2_game_win_prob = 1 - team1_game_win_prob
            
            # Simulate series (best of 7)
            team1_series_wins = 0
            team2_series_wins = 0
            simulations = 1000
            
            for _ in range(simulations):
                t1_wins, t2_wins = self._simulate_single_series(team1_game_win_prob, series_length)
                if t1_wins > t2_wins:
                    team1_series_wins += 1
                else:
                    team2_series_wins += 1
            
            team1_series_prob = team1_series_wins / simulations
            
            return {
                'team1_series_probability': round(team1_series_prob, 3),
                'team2_series_probability': round(1 - team1_series_prob, 3),
                'predicted_winner': team1 if team1_series_prob > 0.5 else team2,
                'confidence': round(max(team1_series_prob, 1 - team1_series_prob), 3),
                'predicted_games': self._predict_series_length(team1_game_win_prob)
            }
            
        except Exception as e:
            logger.error(f"Error predicting series: {e}")
            return {
                'team1_series_probability': 0.5,
                'team2_series_probability': 0.5,
                'predicted_winner': team1,
                'confidence': 0.5,
                'predicted_games': 6
            }
    
    def _simulate_single_series(self, team1_win_prob: float, series_length: int = 7) -> Tuple[int, int]:
        """Simulate a single playoff series"""
        team1_wins = 0
        team2_wins = 0
        games_needed = (series_length // 2) + 1  # 4 wins needed for best of 7
        
        while team1_wins < games_needed and team2_wins < games_needed:
            if random.random() < team1_win_prob:
                team1_wins += 1
            else:
                team2_wins += 1
        
        return team1_wins, team2_wins
    
    def _predict_series_length(self, stronger_team_prob: float) -> int:
        """Predict how many games a series will last"""
        if stronger_team_prob >= 0.7:
            return random.choice([4, 5])  # Dominant team wins quickly
        elif stronger_team_prob >= 0.6:
            return random.choice([5, 6])  # Strong team but some resistance
        else:
            return random.choice([6, 7])  # Competitive series
    
    def _calculate_bracket_championship_odds(self, standings: Dict[str, List[Dict]]) -> List[Dict]:
        """Calculate championship odds for all teams"""
        all_teams = []
        
        for conference_teams in standings.values():
            for team in conference_teams:
                all_teams.append({
                    'team_id': team['team_id'],
                    'team_name': team['team_name'],
                    'team_abbreviation': team['team_abbreviation'],
                    'conference': 'Eastern' if team in standings['Eastern'] else 'Western',
                    'championship_odds': team['championship_odds'],
                    'conference_odds': team['playoff_probability'] * 0.5 if team['rank'] <= 8 else 0.0
                })
        
        # Sort by championship odds
        all_teams.sort(key=lambda x: x['championship_odds'], reverse=True)
        
        return all_teams
    
    def _create_conference_semifinals(self, first_round: Dict) -> Dict:
        """Create conference semifinals matchups based on first round winners"""
        semifinals = {'Eastern': [], 'Western': []}
        
        for conference, matchups in first_round.items():
            if len(matchups) >= 4:
                # Get winners from first round
                winners = []
                for matchup in matchups:
                    winner = matchup['series_prediction']['predicted_winner']
                    winners.append(winner)
                
                # Create semifinals matchups (1v4 winner vs 2v3 winner style)
                if len(winners) >= 4:
                    semifinal_matchups = [
                        (winners[0], winners[3]),  # 1v8 winner vs 4v5 winner
                        (winners[1], winners[2])   # 2v7 winner vs 3v6 winner
                    ]
                    
                    for team1, team2 in semifinal_matchups:
                        series_prediction = self._predict_series(team1, team2)
                        
                        semifinals[conference].append({
                            'matchup': f"{team1['team_abbreviation']} vs {team2['team_abbreviation']}",
                            'team1': team1,
                            'team2': team2,
                            'series_prediction': series_prediction
                        })
        
        return semifinals
    
    def _create_conference_finals(self, conference_semifinals: Dict) -> Dict:
        """Create conference finals matchups based on semifinals winners"""
        conference_finals = {'Eastern': {}, 'Western': {}}
        
        for conference, matchups in conference_semifinals.items():
            if len(matchups) >= 2:
                # Get winners from semifinals
                winner1 = matchups[0]['series_prediction']['predicted_winner']
                winner2 = matchups[1]['series_prediction']['predicted_winner']
                
                series_prediction = self._predict_series(winner1, winner2)
                
                conference_finals[conference] = {
                    'matchup': f"{winner1['team_abbreviation']} vs {winner2['team_abbreviation']}",
                    'team1': winner1,
                    'team2': winner2,
                    'series_prediction': series_prediction
                }
        
        return conference_finals
    
    def _create_nba_finals(self, conference_finals: Dict) -> Dict:
        """Create NBA Finals matchup based on conference champions"""
        if 'Eastern' in conference_finals and 'Western' in conference_finals:
            eastern_champion = conference_finals['Eastern'].get('series_prediction', {}).get('predicted_winner')
            western_champion = conference_finals['Western'].get('series_prediction', {}).get('predicted_winner')
            
            if eastern_champion and western_champion:
                series_prediction = self._predict_series(eastern_champion, western_champion)
                
                return {
                    'matchup': f"{eastern_champion['team_abbreviation']} vs {western_champion['team_abbreviation']}",
                    'eastern_champion': eastern_champion,
                    'western_champion': western_champion,
                    'series_prediction': series_prediction
                }
        
        return {}
    
    def _get_default_standings(self) -> Dict[str, List[Dict]]:
        """Return default standings if simulation fails"""
        return {
            'Eastern': [
                {'rank': i, 'team_id': team_id, 'projected_wins': 45.0, 'projected_losses': 37.0, 
                 'win_percentage': 0.549, 'playoff_probability': 0.6, 'championship_odds': 0.033}
                for i, team_id in enumerate(self.conference_teams['Eastern'], 1)
            ],
            'Western': [
                {'rank': i, 'team_id': team_id, 'projected_wins': 45.0, 'projected_losses': 37.0,
                 'win_percentage': 0.549, 'playoff_probability': 0.6, 'championship_odds': 0.033}
                for i, team_id in enumerate(self.conference_teams['Western'], 1)
            ]
        }
    
    def _get_default_bracket(self) -> Dict:
        """Return default bracket if generation fails"""
        return {
            'generated_at': datetime.now().isoformat(),
            'play_in': {'Eastern': {}, 'Western': {}},
            'first_round': {'Eastern': [], 'Western': []},
            'conference_semifinals': {},
            'conference_finals': {},
            'nba_finals': {},
            'championship_odds': []
        }