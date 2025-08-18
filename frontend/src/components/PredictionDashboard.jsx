import React, { useState , useEffect} from 'react';
import {Chart as ChartJS, CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend, ArcElement, PointElement, LineElement, RadialLinearScale,} from 'chart.js';
import { Bar, Doughnut, Line, Radar } from 'react-chartjs-2';
import './PredictionDashboard.css';

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
  PointElement,
  LineElement,
  RadialLinearScale
);

const PredictionDashboard = () => {
  const [prediction, setPrediction] = useState(null);
  const [chartData, setChartData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [team1Id, setTeam1Id] = useState('1');
  const [team2Id, setTeam2Id] = useState('2');

  const makePrediction = async () => {
    if (team1Id === team2Id) {
      setError('Please select different teams');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await fetch('http://localhost:5000/predict', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          team1_id: parseInt(team1Id),
          team2_id: parseInt(team2Id),
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to get prediction');
      }

      const data = await response.json();
      setPrediction(data.prediction);
      setChartData(data.chart_data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const ConfidenceGauge = ({ confidence }) => {
    const percentage = Math.round(confidence * 100);
    const color = confidence >= 0.8 ? '#10B981' : confidence >= 0.6 ? '#F59E0B' : '#EF4444';
    
    return (
      <div className="confidence-gauge">
        <div className="gauge-container">
          <svg width="200" height="120" viewBox="0 0 200 120">
            <path
              d="M 20 100 A 80 80 0 0 1 180 100"
              stroke="#E5E7EB"
              strokeWidth="8"
              fill="none"
            />
            <path
              d="M 20 100 A 80 80 0 0 1 180 100"
              stroke={color}
              strokeWidth="8"
              fill="none"
              strokeDasharray={`${percentage * 2.51} 251`}
              strokeLinecap="round"
            />
          </svg>
          <div className="gauge-text">
            <div className="gauge-percentage">{percentage}%</div>
            <div className="gauge-label">Confidence</div>
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="prediction-dashboard">
      <div className="dashboard-header">
        <h1>NBA Game Prediction Dashboard</h1>
        <p>AI-powered basketball game outcome predictions with detailed analytics</p>
      </div>

      <div className="prediction-form">
        <div className="form-group">
          <label htmlFor="team1">Team 1 ID:</label>
          <input
            type="number"
            id="team1"
            value={team1Id}
            onChange={(e) => setTeam1Id(e.target.value)}
            min="1"
            max="30"
          />
        </div>
        <div className="form-group">
          <label htmlFor="team2">Team 2 ID:</label>
          <input
            type="number"
            id="team2"
            value={team2Id}
            onChange={(e) => setTeam2Id(e.target.value)}
            min="1"
            max="30"
          />
        </div>
        <button 
          onClick={makePrediction} 
          disabled={loading}
          className="predict-button"
        >
          {loading ? 'Predicting...' : 'Get Prediction'}
        </button>
      </div>

      {error && (
        <div className="error-message">
          <p>Error: {error}</p>
        </div>
      )}

      {prediction && (
        <div className="prediction-results">
          <div className="prediction-summary">
            <h2>Prediction Results</h2>
            <div className="summary-cards">
              <div className="summary-card winner">
                <h3>Predicted Winner</h3>
                <p>Team {prediction.winner_team_id}</p>
              </div>
              <div className="summary-card score">
                <h3>Predicted Score</h3>
                <p>
                  Team {team1Id}: {prediction.team1_predicted_score} | 
                  Team {team2Id}: {prediction.team2_predicted_score}
                </p>
              </div>
            </div>
          </div>

          <div className="confidence-section">
            <ConfidenceGauge confidence={prediction.confidence} />
          </div>
        </div>
      )}

      {chartData && (
        <div className="charts-container">
          <div className="chart-grid">
            <div className="chart-item">
              <h3>Predicted Score Comparison</h3>
              <Bar data={chartData.score_comparison.data} options={chartData.score_comparison.options} />
            </div>

            <div className="chart-item">
              <h3>Win Probability</h3>
              <Doughnut data={chartData.win_probability.data} options={chartData.win_probability.options} />
            </div>

            <div className="chart-item">
              <h3>Team Performance Comparison</h3>
              <Radar data={chartData.team_comparison.data} options={chartData.team_comparison.options} />
            </div>

            <div className="chart-item">
              <h3>Recent Performance Trend</h3>
              <Line data={chartData.trend_analysis.data} options={chartData.trend_analysis.options} />
            </div>
          </div>
        </div>
      )}

      <div className="dashboard-footer">
        <p>Powered by AI machine learning algorithms and real-time NBA statistics</p>
      </div>
    </div>
  );
};

export default PredictionDashboard;