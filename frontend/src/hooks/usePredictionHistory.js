import { useState, useEffect, useCallback } from 'react';
import { predictionService } from '../services/predictionService';

export const usePredictionHistory = (initialPage = 0, initialSize = 20) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [predictions, setPredictions] = useState([]);
  const [totalElements, setTotalElements] = useState(0);
  const [totalPages, setTotalPages] = useState(0);
  const [currentPage, setCurrentPage] = useState(initialPage);
  const [pageSize, setPageSize] = useState(initialSize);
  const [filters, setFilters] = useState({
    startDate: null,
    endDate: null,
    teamId: null,
    accuracyFilter: null // 'accurate', 'inaccurate', null for all
  });

  const fetchHistory = useCallback(async (page = currentPage, size = pageSize) => {
    try {
      setLoading(true);
      setError(null);
      
      let result;
      
      // Apply date range filter if set
      if (filters.startDate && filters.endDate) {
        result = await predictionService.getPredictionsInDateRange(
          filters.startDate, 
          filters.endDate
        );
        // For date range, we get all results, so we need to manually paginate
        const startIndex = page * size;
        const endIndex = startIndex + size;
        const paginatedPredictions = result.predictions.slice(startIndex, endIndex);
        
        setPredictions(paginatedPredictions);
        setTotalElements(result.predictions.length);
        setTotalPages(Math.ceil(result.predictions.length / size));
      } else if (filters.teamId) {
        // Team-specific predictions
        result = await predictionService.getPredictionsByTeam(filters.teamId, page, size);
        setPredictions(result.predictions || []);
        setTotalElements(result.totalElements || 0);
        setTotalPages(result.totalPages || 0);
      } else {
        // General prediction history
        result = await predictionService.getPredictionHistory(page, size);
        setPredictions(result.predictions || []);
        setTotalElements(result.totalElements || 0);
        setTotalPages(result.totalPages || 0);
      }
      
      setCurrentPage(page);
      return result;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, [currentPage, pageSize, filters]);

  // Load initial data
  useEffect(() => {
    fetchHistory();
  }, [fetchHistory]);

  const goToPage = useCallback((page) => {
    if (page >= 0 && page < totalPages) {
      fetchHistory(page, pageSize);
    }
  }, [fetchHistory, pageSize, totalPages]);

  const changePageSize = useCallback((size) => {
    setPageSize(size);
    fetchHistory(0, size); // Reset to first page with new size
  }, [fetchHistory]);

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
    return fetchHistory(currentPage, pageSize);
  }, [fetchHistory, currentPage, pageSize]);

  // Filter predictions by accuracy if accuracy filter is set
  const filteredPredictions = predictions.filter(prediction => {
    if (!filters.accuracyFilter) return true;
    
    if (filters.accuracyFilter === 'accurate') {
      return prediction.predictionAccuracy === true;
    }
    if (filters.accuracyFilter === 'inaccurate') {
      return prediction.predictionAccuracy === false;
    }
    
    return true;
  });

  return {
    loading,
    error,
    predictions: filteredPredictions,
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
    hasPreviousPage: currentPage > 0
  };
};