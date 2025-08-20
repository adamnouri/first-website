import { Bar } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
} from 'chart.js';

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
);

const ScoreComparison = ({ 
  team1Name = 'Team 1', 
  team2Name = 'Team 2', 
  team1Score = 105, 
  team2Score = 102,
  height = 300
}) => {
  const winnerColor = team1Score > team2Score ? '#10B981' : '#EF4444';
  const loserColor = team1Score > team2Score ? '#EF4444' : '#10B981';

  const data = {
    labels: [team1Name, team2Name],
    datasets: [{
      label: 'Predicted Score',
      data: [team1Score, team2Score],
      backgroundColor: [
        team1Score > team2Score ? winnerColor : loserColor,
        team2Score > team1Score ? winnerColor : loserColor
      ],
      borderColor: [
        team1Score > team2Score ? '#059669' : '#DC2626',
        team2Score > team1Score ? '#059669' : '#DC2626'
      ],
      borderWidth: 2,
      borderRadius: 4,
      borderSkipped: false
    }]
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: false
      },
      title: {
        display: true,
        text: 'Predicted Final Scores',
        font: {
          size: 16,
          weight: 'bold'
        },
        color: '#111827'
      },
      tooltip: {
        backgroundColor: 'rgba(0, 0, 0, 0.8)',
        titleColor: 'white',
        bodyColor: 'white',
        borderColor: '#E5E7EB',
        borderWidth: 1,
        callbacks: {
          label: function(context) {
            return `Predicted Score: ${context.parsed.y} points`;
          }
        }
      }
    },
    scales: {
      y: {
        beginAtZero: true,
        min: 80,
        max: 130,
        grid: {
          color: '#F3F4F6'
        },
        ticks: {
          color: '#6B7280',
          font: {
            size: 12
          }
        }
      },
      x: {
        grid: {
          display: false
        },
        ticks: {
          color: '#374151',
          font: {
            size: 12,
            weight: 'bold'
          },
          maxRotation: 0
        }
      }
    },
    animation: {
      duration: 1000,
      easing: 'easeOutQuart'
    }
  };

  return (
    <div className="score-comparison-chart" style={{ height }}>
      <Bar data={data} options={options} />
      <div className="score-summary">
        <div className="score-difference">
          <span className="difference-label">Predicted Margin:</span>
          <span className="difference-value">
            {Math.abs(team1Score - team2Score)} points
          </span>
        </div>
      </div>
    </div>
  );
};

export default ScoreComparison;