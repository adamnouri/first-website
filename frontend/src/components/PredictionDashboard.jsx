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
  
  // New state for S3 integration
  const [activeTab, setActiveTab] = useState('current'); // current, history, upcoming, accuracy
  const [predictionHistory, setPredictionHistory] = useState([]);
  const [upcomingPredictions, setUpcomingPredictions] = useState([]);
  const [modelAccuracy, setModelAccuracy] = useState(null);
  const [historyLoading, setHistoryLoading] = useState(false);
  const [predictionAge, setPredictionAge] = useState(null);
  const [chartImageUrl, setChartImageUrl] = useState(null);

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
    setPredictionAge(null);
    setChartImageUrl(null);

    try {
      // First, try to get pre-computed prediction from Spring Boot
      const springBootResponse = await fetch(
        `http://localhost:8080/api/v1/predictions/matchup?team1=${team1Id}&team2=${team2Id}`
      );

      if (springBootResponse.ok) {
        const springData = await springBootResponse.json();
        
        if (springData.status === 'found') {
          // Use pre-computed prediction
          const predictionData = springData.prediction;
          const s3Data = springData.s3Data || {};
          
          setPrediction({
            ...predictionData,
            ...s3Data.prediction,
            source: 'pre-computed',
            is_fresh: springData.isFresh
          });
          
          // Set prediction age info
          setPredictionAge({
            generated_at: predictionData.predictionGeneratedAt,
            is_fresh: springData.isFresh,
            stale_days: springData.staleDays
          });
          
          // Set chart image URL if available
          if (springData.chartUrl) {
            setChartImageUrl(springData.chartUrl);
          }
          
          // Generate fallback chart data for frontend charts
          const fallbackChartData = await generateFallbackChartData(springData);
          setChartData(fallbackChartData);
          
          return;
        }
      }

      // Fall back to ML service for real-time prediction
      const mlResponse = await fetch('http://localhost:5001/predict', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          team1_id: parseInt(team1Id),
          team2_id: parseInt(team2Id),
        }),
      });

      if (!mlResponse.ok) {
        throw new Error('Failed to get prediction from ML service');
      }

      const mlData = await mlResponse.json();
      setPrediction({
        ...mlData.prediction,
        source: 'real-time',
        is_fresh: true
      });
      setChartData(mlData.chart_data);
      
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const generateFallbackChartData = async (springData) => {
    // Generate basic chart data from Spring Boot prediction data
    const prediction = springData.prediction;
    const s3Data = springData.s3Data || {};
    
    return {
      confidence_chart: { data: { value: (prediction.confidencePercentage || 50) } },
      score_comparison: {
        data: {
          labels: [`Team ${prediction.team1Id}`, `Team ${prediction.team2Id}`],
          datasets: [{
            label: "Predicted Score",
            data: [prediction.team1PredictedScore || 105, prediction.team2PredictedScore || 105],
            backgroundColor: ["#3B82F6", "#EF4444"]
          }]
        },
        options: { responsive: true }
      },
      win_probability: {
        data: {
          labels: ["Winner", "Underdog"],
          datasets: [{
            data: [prediction.confidencePercentage || 50, 100 - (prediction.confidencePercentage || 50)],
            backgroundColor: ["#10B981", "#F59E0B"]
          }]
        },
        options: { responsive: true }
      },
      team_comparison: {
        data: { labels: [], datasets: [] },
        options: { responsive: true }
      },
      trend_analysis: {
        data: { labels: [], datasets: [] },
        options: { responsive: true }
      }
    };
  };

  // Helper function to get team name by ID
  const getTeamById = (teamId) => {
    return teams.find(team => team.nbaApiId.toString() === teamId.toString());
  };

  // Fetch prediction history
  const fetchPredictionHistory = async () => {
    setHistoryLoading(true);
    try {
      const response = await fetch('http://localhost:8080/api/v1/predictions/history?page=0&size=20');
      if (response.ok) {
        const data = await response.json();
        setPredictionHistory(data.predictions || []);
      }
    } catch (err) {
      console.error('Error fetching prediction history:', err);
    } finally {
      setHistoryLoading(false);
    }
  };

  // Fetch upcoming predictions
  const fetchUpcomingPredictions = async () => {
    setHistoryLoading(true);
    try {
      const response = await fetch('http://localhost:8080/api/v1/predictions/upcoming');
      if (response.ok) {
        const data = await response.json();
        setUpcomingPredictions(data.predictions || []);
      }
    } catch (err) {
      console.error('Error fetching upcoming predictions:', err);
    } finally {
      setHistoryLoading(false);
    }
  };

  // Fetch model accuracy stats
  const fetchModelAccuracy = async () => {
    setHistoryLoading(true);
    try {
      const response = await fetch('http://localhost:8080/api/v1/predictions/accuracy');
      if (response.ok) {
        const data = await response.json();
        setModelAccuracy(data);
      }
    } catch (err) {
      console.error('Error fetching model accuracy:', err);
    } finally {
      setHistoryLoading(false);
    }
  };

  // Handle tab change
  const handleTabChange = (tab) => {
    setActiveTab(tab);
    switch (tab) {
      case 'history':
        if (predictionHistory.length === 0) fetchPredictionHistory();
        break;
      case 'upcoming':
        if (upcomingPredictions.length === 0) fetchUpcomingPredictions();
        break;
      case 'accuracy':
        if (!modelAccuracy) fetchModelAccuracy();
        break;
      default:
        break;
    }
  };

  // Format prediction age
  const formatPredictionAge = (generatedAt) => {
    const now = new Date();
    const generated = new Date(generatedAt);
    const diffMs = now - generated;
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
    const diffDays = Math.floor(diffHours / 24);
    
    if (diffDays > 0) {
      return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`;
    } else if (diffHours > 0) {
      return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`;
    } else {
      return 'Just now';
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
        <p>AI-powered basketball game outcome predictions with detailed analytics and S3 storage</p>
      </div>

      {/* Tab Navigation */}
      <div className="tab-navigation">
        <button 
          className={`tab-button ${activeTab === 'current' ? 'active' : ''}`}
          onClick={() => handleTabChange('current')}
        >
          Current Prediction
        </button>
        <button 
          className={`tab-button ${activeTab === 'upcoming' ? 'active' : ''}`}
          onClick={() => handleTabChange('upcoming')}
        >
          Upcoming Games
        </button>
        <button 
          className={`tab-button ${activeTab === 'history' ? 'active' : ''}`}
          onClick={() => handleTabChange('history')}
        >
          Prediction History
        </button>
        <button 
          className={`tab-button ${activeTab === 'accuracy' ? 'active' : ''}`}
          onClick={() => handleTabChange('accuracy')}
        >
          Model Accuracy
        </button>
      </div>

      {/* Current Prediction Tab */}
      {activeTab === 'current' && (
        <div className="tab-content">
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
                
                {/* Prediction Age/Source Info */}
                <div className="prediction-meta">
                  {prediction.source === 'pre-computed' && predictionAge && (
                    <div className={`prediction-age ${predictionAge.is_fresh ? 'fresh' : 'stale'}`}>
                      <span className="age-badge">
                        {predictionAge.is_fresh ? '✓ Fresh' : '⚠ Stale'} - 
                        Generated {formatPredictionAge(predictionAge.generated_at)}
                      </span>
                      {!predictionAge.is_fresh && (
                        <small> (Model may have been updated since this prediction)</small>
                      )}
                    </div>
                  )}
                  {prediction.source === 'real-time' && (
                    <div className="prediction-age fresh">
                      <span className="age-badge">⚡ Real-time prediction</span>
                    </div>
                  )}
                </div>

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

              {/* S3 Chart Image */}
              {chartImageUrl && (
                <div className="s3-chart-container">
                  <h3>ML-Generated Prediction Chart</h3>
                  <img 
                    src={chartImageUrl} 
                    alt="Prediction Chart from S3" 
                    className="s3-chart-image"
                    onError={(e) => {
                      e.target.style.display = 'none';
                      console.log('Failed to load S3 chart image');
                    }}
                  />
                </div>
              )}
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
        </div>
      )}

      {/* Upcoming Predictions Tab */}
      {activeTab === 'upcoming' && (
        <div className="tab-content">
          <div className="upcoming-predictions">
            <h2>Upcoming Game Predictions</h2>
            {historyLoading ? (
              <div className="loading">Loading upcoming predictions...</div>
            ) : upcomingPredictions.length > 0 ? (
              <div className="predictions-list">
                {upcomingPredictions.map((pred, index) => (
                  <div key={index} className="prediction-card">
                    <div className="prediction-matchup">
                      <h4>Team {pred.team1Id} vs Team {pred.team2Id}</h4>
                      <p className="game-date">Game Date: {pred.gameDate}</p>
                    </div>
                    <div className="prediction-details">
                      <p>Predicted Winner: Team {pred.predictedWinnerId}</p>
                      <p>Score: {pred.team1PredictedScore} - {pred.team2PredictedScore}</p>
                      <p>Confidence: {pred.confidencePercentage}%</p>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p>No upcoming predictions available</p>
            )}
          </div>
        </div>
      )}

      {/* Prediction History Tab */}
      {activeTab === 'history' && (
        <div className="tab-content">
          <div className="prediction-history">
            <h2>Prediction History</h2>
            {historyLoading ? (
              <div className="loading">Loading prediction history...</div>
            ) : predictionHistory.length > 0 ? (
              <div className="history-list">
                {predictionHistory.map((pred, index) => (
                  <div key={index} className="history-card">
                    <div className="history-header">
                      <h4>Team {pred.team1Id} vs Team {pred.team2Id}</h4>
                      <span className="prediction-date">
                        {new Date(pred.createdAt).toLocaleDateString()}
                      </span>
                    </div>
                    <div className="history-details">
                      <p>Predicted: Team {pred.predictedWinnerId} wins</p>
                      <p>Score: {pred.team1PredictedScore} - {pred.team2PredictedScore}</p>
                      <p>Confidence: {pred.confidencePercentage}%</p>
                      {pred.predictionAccuracy !== null && (
                        <p className={`accuracy ${pred.predictionAccuracy ? 'correct' : 'incorrect'}`}>
                          {pred.predictionAccuracy ? '✓ Correct' : '✗ Incorrect'}
                        </p>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p>No prediction history available</p>
            )}
          </div>
        </div>
      )}

      {/* Model Accuracy Tab */}
      {activeTab === 'accuracy' && (
        <div className="tab-content">
          <div className="model-accuracy">
            <h2>Model Performance Statistics</h2>
            {historyLoading ? (
              <div className="loading">Loading accuracy stats...</div>
            ) : modelAccuracy ? (
              <div className="accuracy-stats">
                <div className="stat-card">
                  <h3>Overall Accuracy</h3>
                  <div className="stat-value">
                    {modelAccuracy.overallAccuracy ? `${modelAccuracy.overallAccuracy.toFixed(1)}%` : 'N/A'}
                  </div>
                </div>
                <div className="stat-card">
                  <h3>Total Predictions</h3>
                  <div className="stat-value">{modelAccuracy.totalPredictions || 0}</div>
                </div>
                <div className="stat-card">
                  <h3>Completed Games</h3>
                  <div className="stat-value">{modelAccuracy.completedPredictions || 0}</div>
                </div>
                <div className="stat-card">
                  <h3>Pending Predictions</h3>
                  <div className="stat-value">{modelAccuracy.pendingPredictions || 0}</div>
                </div>
                <div className="stat-card">
                  <h3>Stale Predictions</h3>
                  <div className="stat-value">{modelAccuracy.stalePredictionsCount || 0}</div>
                </div>
              </div>
            ) : (
              <p>No accuracy data available</p>
            )}
          </div>
        </div>
      )}

      <div className="dashboard-footer">
        <p>Powered by AI machine learning algorithms, real-time NBA statistics, and AWS S3 storage</p>
      </div>
    </div>
  );
};

export default PredictionDashboard;