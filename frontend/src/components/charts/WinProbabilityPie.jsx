import { Doughnut } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  ArcElement,
  Tooltip,
  Legend
} from 'chart.js';

ChartJS.register(ArcElement, Tooltip, Legend);

const WinProbabilityPie = ({ 
  team1Name = 'Team 1',
  team2Name = 'Team 2',
  team1Probability = 0.6,
  team2Probability = 0.4,
  predictedWinner = null,
  height = 300
}) => {
  const team1Percentage = Math.round(team1Probability * 100);
  const team2Percentage = Math.round(team2Probability * 100);

  // Determine colors based on which team is favored
  const team1Color = team1Probability > team2Probability ? '#10B981' : '#F59E0B';
  const team2Color = team2Probability > team1Probability ? '#10B981' : '#F59E0B';

  const data = {
    labels: [
      `${team1Name} (${team1Percentage}%)`,
      `${team2Name} (${team2Percentage}%)`
    ],
    datasets: [{
      data: [team1Percentage, team2Percentage],
      backgroundColor: [team1Color, team2Color],
      borderColor: ['#ffffff', '#ffffff'],
      borderWidth: 3,
      hoverBackgroundColor: [
        team1Probability > team2Probability ? '#059669' : '#D97706',
        team2Probability > team1Probability ? '#059669' : '#D97706'
      ],
      hoverBorderWidth: 4
    }]
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    cutout: '50%',
    plugins: {
      title: {
        display: true,
        text: 'Win Probability',
        font: {
          size: 16,
          weight: 'bold'
        },
        color: '#111827',
        padding: {
          bottom: 20
        }
      },
      legend: {
        position: 'bottom',
        labels: {
          font: {
            size: 12
          },
          color: '#374151',
          usePointStyle: true,
          padding: 15,
          generateLabels: function(chart) {
            const data = chart.data;
            return data.labels.map((label, index) => ({
              text: label,
              fillStyle: data.datasets[0].backgroundColor[index],
              strokeStyle: data.datasets[0].borderColor[index],
              lineWidth: data.datasets[0].borderWidth,
              pointStyle: 'circle'
            }));
          }
        }
      },
      tooltip: {
        backgroundColor: 'rgba(0, 0, 0, 0.8)',
        titleColor: 'white',
        bodyColor: 'white',
        borderColor: '#E5E7EB',
        borderWidth: 1,
        callbacks: {
          label: function(context) {
            const label = context.label || '';
            return `${label} chance to win`;
          }
        }
      }
    },
    animation: {
      animateRotate: true,
      duration: 1500,
      easing: 'easeOutQuart'
    }
  };

  const favoriteTeam = team1Probability > team2Probability ? team1Name : team2Name;
  const favoritePercentage = Math.max(team1Percentage, team2Percentage);

  return (
    <div className="win-probability-chart" style={{ height }}>
      <Doughnut data={data} options={options} />
      
      {predictedWinner && (
        <div className="prediction-summary">
          <div className="favorite-indicator">
            <span className="favorite-label">Predicted Winner:</span>
            <span className="favorite-team">{predictedWinner}</span>
          </div>
          <div className="confidence-indicator">
            <span className="confidence-label">Confidence:</span>
            <span className="confidence-value">{favoritePercentage}%</span>
          </div>
        </div>
      )}
      
      <div className="probability-breakdown">
        <div className="team-probability">
          <div 
            className="probability-bar team1" 
            style={{ 
              width: `${team1Percentage}%`,
              backgroundColor: team1Color 
            }}
          ></div>
          <span className="team-label">{team1Name}: {team1Percentage}%</span>
        </div>
        <div className="team-probability">
          <div 
            className="probability-bar team2" 
            style={{ 
              width: `${team2Percentage}%`,
              backgroundColor: team2Color 
            }}
          ></div>
          <span className="team-label">{team2Name}: {team2Percentage}%</span>
        </div>
      </div>
    </div>
  );
};

export default WinProbabilityPie;