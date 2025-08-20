import { useState } from 'react';
import { usePredictionChart } from '../../hooks/usePredictionChart';
import LoadingSpinner from '../common/LoadingSpinner';
import ErrorMessage from '../common/ErrorMessage';

const PredictionChart = ({ 
  chartUrl, 
  altText = 'Prediction Chart',
  className = '',
  onImageClick = null,
  showRetry = true
}) => {
  const { loading, error, chartLoaded, loadChart, retryLoadChart } = usePredictionChart();
  const [imageError, setImageError] = useState(false);

  const handleImageLoad = () => {
    setImageError(false);
  };

  const handleImageError = () => {
    setImageError(true);
  };

  const handleRetry = () => {
    setImageError(false);
    if (chartUrl) {
      retryLoadChart(chartUrl);
    }
  };

  if (!chartUrl) {
    return (
      <div className={`prediction-chart-placeholder ${className}`}>
        <div className="placeholder-content">
          <div className="placeholder-icon">📊</div>
          <p className="placeholder-text">No chart available</p>
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className={`prediction-chart-loading ${className}`}>
        <LoadingSpinner size="lg" />
        <p className="loading-text">Loading prediction chart...</p>
      </div>
    );
  }

  if (error || imageError) {
    return (
      <div className={`prediction-chart-error ${className}`}>
        <ErrorMessage 
          message={error || 'Failed to load chart image'}
          onRetry={showRetry ? handleRetry : null}
        />
      </div>
    );
  }

  return (
    <div className={`prediction-chart ${className}`}>
      <div className="chart-container">
        <img
          src={chartUrl}
          alt={altText}
          className="chart-image"
          onLoad={handleImageLoad}
          onError={handleImageError}
          onClick={onImageClick}
          style={{ 
            cursor: onImageClick ? 'pointer' : 'default',
            maxWidth: '100%',
            height: 'auto',
            borderRadius: '8px',
            boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
          }}
        />
        {onImageClick && (
          <div className="chart-overlay">
            <span className="chart-expand-hint">Click to expand</span>
          </div>
        )}
      </div>
    </div>
  );
};

export default PredictionChart;