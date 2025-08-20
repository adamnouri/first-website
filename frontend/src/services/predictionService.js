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
  }
};