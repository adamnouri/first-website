import { Radar } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  RadialLinearScale,
  PointElement,
  LineElement,
  Filler,
  Tooltip,
  Legend
} from 'chart.js';

ChartJS.register(
  RadialLinearScale,
  PointElement,
  LineElement,
  Filler,
  Tooltip,
  Legend
);

const TeamRadarChart = ({ 
  team1Name = 'Team 1', 
  team2Name = 'Team 2', 
  team1Stats = {},
  team2Stats = {},
  height = 400
}) => {
  // Default stats if not provided
  const defaultStats = {
    offense: 75,
    defense: 70,
    rebounding: 65,
    threePoint: 72,
    freeThrows: 78,
    turnovers: 68
  };

  const team1Data = { ...defaultStats, ...team1Stats };
  const team2Data = { ...defaultStats, ...team2Stats };

  const categories = [
    'Offense',
    'Defense', 
    'Rebounding',
    '3-Point %',
    'Free Throws',
    'Turnover Control'
  ];

  const data = {
    labels: categories,
    datasets: [
      {
        label: team1Name,
        data: [
          team1Data.offense,
          team1Data.defense,
          team1Data.rebounding,
          team1Data.threePoint,
          team1Data.freeThrows,
          team1Data.turnovers
        ],
        backgroundColor: 'rgba(59, 130, 246, 0.2)',
        borderColor: '#3B82F6',
        pointBackgroundColor: '#3B82F6',
        pointBorderColor: '#ffffff',
        pointBorderWidth: 2,
        pointRadius: 5,
        borderWidth: 2
      },
      {
        label: team2Name,
        data: [
          team2Data.offense,
          team2Data.defense,
          team2Data.rebounding,
          team2Data.threePoint,
          team2Data.freeThrows,
          team2Data.turnovers
        ],
        backgroundColor: 'rgba(239, 68, 68, 0.2)',
        borderColor: '#EF4444',
        pointBackgroundColor: '#EF4444',
        pointBorderColor: '#ffffff',
        pointBorderWidth: 2,
        pointRadius: 5,
        borderWidth: 2
      }
    ]
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      title: {
        display: true,
        text: 'Team Performance Comparison',
        font: {
          size: 16,
          weight: 'bold'
        },
        color: '#111827'
      },
      legend: {
        position: 'bottom',
        labels: {
          font: {
            size: 12
          },
          color: '#374151',
          usePointStyle: true,
          padding: 20
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
            return `${context.dataset.label}: ${context.parsed.r}/100`;
          }
        }
      }
    },
    scales: {
      r: {
        beginAtZero: true,
        min: 0,
        max: 100,
        ticks: {
          stepSize: 20,
          color: '#6B7280',
          font: {
            size: 10
          }
        },
        grid: {
          color: '#E5E7EB'
        },
        angleLines: {
          color: '#E5E7EB'
        },
        pointLabels: {
          color: '#374151',
          font: {
            size: 11,
            weight: 'bold'
          }
        }
      }
    },
    animation: {
      duration: 1500,
      easing: 'easeOutQuart'
    }
  };

  return (
    <div className="team-radar-chart" style={{ height }}>
      <Radar data={data} options={options} />
      <div className="radar-legend">
        <div className="legend-item">
          <div className="legend-color team1"></div>
          <span>{team1Name}</span>
        </div>
        <div className="legend-item">
          <div className="legend-color team2"></div>
          <span>{team2Name}</span>
        </div>
      </div>
    </div>
  );
};

export default TeamRadarChart;