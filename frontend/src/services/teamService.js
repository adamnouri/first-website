import { apiClient } from './api';

export const teamService = {
  getAllTeams: async () => {
    try {
      const response = await apiClient.get('/api/v1/teams');
      return response.data;
    } catch (error) {
      throw new Error('Failed to fetch teams');
    }
  },

  getTeamById: async (id) => {
    try {
      const response = await apiClient.get(`/api/v1/teams/${id}`);
      return response.data;
    } catch (error) {
      throw new Error(`Failed to fetch team with ID ${id}`);
    }
  },

  getTeamByNbaApiId: async (nbaApiId) => {
    try {
      const response = await apiClient.get(`/api/v1/teams/nba-api/${nbaApiId}`);
      return response.data;
    } catch (error) {
      throw new Error(`Failed to fetch team with NBA API ID ${nbaApiId}`);
    }
  },

  getTeamStats: async (teamId) => {
    try {
      const response = await apiClient.get(`/api/v1/teams/${teamId}/stats`);
      return response.data;
    } catch (error) {
      throw new Error(`Failed to fetch stats for team ${teamId}`);
    }
  }
};