"""
Championship Odds Calculator
===========================

Advanced calculations for championship probabilities, conference odds,
and playoff path analysis.
"""

import numpy as np
import pandas as pd
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import logging
from itertools import combinations
from .s3_prediction_storage import s3_cached_prediction

logger = logging.getLogger(__name__)

class ChampionshipCalculator:
    """Calculate championship probabilities and playoff scenarios"""
    
    def __init__(self, prediction_service, playoff_predictor, s3_service=None):
        self.prediction_service = prediction_service
        self.playoff_predictor = playoff_predictor
        self.s3_service = s3_service
    
    @s3_cached_prediction("championship_odds", ttl_hours=6)
    def calculate_comprehensive_odds(self, standings: Dict[str, List[Dict]] = None, simulations: int = 5000) -> Dict:
        """
        Calculate comprehensive championship odds using Monte Carlo simulation
        
        Args:
            standings: Conference standings (if None, will generate)
            simulations: Number of playoff simulations to run
            
        Returns:
            Comprehensive odds breakdown for all teams
        """
        try:
            if standings is None:
                standings = self.playoff_predictor.simulate_season_standings()
            
            results = {
                'last_updated': datetime.now().isoformat(),
                'simulations_run': simulations,
                'championship_odds': [],
                'conference_odds': {'Eastern': [], 'Western': []},
                'round_probabilities': {},
                'playoff_scenarios': {}
            }
            
            # Run playoff simulations
            team_results = self._run_championship_simulations(standings, simulations)
            
            # Process results
            results['championship_odds'] = self._format_championship_odds(team_results)
            results['conference_odds'] = self._format_conference_odds(team_results, standings)
            results['round_probabilities'] = self._calculate_round_probabilities(team_results)
            results['playoff_scenarios'] = self._analyze_playoff_scenarios(team_results)
            
            logger.info(f"Calculated comprehensive odds with {simulations} simulations")
            return results
            
        except Exception as e:
            logger.error(f"Error calculating comprehensive odds: {e}")
            return self._get_default_odds()
    
    def _run_championship_simulations(self, standings: Dict[str, List[Dict]], simulations: int) -> Dict:
        """Run multiple playoff simulations to calculate probabilities"""
        team_results = {}
        
        # Initialize tracking for all teams
        for conference, teams in standings.items():
            for team in teams:
                team_id = team['team_id']
                team_results[team_id] = {
                    'team_info': team,
                    'conference': conference,
                    'championships': 0,
                    'conference_finals': 0,
                    'conference_semifinals': 0,
                    'first_round': 0,
                    'play_in': 0,
                    'missed_playoffs': 0,
                    'finals_appearances': 0
                }
        
        # Run simulations
        for sim in range(simulations):
            playoff_result = self._simulate_single_playoff(standings)
            self._update_team_results(team_results, playoff_result)
            
            if sim % 1000 == 0:
                logger.info(f"Completed {sim}/{simulations} playoff simulations")
        
        # Convert counts to probabilities
        for team_id, results in team_results.items():
            for key in ['championships', 'conference_finals', 'conference_semifinals', 
                       'first_round', 'play_in', 'missed_playoffs', 'finals_appearances']:
                results[f'{key}_probability'] = results[key] / simulations
        
        return team_results
    
    def _simulate_single_playoff(self, standings: Dict[str, List[Dict]]) -> Dict:
        """Simulate a complete playoff tournament"""
        playoff_result = {
            'champion': None,
            'finals_teams': [],
            'conference_champions': {'Eastern': None, 'Western': None},
            'round_results': {
                'play_in': {'Eastern': [], 'Western': []},
                'first_round': {'Eastern': [], 'Western': []},
                'conference_semifinals': {'Eastern': [], 'Western': []},
                'conference_finals': {'Eastern': [], 'Western': []}
            }
        }
        
        # Simulate each conference
        for conference, teams in standings.items():
            conference_champion = self._simulate_conference_playoffs(teams, conference, playoff_result)
            playoff_result['conference_champions'][conference] = conference_champion
            playoff_result['finals_teams'].append(conference_champion)
        
        # Simulate NBA Finals
        if len(playoff_result['finals_teams']) == 2:
            east_champ = playoff_result['finals_teams'][0]
            west_champ = playoff_result['finals_teams'][1]
            
            finals_winner = self._simulate_finals(east_champ, west_champ)
            playoff_result['champion'] = finals_winner
        
        return playoff_result
    
    def _simulate_conference_playoffs(self, teams: List[Dict], conference: str, playoff_result: Dict) -> Dict:
        """Simulate playoffs for one conference"""
        # Play-in tournament (teams 7-10)
        play_in_teams = teams[6:10] if len(teams) >= 10 else []
        playoff_teams = teams[:6].copy()  # Top 6 auto-qualify
        
        if len(play_in_teams) >= 4:
            # Simulate play-in games
            play_in_winners = self._simulate_play_in(play_in_teams)
            playoff_teams.extend(play_in_winners)
            
            for team in play_in_teams:
                playoff_result['round_results']['play_in'][conference].append(team['team_id'])
        
        # Ensure we have 8 playoff teams
        while len(playoff_teams) < 8 and len(teams) > len(playoff_teams):
            playoff_teams.append(teams[len(playoff_teams)])
        
        # First Round (8 teams -> 4 teams)
        first_round_winners = self._simulate_playoff_round(playoff_teams, 'first_round')
        for team in first_round_winners:
            playoff_result['round_results']['first_round'][conference].append(team['team_id'])
        
        # Conference Semifinals (4 teams -> 2 teams)
        semifinals_winners = self._simulate_playoff_round(first_round_winners, 'semifinals')
        for team in semifinals_winners:
            playoff_result['round_results']['conference_semifinals'][conference].append(team['team_id'])
        
        # Conference Finals (2 teams -> 1 team)
        if len(semifinals_winners) >= 2:
            finals_winner = self._simulate_playoff_round(semifinals_winners, 'finals')[0]
            playoff_result['round_results']['conference_finals'][conference].append(finals_winner['team_id'])
            return finals_winner
        
        return semifinals_winners[0] if semifinals_winners else playoff_teams[0]
    
    def _simulate_play_in(self, teams: List[Dict]) -> List[Dict]:
        """Simulate play-in tournament"""
        if len(teams) < 4:
            return teams[:2]
        
        # Game 1: 7 vs 8 (winner gets 7th seed)
        game1_winner = self._simulate_head_to_head(teams[0], teams[1])
        game1_loser = teams[1] if game1_winner == teams[0] else teams[0]
        
        # Game 2: 9 vs 10 (winner plays loser of Game 1)
        game2_winner = self._simulate_head_to_head(teams[2], teams[3])
        
        # Final play-in game: loser of Game 1 vs winner of Game 2
        eighth_seed = self._simulate_head_to_head(game1_loser, game2_winner)
        
        return [game1_winner, eighth_seed]
    
    def _simulate_playoff_round(self, teams: List[Dict], round_name: str) -> List[Dict]:
        """Simulate a playoff round"""
        if len(teams) <= 1:
            return teams
        
        winners = []
        
        # Pair teams for matchups
        if round_name == 'first_round':
            # 1v8, 2v7, 3v6, 4v5
            matchups = [(teams[0], teams[7]), (teams[1], teams[6]), 
                       (teams[2], teams[5]), (teams[3], teams[4])]
        else:
            # Pair sequentially for later rounds
            matchups = [(teams[i], teams[i+1]) for i in range(0, len(teams)-1, 2)]
        
        for team1, team2 in matchups:
            winner = self._simulate_head_to_head(team1, team2)
            winners.append(winner)
        
        return winners
    
    def _simulate_head_to_head(self, team1: Dict, team2: Dict) -> Dict:
        """Simulate head-to-head matchup between two teams"""
        try:
            # Use fast rating-based calculation for bulk simulations
            team1_rating = self.prediction_service.team_ratings.get(team1['team_id'], 1500)
            team2_rating = self.prediction_service.team_ratings.get(team2['team_id'], 1500)
            team1_win_prob = 1 / (1 + 10**((team2_rating - team1_rating) / 400))
            
            # For playoffs, boost win probability slightly (home advantage simulation)
            team1_series_prob = min(0.95, team1_win_prob * 1.1)
            
            return team1 if np.random.random() < team1_series_prob else team2
            
        except Exception as e:
            logger.warning(f"Error in head-to-head simulation: {e}")
            # Fallback to higher seed wins
            return team1 if team1.get('rank', 15) < team2.get('rank', 15) else team2
    
    def _simulate_finals(self, east_champ: Dict, west_champ: Dict) -> Dict:
        """Simulate NBA Finals"""
        return self._simulate_head_to_head(east_champ, west_champ)
    
    def _update_team_results(self, team_results: Dict, playoff_result: Dict):
        """Update team results based on playoff simulation"""
        # Track championship
        if playoff_result['champion']:
            team_results[playoff_result['champion']['team_id']]['championships'] += 1
        
        # Track finals appearances
        for team in playoff_result['finals_teams']:
            if team:
                team_results[team['team_id']]['finals_appearances'] += 1
        
        # Track conference champions
        for conference, champion in playoff_result['conference_champions'].items():
            if champion:
                team_results[champion['team_id']]['conference_finals'] += 1
        
        # Track round progression
        for round_name, conferences in playoff_result['round_results'].items():
            for conference, team_ids in conferences.items():
                for team_id in team_ids:
                    if team_id in team_results:
                        team_results[team_id][round_name] += 1
    
    def _format_championship_odds(self, team_results: Dict) -> List[Dict]:
        """Format championship odds for display"""
        odds_list = []
        
        for team_id, results in team_results.items():
            odds_list.append({
                'team_id': team_id,
                'team_name': results['team_info']['team_name'],
                'team_abbreviation': results['team_info']['team_abbreviation'],
                'conference': results['conference'],
                'rank': results['team_info']['rank'],
                'championship_probability': round(results['championships_probability'], 4),
                'finals_probability': round(results['finals_appearances_probability'], 4),
                'conference_finals_probability': round(results['conference_finals_probability'], 4),
                'playoff_probability': round(1 - results['missed_playoffs_probability'], 4)
            })
        
        # Sort by championship probability
        odds_list.sort(key=lambda x: x['championship_probability'], reverse=True)
        
        return odds_list
    
    def _format_conference_odds(self, team_results: Dict, standings: Dict) -> Dict:
        """Format conference championship odds"""
        conference_odds = {'Eastern': [], 'Western': []}
        
        for conference, teams in standings.items():
            for team in teams:
                team_id = team['team_id']
                if team_id in team_results:
                    conference_odds[conference].append({
                        'team_id': team_id,
                        'team_name': team['team_name'],
                        'team_abbreviation': team['team_abbreviation'],
                        'rank': team['rank'],
                        'conference_championship_probability': round(
                            team_results[team_id]['conference_finals_probability'], 4
                        ),
                        'playoff_probability': round(
                            1 - team_results[team_id]['missed_playoffs_probability'], 4
                        )
                    })
            
            # Sort by conference championship probability
            conference_odds[conference].sort(
                key=lambda x: x['conference_championship_probability'], reverse=True
            )
        
        return conference_odds
    
    def _calculate_round_probabilities(self, team_results: Dict) -> Dict:
        """Calculate probabilities for reaching each playoff round"""
        round_probs = {}
        
        for team_id, results in team_results.items():
            round_probs[team_id] = {
                'team_name': results['team_info']['team_name'],
                'make_playoffs': round(1 - results['missed_playoffs_probability'], 4),
                'first_round': round(results['first_round_probability'], 4),
                'conference_semifinals': round(results['conference_semifinals_probability'], 4),
                'conference_finals': round(results['conference_finals_probability'], 4),
                'nba_finals': round(results['finals_appearances_probability'], 4),
                'championship': round(results['championships_probability'], 4)
            }
        
        return round_probs
    
    def _analyze_playoff_scenarios(self, team_results: Dict) -> Dict:
        """Analyze various playoff scenarios and outcomes"""
        scenarios = {
            'most_likely_champion': None,
            'most_likely_finals': [],
            'upset_potential': [],
            'conference_balance': {}
        }
        
        # Find most likely champion
        max_prob = 0
        for team_id, results in team_results.items():
            if results['championships_probability'] > max_prob:
                max_prob = results['championships_probability']
                scenarios['most_likely_champion'] = {
                    'team_id': team_id,
                    'team_name': results['team_info']['team_name'],
                    'probability': round(max_prob, 4)
                }
        
        # Find most likely finals matchup
        finals_combos = {}
        # This would require tracking actual finals matchups in simulation
        # For now, use top teams from each conference
        
        return scenarios
    
    def _get_default_odds(self) -> Dict:
        """Return default odds if calculation fails"""
        return {
            'last_updated': datetime.now().isoformat(),
            'simulations_run': 0,
            'championship_odds': [],
            'conference_odds': {'Eastern': [], 'Western': []},
            'round_probabilities': {},
            'playoff_scenarios': {}
        }