import { useState, useCallback } from 'react';
import { predictionService } from '../services/predictionService';

export const usePredictions = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [prediction, setPrediction] = useState(null);
  const [upcomingPredictions, setUpcomingPredictions] = useState([]);

  // Get prediction for specific matchup
  const getPredictionForMatchup = useCallback(async (team1Id, team2Id) => {
    try {
      setLoading(true);
      setError(null);
      const result = await predictionService.getPredictionForMatchup(team1Id, team2Id);
      setPrediction(result);
      return result;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  // Generate real-time prediction as fallback
  const generateRealTimePrediction = useCallback(async (team1Id, team2Id, gameDate) => {
    try {
      setLoading(true);
      setError(null);
      const result = await predictionService.generateRealTimePrediction(team1Id, team2Id, gameDate);
      setPrediction(result);
      return result;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  // Get upcoming predictions
  const fetchUpcomingPredictions = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const result = await predictionService.getUpcomingPredictions();
      setUpcomingPredictions(result.predictions || []);
      return result;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  // Clear current prediction
  const clearPrediction = useCallback(() => {
    setPrediction(null);
    setError(null);
  }, []);

  // Retry last prediction request
  const retryPrediction = useCallback(async () => {
    if (prediction?.team1_id && prediction?.team2_id) {
      return getPredictionForMatchup(prediction.team1_id, prediction.team2_id);
    }
  }, [prediction, getPredictionForMatchup]);

  return {
    loading,
    error,
    prediction,
    upcomingPredictions,
    getPredictionForMatchup,
    generateRealTimePrediction,
    fetchUpcomingPredictions,
    clearPrediction,
    retryPrediction
  };
};