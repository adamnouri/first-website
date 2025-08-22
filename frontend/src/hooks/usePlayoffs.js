import { useState, useEffect, useCallback } from 'react';
import { predictionService } from '../services/predictionService';

/**
 * Custom hook for managing playoff predictions and state
 * Integrates with existing prediction service architecture
 */
export const usePlayoffs = () => {
  // State management
  const [standings, setStandings] = useState({ Eastern: [], Western: [] });
  const [bracket, setBracket] = useState(null);
  const [championshipOdds, setChampionshipOdds] = useState([]);
  const [loading, setLoading] = useState({
    standings: false,
    bracket: false,
    odds: false,
    series: false,
    tournament: false
  });
  const [errors, setErrors] = useState({});
  const [lastUpdated, setLastUpdated] = useState({});

  // Update loading state for specific operation
  const updateLoading = useCallback((operation, isLoading) => {
    setLoading(prev => ({ ...prev, [operation]: isLoading }));
  }, []);

  // Update error state
  const updateError = useCallback((operation, error) => {
    setErrors(prev => ({ ...prev, [operation]: error }));
  }, []);

  // Update last updated timestamp
  const updateTimestamp = useCallback((operation) => {
    setLastUpdated(prev => ({ ...prev, [operation]: new Date().toISOString() }));
  }, []);

  // Fetch conference standings
  const fetchStandings = useCallback(async (conference = 'both', simulations = 1000, forceRefresh = false) => {
    if (loading.standings && !forceRefresh) return;

    updateLoading('standings', true);
    updateError('standings', null);

    try {
      const response = await predictionService.getConferenceStandings(conference, simulations);
      
      if (response.status === 'success') {
        setStandings(response.standings);
        updateTimestamp('standings');
      } else {
        throw new Error('Failed to fetch standings');
      }
    } catch (error) {
      console.error('Error fetching standings:', error);
      updateError('standings', error.message);
    } finally {
      updateLoading('standings', false);
    }
  }, [loading.standings, updateLoading, updateError, updateTimestamp]);

  // Fetch playoff bracket
  const fetchBracket = useCallback(async (useCached = false, forceRefresh = false) => {
    if (loading.bracket && !forceRefresh) return;

    updateLoading('bracket', true);
    updateError('bracket', null);

    try {
      const response = await predictionService.generatePlayoffBracket(useCached);
      
      if (response.status === 'success') {
        setBracket(response.bracket);
        updateTimestamp('bracket');
      } else {
        throw new Error('Failed to generate bracket');
      }
    } catch (error) {
      console.error('Error fetching bracket:', error);
      updateError('bracket', error.message);
    } finally {
      updateLoading('bracket', false);
    }
  }, [loading.bracket, updateLoading, updateError, updateTimestamp]);

  // Fetch championship odds
  const fetchChampionshipOdds = useCallback(async (simulations = 5000, forceRefresh = false) => {
    if (loading.odds && !forceRefresh) return;

    updateLoading('odds', true);
    updateError('odds', null);

    try {
      const response = await predictionService.getChampionshipOdds(simulations);
      
      if (response.status === 'success') {
        setChampionshipOdds(response.odds.championship_odds || []);
        updateTimestamp('odds');
      } else {
        throw new Error('Failed to fetch championship odds');
      }
    } catch (error) {
      console.error('Error fetching championship odds:', error);
      updateError('odds', error.message);
    } finally {
      updateLoading('odds', false);
    }
  }, [loading.odds, updateLoading, updateError, updateTimestamp]);

  // Predict playoff series
  const predictSeries = useCallback(async (team1Id, team2Id, round = 'first_round', seriesLength = 7) => {
    updateLoading('series', true);
    updateError('series', null);

    try {
      const response = await predictionService.predictPlayoffSeries(team1Id, team2Id, round, seriesLength);
      
      if (response.status === 'success') {
        updateTimestamp('series');
        return response;
      } else {
        throw new Error('Failed to predict series');
      }
    } catch (error) {
      console.error('Error predicting series:', error);
      updateError('series', error.message);
      throw error;
    } finally {
      updateLoading('series', false);
    }
  }, [updateLoading, updateError, updateTimestamp]);

  // Simulate tournament
  const simulateTournament = useCallback(async (simulations = 1000, standings = null, includePlayIn = true) => {
    updateLoading('tournament', true);
    updateError('tournament', null);

    try {
      const response = await predictionService.simulatePlayoffTournament(simulations, standings, includePlayIn);
      
      if (response.status === 'success') {
        updateTimestamp('tournament');
        return response;
      } else {
        throw new Error('Failed to simulate tournament');
      }
    } catch (error) {
      console.error('Error simulating tournament:', error);
      updateError('tournament', error.message);
      throw error;
    } finally {
      updateLoading('tournament', false);
    }
  }, [updateLoading, updateError, updateTimestamp]);

  // Get team-specific playoff odds
  const getTeamOdds = useCallback(async (teamId) => {
    try {
      const response = await predictionService.getTeamPlayoffOdds(teamId);
      
      if (response.status === 'success') {
        return response;
      } else {
        throw new Error('Failed to get team odds');
      }
    } catch (error) {
      console.error('Error getting team odds:', error);
      throw error;
    }
  }, []);

  // Refresh all playoff data
  const refreshAllData = useCallback(async () => {
    const promises = [
      fetchStandings('both', 1000, true),
      fetchBracket(false, true),
      fetchChampionshipOdds(5000, true)
    ];

    try {
      await Promise.allSettled(promises);
    } catch (error) {
      console.error('Error refreshing playoff data:', error);
    }
  }, [fetchStandings, fetchBracket, fetchChampionshipOdds]);

  // Initial data fetch on mount
  useEffect(() => {
    // Only fetch if data is not already loaded
    if (standings.Eastern.length === 0 && standings.Western.length === 0) {
      fetchStandings();
    }
    
    if (!bracket) {
      fetchBracket();
    }
    
    if (championshipOdds.length === 0) {
      fetchChampionshipOdds();
    }
  }, [fetchStandings, fetchBracket, fetchChampionshipOdds, standings.Eastern.length, standings.Western.length, bracket, championshipOdds.length]);

  // Utility functions
  const getTopTeams = useCallback((conference, count = 8) => {
    const conferenceStandings = standings[conference] || [];
    return conferenceStandings.slice(0, count);
  }, [standings]);

  const getPlayoffTeams = useCallback(() => {
    return {
      Eastern: getTopTeams('Eastern', 10), // Top 10 make play-in
      Western: getTopTeams('Western', 10)
    };
  }, [getTopTeams]);

  const getTeamByRank = useCallback((conference, rank) => {
    const conferenceStandings = standings[conference] || [];
    return conferenceStandings.find(team => team.rank === rank);
  }, [standings]);

  const isDataFresh = useCallback((operation, maxAgeMinutes = 30) => {
    const timestamp = lastUpdated[operation];
    if (!timestamp) return false;
    
    const age = (Date.now() - new Date(timestamp).getTime()) / (1000 * 60);
    return age < maxAgeMinutes;
  }, [lastUpdated]);

  return {
    // State
    standings,
    bracket,
    championshipOdds,
    loading,
    errors,
    lastUpdated,

    // Actions
    fetchStandings,
    fetchBracket,
    fetchChampionshipOdds,
    predictSeries,
    simulateTournament,
    getTeamOdds,
    refreshAllData,

    // Utility functions
    getTopTeams,
    getPlayoffTeams,
    getTeamByRank,
    isDataFresh,

    // Computed properties
    hasStandings: standings.Eastern.length > 0 || standings.Western.length > 0,
    hasBracket: bracket !== null,
    hasChampionshipOdds: championshipOdds.length > 0,
    isLoading: Object.values(loading).some(Boolean),
    hasErrors: Object.keys(errors).length > 0,

    // Conference-specific helpers
    easternStandings: standings.Eastern || [],
    westernStandings: standings.Western || [],
    easternPlayoffTeams: getTopTeams('Eastern', 10),
    westernPlayoffTeams: getTopTeams('Western', 10),

    // Championship contenders (top teams by odds)
    topContenders: championshipOdds.slice(0, 10),
    favoritesToWin: championshipOdds.slice(0, 3)
  };
};

export default usePlayoffs;