import { apiClient, mlClient } from './api';

export const predictionService = {
  // Prediction retrieval from Spring Boot backend
  getPredictionForMatchup: async (team1Id, team2Id) => {
    try {
      const response = await apiClient.get(`/api/v1/predictions/matchup`, {
        params: { team1: team1Id, team2: team2Id }
      });
      return response.data;
    } catch (error) {
      throw new Error(`Failed to get prediction for matchup: ${error.message}`);
    }
  },

  getUpcomingPredictions: async () => {
    try {
      const response = await apiClient.get('/api/v1/predictions/upcoming');
      return response.data;
    } catch (error) {
      throw new Error(`Failed to get upcoming predictions: ${error.message}`);
    }
  },

  getPredictionHistory: async (page = 0, size = 20) => {
    try {
      const response = await apiClient.get('/api/v1/predictions/history', {
        params: { page, size }
      });
      return response.data;
    } catch (error) {
      throw new Error(`Failed to get prediction history: ${error.message}`);
    }
  },

  getPredictionById: async (predictionUuid) => {
    try {
      const response = await apiClient.get(`/api/v1/predictions/${predictionUuid}`);
      return response.data;
    } catch (error) {
      throw new Error(`Failed to get prediction ${predictionUuid}: ${error.message}`);
    }
  },

  getPredictionsByTeam: async (teamId, page = 0, size = 10) => {
    try {
      const response = await apiClient.get(`/api/v1/predictions/team/${teamId}`, {
        params: { page, size }
      });
      return response.data;
    } catch (error) {
      throw new Error(`Failed to get predictions for team ${teamId}: ${error.message}`);
    }
  },

  getPredictionsInDateRange: async (startDate, endDate) => {
    try {
      const response = await apiClient.get('/api/v1/predictions/date-range', {
        params: { startDate, endDate }
      });
      return response.data;
    } catch (error) {
      throw new Error(`Failed to get predictions for date range: ${error.message}`);
    }
  },

  // Analytics endpoints
  getModelAccuracy: async () => {
    try {
      const response = await apiClient.get('/api/v1/predictions/accuracy');
      return response.data;
    } catch (error) {
      throw new Error(`Failed to get model accuracy: ${error.message}`);
    }
  },

  getStalePredictions: async (staleDays = 7) => {
    try {
      const response = await apiClient.get('/api/v1/predictions/stale', {
        params: { staleDays }
      });
      return response.data;
    } catch (error) {
      throw new Error(`Failed to get stale predictions: ${error.message}`);
    }
  },

  // Management endpoints
  updatePredictionResults: async (predictionUuid, actualResults) => {
    try {
      const response = await apiClient.post('/api/v1/predictions/update-results', {
        predictionUuid,
        ...actualResults
      });
      return response.data;
    } catch (error) {
      throw new Error(`Failed to update prediction results: ${error.message}`);
    }
  },

  triggerModelRetrain: async () => {
    try {
      const response = await apiClient.post('/api/v1/predictions/trigger-retrain');
      return response.data;
    } catch (error) {
      throw new Error(`Failed to trigger model retrain: ${error.message}`);
    }
  },

  // ML Service endpoints (fallback and real-time)
  generateRealTimePrediction: async (team1Id, team2Id, gameDate) => {
    try {
      const response = await mlClient.post('/predict', {
        team1_id: team1Id,
        team2_id: team2Id,
        game_date: gameDate
      });
      return response.data;
    } catch (error) {
      throw new Error(`Failed to generate real-time prediction: ${error.message}`);
    }
  },

  generateBatchPredictions: async (matchups) => {
    try {
      const response = await mlClient.post('/batch/generate-predictions', {
        matchups
      });
      return response.data;
    } catch (error) {
      throw new Error(`Failed to generate batch predictions: ${error.message}`);
    }
  },

  generateUpcomingGamesPredictions: async (daysAhead = 7) => {
    try {
      const response = await mlClient.post('/batch/upcoming-games', {
        days_ahead: daysAhead
      });
      return response.data;
    } catch (error) {
      throw new Error(`Failed to generate upcoming games predictions: ${error.message}`);
    }
  },

  getTeamRankings: async () => {
    try {
      const response = await mlClient.get('/teams/rankings');
      return response.data;
    } catch (error) {
      throw new Error(`Failed to get team rankings: ${error.message}`);
    }
  },

  getModelInfo: async () => {
    try {
      const response = await mlClient.get('/model/info');
      return response.data;
    } catch (error) {
      throw new Error(`Failed to get model info: ${error.message}`);
    }
  },

  // Health check
  checkPredictionServiceHealth: async () => {
    try {
      const response = await apiClient.get('/api/v1/predictions/health');
      return response.data;
    } catch (error) {
      throw new Error(`Prediction service health check failed: ${error.message}`);
    }
  },

  checkMLServiceHealth: async () => {
    try {
      const response = await mlClient.get('/health');
      return response.data;
    } catch (error) {
      throw new Error(`ML service health check failed: ${error.message}`);
    }
  },

  // ============================================================================
  // PLAYOFF PREDICTION SERVICES
  // ============================================================================

  // Conference standings predictions
  getConferenceStandings: async (conference = 'both', simulations = 1000) => {
    try {
      const response = await apiClient.get('/api/v1/playoffs/conference-standings', {
        params: { conference, simulations }
      });
      return response.data;
    } catch (error) {
      throw new Error(`Failed to get conference standings: ${error.message}`);
    }
  },

  // Generate playoff bracket
  generatePlayoffBracket: async (useCached = false) => {
    try {
      const response = await apiClient.get('/api/v1/playoffs/bracket', {
        params: { use_cached: useCached }
      });
      return response.data;
    } catch (error) {
      throw new Error(`Failed to generate playoff bracket: ${error.message}`);
    }
  },

  // Championship odds calculation
  getChampionshipOdds: async (simulations = 5000) => {
    try {
      const response = await apiClient.get('/api/v1/playoffs/championship-odds', {
        params: { simulations }
      });
      return response.data;
    } catch (error) {
      throw new Error(`Failed to get championship odds: ${error.message}`);
    }
  },

  // Predict playoff series
  predictPlayoffSeries: async (team1Id, team2Id, round = 'first_round', seriesLength = 7) => {
    try {
      const response = await apiClient.post('/api/v1/playoffs/series-prediction', {
        team1_id: team1Id,
        team2_id: team2Id,
        round,
        series_length: seriesLength
      });
      return response.data;
    } catch (error) {
      throw new Error(`Failed to predict playoff series: ${error.message}`);
    }
  },

  // Simulate full tournament
  simulatePlayoffTournament: async (simulations = 1000, standings = null, includePlayIn = true) => {
    try {
      const response = await apiClient.post('/api/v1/playoffs/simulate-tournament', {
        simulations,
        standings,
        include_play_in: includePlayIn
      });
      return response.data;
    } catch (error) {
      throw new Error(`Failed to simulate playoff tournament: ${error.message}`);
    }
  },

  // Get detailed odds for specific team
  getTeamPlayoffOdds: async (teamId) => {
    try {
      const response = await apiClient.get(`/api/v1/playoffs/team-odds/${teamId}`);
      return response.data;
    } catch (error) {
      throw new Error(`Failed to get team playoff odds: ${error.message}`);
    }
  },

  // Convenience methods for specific use cases
  getEasternConferenceStandings: async (simulations = 1000) => {
    return predictionService.getConferenceStandings('eastern', simulations);
  },

  getWesternConferenceStandings: async (simulations = 1000) => {
    return predictionService.getConferenceStandings('western', simulations);
  },

  // Get playoff odds for multiple teams
  getBulkTeamOdds: async (teamIds) => {
    try {
      const promises = teamIds.map(teamId => 
        predictionService.getTeamPlayoffOdds(teamId).catch(error => ({
          teamId,
          error: error.message
        }))
      );
      
      const results = await Promise.all(promises);
      return {
        team_odds: results.filter(result => !result.error),
        errors: results.filter(result => result.error),
        timestamp: new Date().toISOString()
      };
    } catch (error) {
      throw new Error(`Failed to get bulk team odds: ${error.message}`);
    }
  },

  // Get playoff bracket with specific conference focus
  getConferenceBracket: async (conference, useCached = false) => {
    try {
      const bracket = await predictionService.generatePlayoffBracket(useCached);
      
      if (conference.toLowerCase() === 'eastern') {
        return {
          ...bracket,
          bracket: {
            ...bracket.bracket,
            first_round: { Eastern: bracket.bracket.first_round?.Eastern || [] },
            conference_semifinals: { Eastern: bracket.bracket.conference_semifinals?.Eastern || {} },
            conference_finals: { Eastern: bracket.bracket.conference_finals?.Eastern || {} }
          }
        };
      } else if (conference.toLowerCase() === 'western') {
        return {
          ...bracket,
          bracket: {
            ...bracket.bracket,
            first_round: { Western: bracket.bracket.first_round?.Western || [] },
            conference_semifinals: { Western: bracket.bracket.conference_semifinals?.Western || {} },
            conference_finals: { Western: bracket.bracket.conference_finals?.Western || {} }
          }
        };
      }
      
      return bracket;
    } catch (error) {
      throw new Error(`Failed to get ${conference} conference bracket: ${error.message}`);
    }
  },

  // Simulate multiple tournaments and get aggregated results
  simulateMultipleTournaments: async (numSimulations = 10, tournamentSimulations = 1000) => {
    try {
      const simulations = [];
      
      for (let i = 0; i < numSimulations; i++) {
        const result = await predictionService.simulatePlayoffTournament(tournamentSimulations);
        simulations.push(result);
      }
      
      // Aggregate results
      const championCounts = {};
      let totalSimulations = 0;
      
      simulations.forEach(sim => {
        const champProbs = sim.tournament_simulation?.champion_probabilities || [];
        totalSimulations += sim.tournament_simulation?.simulations_run || 0;
        
        champProbs.forEach(({ team, probability }) => {
          championCounts[team] = (championCounts[team] || 0) + probability;
        });
      });
      
      // Convert to final probabilities
      const finalOdds = Object.entries(championCounts)
        .map(([team, totalProb]) => ({
          team,
          probability: totalProb / numSimulations
        }))
        .sort((a, b) => b.probability - a.probability);
      
      return {
        aggregated_results: {
          total_tournament_simulations: numSimulations,
          total_game_simulations: totalSimulations,
          final_championship_odds: finalOdds,
          most_likely_champion: finalOdds[0] || null
        },
        individual_simulations: simulations,
        generated_at: new Date().toISOString()
      };
      
    } catch (error) {
      throw new Error(`Failed to simulate multiple tournaments: ${error.message}`);
    }
  }
};