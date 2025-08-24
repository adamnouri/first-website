import { useState, useEffect, useCallback } from 'react';

const HISTORY_STORAGE_KEY = 'nba_prediction_history';
const MAX_HISTORY_ITEMS = 1000;

export const useLocalStorageHistory = (initialPage = 0, initialSize = 20) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [allPredictions, setAllPredictions] = useState([]);
  const [currentPage, setCurrentPage] = useState(initialPage);
  const [pageSize, setPageSize] = useState(initialSize);
  const [filters, setFilters] = useState({
    startDate: null,
    endDate: null,
    teamId: null,
    accuracyFilter: null
  });

  // Load predictions from localStorage
  const loadPredictions = useCallback(() => {
    try {
      setLoading(true);
      const stored = localStorage.getItem(HISTORY_STORAGE_KEY);
      const predictions = stored ? JSON.parse(stored) : [];
      setAllPredictions(predictions);
      setError(null);
    } catch (err) {
      setError('Failed to load prediction history');
      setAllPredictions([]);
    } finally {
      setLoading(false);
    }
  }, []);

  // Save predictions to localStorage
  const savePredictions = useCallback((predictions) => {
    try {
      // Keep only the most recent predictions to avoid storage bloat
      const trimmed = predictions.slice(0, MAX_HISTORY_ITEMS);
      localStorage.setItem(HISTORY_STORAGE_KEY, JSON.stringify(trimmed));
      setAllPredictions(trimmed);
    } catch (err) {
      console.error('Failed to save prediction history:', err);
    }
  }, []);

  // Add a new prediction to history
  const addPrediction = useCallback((prediction) => {
    const newPrediction = {
      id: Date.now() + Math.random(), // Simple unique ID
      predictionGeneratedAt: new Date().toISOString(),
      gameDate: prediction.gameDate || new Date().toISOString(),
      team1Id: prediction.team1Id,
      team2Id: prediction.team2Id,
      team1Name: prediction.team1Name,
      team2Name: prediction.team2Name,
      predictedWinnerId: prediction.predictedWinnerId,
      predictedWinnerName: prediction.predictedWinnerName,
      team1PredictedScore: prediction.team1PredictedScore,
      team2PredictedScore: prediction.team2PredictedScore,
      confidencePercentage: prediction.confidencePercentage || 75,
      predictionAccuracy: null, // Will be updated when actual result is known
      actualWinnerId: null,
      actualTeam1Score: null,
      actualTeam2Score: null,
      s3ChartPath: prediction.s3ChartPath || null, // S3 chart URL for visualization
      ...prediction
    };

    const updated = [newPrediction, ...allPredictions];
    savePredictions(updated);
  }, [allPredictions, savePredictions]);

  // Update prediction with actual results
  const updatePredictionResult = useCallback((predictionId, actualResult) => {
    const updated = allPredictions.map(prediction => {
      if (prediction.id === predictionId) {
        return {
          ...prediction,
          actualWinnerId: actualResult.winnerId,
          actualTeam1Score: actualResult.team1Score,
          actualTeam2Score: actualResult.team2Score,
          predictionAccuracy: prediction.predictedWinnerId === actualResult.winnerId
        };
      }
      return prediction;
    });
    savePredictions(updated);
  }, [allPredictions, savePredictions]);

  // Filter predictions based on current filters
  const getFilteredPredictions = useCallback(() => {
    let filtered = [...allPredictions];

    // Date range filter
    if (filters.startDate || filters.endDate) {
      filtered = filtered.filter(prediction => {
        const predDate = new Date(prediction.gameDate || prediction.predictionGeneratedAt);
        const startDate = filters.startDate ? new Date(filters.startDate) : null;
        const endDate = filters.endDate ? new Date(filters.endDate) : null;

        if (startDate && predDate < startDate) return false;
        if (endDate && predDate > endDate) return false;
        return true;
      });
    }

    // Team filter
    if (filters.teamId) {
      filtered = filtered.filter(prediction => 
        prediction.team1Id === parseInt(filters.teamId) || 
        prediction.team2Id === parseInt(filters.teamId)
      );
    }

    // Accuracy filter
    if (filters.accuracyFilter) {
      filtered = filtered.filter(prediction => {
        if (filters.accuracyFilter === 'accurate') {
          return prediction.predictionAccuracy === true;
        }
        if (filters.accuracyFilter === 'inaccurate') {
          return prediction.predictionAccuracy === false;
        }
        return true;
      });
    }

    return filtered;
  }, [allPredictions, filters]);

  // Get paginated predictions
  const getPaginatedPredictions = useCallback(() => {
    const filtered = getFilteredPredictions();
    const startIndex = currentPage * pageSize;
    const endIndex = startIndex + pageSize;
    
    return {
      predictions: filtered.slice(startIndex, endIndex),
      totalElements: filtered.length,
      totalPages: Math.ceil(filtered.length / pageSize)
    };
  }, [getFilteredPredictions, currentPage, pageSize]);

  // Initialize on mount
  useEffect(() => {
    loadPredictions();
  }, [loadPredictions]);

  const goToPage = useCallback((page) => {
    const { totalPages } = getPaginatedPredictions();
    if (page >= 0 && page < totalPages) {
      setCurrentPage(page);
    }
  }, [getPaginatedPredictions]);

  const changePageSize = useCallback((size) => {
    setPageSize(size);
    setCurrentPage(0); // Reset to first page
  }, []);

  const updateFilters = useCallback((newFilters) => {
    setFilters(prev => ({ ...prev, ...newFilters }));
    setCurrentPage(0); // Reset to first page when filters change
  }, []);

  const clearFilters = useCallback(() => {
    setFilters({
      startDate: null,
      endDate: null,
      teamId: null,
      accuracyFilter: null
    });
    setCurrentPage(0);
  }, []);

  const refreshHistory = useCallback(() => {
    loadPredictions();
  }, [loadPredictions]);

  const clearAllHistory = useCallback(() => {
    localStorage.removeItem(HISTORY_STORAGE_KEY);
    setAllPredictions([]);
    setCurrentPage(0);
  }, []);

  const { predictions, totalElements, totalPages } = getPaginatedPredictions();

  return {
    loading,
    error,
    predictions,
    totalElements,
    totalPages,
    currentPage,
    pageSize,
    filters,
    goToPage,
    changePageSize,
    updateFilters,
    clearFilters,
    refreshHistory,
    hasNextPage: currentPage < totalPages - 1,
    hasPreviousPage: currentPage > 0,
    // Additional methods for localStorage management
    addPrediction,
    updatePredictionResult,
    clearAllHistory
  };
};