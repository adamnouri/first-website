import { useState, useCallback } from 'react';

export const usePredictionChart = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [chartUrl, setChartUrl] = useState(null);
  const [chartLoaded, setChartLoaded] = useState(false);

  const loadChart = useCallback(async (s3ChartUrl) => {
    if (!s3ChartUrl) {
      setError('No chart URL provided');
      return;
    }

    try {
      setLoading(true);
      setError(null);
      setChartLoaded(false);
      
      // Pre-load the image to check if it's accessible
      const img = new Image();
      
      return new Promise((resolve, reject) => {
        img.onload = () => {
          setChartUrl(s3ChartUrl);
          setChartLoaded(true);
          setLoading(false);
          resolve(s3ChartUrl);
        };
        
        img.onerror = () => {
          setError('Failed to load chart image');
          setLoading(false);
          reject(new Error('Chart image failed to load'));
        };
        
        img.src = s3ChartUrl;
      });
    } catch (err) {
      setError(err.message);
      setLoading(false);
      throw err;
    }
  }, []);

  const clearChart = useCallback(() => {
    setChartUrl(null);
    setChartLoaded(false);
    setError(null);
  }, []);

  const retryLoadChart = useCallback((s3ChartUrl) => {
    return loadChart(s3ChartUrl);
  }, [loadChart]);

  return {
    loading,
    error,
    chartUrl,
    chartLoaded,
    loadChart,
    clearChart,
    retryLoadChart
  };
};