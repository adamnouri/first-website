import { useState, useEffect, useCallback } from 'react';
import { predictionService } from '../services/predictionService';

export const useAnalytics = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [accuracyStats, setAccuracyStats] = useState(null);
  const [modelInfo, setModelInfo] = useState(null);
  const [teamRankings, setTeamRankings] = useState([]);
  const [stalePredictions, setStalePredictions] = useState([]);

  const fetchAccuracyStats = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const result = await predictionService.getModelAccuracy();
      setAccuracyStats(result);
      return result;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const fetchModelInfo = useCallback(async () => {
    try {
      const result = await predictionService.getModelInfo();
      setModelInfo(result);
      return result;
    } catch (err) {
      console.warn('Failed to fetch model info:', err.message);
      return null;
    }
  }, []);

  const fetchTeamRankings = useCallback(async () => {
    try {
      const result = await predictionService.getTeamRankings();
      setTeamRankings(result.rankings || []);
      return result;
    } catch (err) {
      console.warn('Failed to fetch team rankings:', err.message);
      return null;
    }
  }, []);

  const fetchStalePredictions = useCallback(async (staleDays = 7) => {
    try {
      const result = await predictionService.getStalePredictions(staleDays);
      setStalePredictions(result.predictions || []);
      return result;
    } catch (err) {
      console.warn('Failed to fetch stale predictions:', err.message);
      return null;
    }
  }, []);

  const fetchAllAnalytics = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Fetch all analytics data concurrently
      const [accuracyResult, modelResult, rankingsResult, staleResult] = await Promise.allSettled([
        fetchAccuracyStats(),
        fetchModelInfo(),
        fetchTeamRankings(),
        fetchStalePredictions()
      ]);

      // Handle results and set states
      if (accuracyResult.status === 'fulfilled') {
        setAccuracyStats(accuracyResult.value);
      }
      
      if (modelResult.status === 'fulfilled') {
        setModelInfo(modelResult.value);
      }
      
      if (rankingsResult.status === 'fulfilled') {
        setTeamRankings(rankingsResult.value?.rankings || []);
      }
      
      if (staleResult.status === 'fulfilled') {
        setStalePredictions(staleResult.value?.predictions || []);
      }

      // If the main accuracy stats failed, throw error
      if (accuracyResult.status === 'rejected') {
        throw new Error(accuracyResult.reason?.message || 'Failed to fetch analytics');
      }

    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, [fetchAccuracyStats, fetchModelInfo, fetchTeamRankings, fetchStalePredictions]);

  const triggerModelRetrain = useCallback(async () => {
    try {
      setLoading(true);
      const result = await predictionService.triggerModelRetrain();
      // Refresh analytics after retrain
      await fetchAllAnalytics();
      return result;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, [fetchAllAnalytics]);

  const checkServiceHealth = useCallback(async () => {
    try {
      const [predictionHealth, mlHealth] = await Promise.allSettled([
        predictionService.checkPredictionServiceHealth(),
        predictionService.checkMLServiceHealth()
      ]);

      return {
        predictionService: predictionHealth.status === 'fulfilled' ? 'healthy' : 'unhealthy',
        mlService: mlHealth.status === 'fulfilled' ? 'healthy' : 'unhealthy',
        details: {
          predictionService: predictionHealth.value || predictionHealth.reason?.message,
          mlService: mlHealth.value || mlHealth.reason?.message
        }
      };
    } catch (err) {
      return {
        predictionService: 'unhealthy',
        mlService: 'unhealthy',
        error: err.message
      };
    }
  }, []);

  // Load initial analytics data
  useEffect(() => {
    fetchAllAnalytics();
  }, [fetchAllAnalytics]);

  // Calculate derived metrics
  const derivedMetrics = {
    accuracyPercentage: accuracyStats?.overallAccuracy || 0,
    totalPredictions: accuracyStats?.totalPredictions || 0,
    completedPredictions: accuracyStats?.completedPredictions || 0,
    pendingPredictions: accuracyStats?.pendingPredictions || 0,
    staleCount: stalePredictions.length,
    modelVersion: modelInfo?.model_version || 'Unknown',
    isModelTrained: modelInfo?.is_trained || false,
    completionRate: accuracyStats?.totalPredictions > 0 
      ? ((accuracyStats.completedPredictions / accuracyStats.totalPredictions) * 100).toFixed(1)
      : 0
  };

  return {
    loading,
    error,
    accuracyStats,
    modelInfo,
    teamRankings,
    stalePredictions,
    derivedMetrics,
    fetchAllAnalytics,
    fetchAccuracyStats,
    fetchModelInfo,
    fetchTeamRankings,
    fetchStalePredictions,
    triggerModelRetrain,
    checkServiceHealth
  };
};