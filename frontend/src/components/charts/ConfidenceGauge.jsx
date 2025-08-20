import { Doughnut } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  ArcElement,
  Tooltip,
  Legend
} from 'chart.js';

ChartJS.register(ArcElement, Tooltip, Legend);

const ConfidenceGauge = ({ confidence = 0.5, size = 200, showLabel = true }) => {
  const confidencePercentage = Math.round(confidence * 100);
  
  // Determine color based on confidence level
  const getConfidenceColor = (conf) => {
    if (conf >= 80) return '#10B981'; // Green
    if (conf >= 60) return '#F59E0B'; // Yellow
    return '#EF4444'; // Red
  };

  const confidenceColor = getConfidenceColor(confidencePercentage);
  const remainingPercentage = 100 - confidencePercentage;

  const data = {
    datasets: [{
      data: [confidencePercentage, remainingPercentage],
      backgroundColor: [confidenceColor, '#E5E7EB'],
      borderColor: [confidenceColor, '#E5E7EB'],
      borderWidth: 0,
      cutout: '70%',
      circumference: 180,
      rotation: 270
    }]
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: false
      },
      tooltip: {
        enabled: false
      }
    }
  };

  const getConfidenceLabel = (conf) => {
    if (conf >= 80) return 'High Confidence';
    if (conf >= 60) return 'Medium Confidence';
    return 'Low Confidence';
  };

  return (
    <div className="confidence-gauge" style={{ width: size, height: size / 2 + 40 }}>
      <div className="gauge-chart" style={{ height: size / 2, position: 'relative' }}>
        <Doughnut data={data} options={options} />
        <div className="gauge-center">
          <div className="confidence-value">
            {confidencePercentage}%
          </div>
          {showLabel && (
            <div className="confidence-label">
              {getConfidenceLabel(confidencePercentage)}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ConfidenceGauge;