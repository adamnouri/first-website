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
  const [teams, setTeams] = useState([]);
  const [teamsLoading, setTeamsLoading] = useState(true);
  const [team1Id, setTeam1Id] = useState('');
  const [team2Id, setTeam2Id] = useState('');

  // Load teams on component mount
  useEffect(() => {
    const fetchTeams = async () => {
      try {
        setTeamsLoading(true);
        const response = await fetch('http://localhost:5001/teams');
        if (response.ok) {
          const data = await response.json();
          setTeams(data.teams || []);
          // Set default teams if available
          if (data.teams && data.teams.length >= 2) {
            setTeam1Id(data.teams[0].nbaApiId.toString());
            setTeam2Id(data.teams[1].nbaApiId.toString());
          }
        } else {
          console.error('Failed to fetch teams');
        }
      } catch (err) {
        console.error('Error fetching teams:', err);
      } finally {
        setTeamsLoading(false);
      }
    };

    fetchTeams();
  }, []);

  const makePrediction = async () => {
    if (team1Id === team2Id) {
      setError('Please select different teams');
      return;
    }

    if (!team1Id || !team2Id) {
      setError('Please select both teams');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await fetch('http://localhost:5001/predict', {
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

  // Helper function to get team name by ID
  const getTeamById = (teamId) => {
    return teams.find(team => team.nbaApiId.toString() === teamId.toString());
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
          <label htmlFor="team1">Home Team:</label>
          {teamsLoading ? (
            <div className="loading-teams">Loading teams...</div>
          ) : (
            <select
              id="team1"
              value={team1Id}
              onChange={(e) => setTeam1Id(e.target.value)}
            >
              <option value="">Select home team</option>
              {teams.map((team) => (
                <option key={team.nbaApiId} value={team.nbaApiId}>
                  {team.fullName}
                </option>
              ))}
            </select>
          )}
        </div>
        <div className="form-group">
          <label htmlFor="team2">Away Team:</label>
          {teamsLoading ? (
            <div className="loading-teams">Loading teams...</div>
          ) : (
            <select
              id="team2"
              value={team2Id}
              onChange={(e) => setTeam2Id(e.target.value)}
            >
              <option value="">Select away team</option>
              {teams.map((team) => (
                <option key={team.nbaApiId} value={team.nbaApiId}>
                  {team.fullName}
                </option>
              ))}
            </select>
          )}
        </div>
        <button 
          onClick={makePrediction} 
          disabled={loading || teamsLoading || !team1Id || !team2Id}
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
                <p>
                  {prediction.winner_team_name || `Team ${prediction.winner_team_id}`}
                </p>
              </div>
              <div className="summary-card score">
                <h3>Predicted Score</h3>
                <p>
                  {prediction.teams ? (
                    <>
                      {prediction.teams.home.name}: {prediction.team1_predicted_score} | {' '}
                      {prediction.teams.away.name}: {prediction.team2_predicted_score}
                    </>
                  ) : (
                    <>
                      {getTeamById(team1Id)?.fullName || `Team ${team1Id}`}: {prediction.team1_predicted_score} | {' '}
                      {getTeamById(team2Id)?.fullName || `Team ${team2Id}`}: {prediction.team2_predicted_score}
                    </>
                  )}
                </p>
              </div>
            </div>
          </div>

          <div className="confidence-section">
            <ConfidenceGauge confidence={prediction.confidence} />
            {prediction.teams && (
              <div className="matchup-display">
                <h3>Matchup</h3>
                <div className="teams-display">
                  <div className="team home-team">
                    <span className="team-name">{prediction.teams.home.name}</span>
                    <span className="team-abbr">({prediction.teams.home.abbreviation})</span>
                  </div>
                  <span className="vs">VS</span>
                  <div className="team away-team">
                    <span className="team-name">{prediction.teams.away.name}</span>
                    <span className="team-abbr">({prediction.teams.away.abbreviation})</span>
                  </div>
                </div>
              </div>
            )}
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