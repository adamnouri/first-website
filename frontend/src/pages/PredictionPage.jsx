import { useState } from 'react';
import { usePredictions } from '../hooks/usePredictions';
import TeamSelectionForm from '../components/forms/TeamSelectionForm';
import ConfidenceGauge from '../components/charts/ConfidenceGauge';
import ScoreComparison from '../components/charts/ScoreComparison';
import TeamRadarChart from '../components/charts/TeamRadarChart';
import WinProbabilityPie from '../components/charts/WinProbabilityPie';
import PredictionChart from '../components/charts/PredictionChart';
import LoadingSpinner from '../components/common/LoadingSpinner';
import ErrorMessage from '../components/common/ErrorMessage';

const PredictionPage = () => {
  const { 
    loading, 
    error, 
    prediction, 
    getPredictionForMatchup, 
    generateRealTimePrediction,
    clearPrediction 
  } = usePredictions();
  
  const [selectedTeams, setSelectedTeams] = useState(null);
  const [predictionMode, setPredictionMode] = useState('precomputed'); // 'precomputed' or 'realtime'

  const handleTeamsSelected = (teams) => {
    setSelectedTeams(teams);
    if (!teams) {
      clearPrediction();
    }
  };

  const handlePredictionRequest = async ({ team1, team2, gameDate }) => {
    try {
      let result;
      
      if (predictionMode === 'precomputed') {
        // Try to get pre-computed prediction first
        try {
          result = await getPredictionForMatchup(team1.nbaApiId, team2.nbaApiId);
          
          // If no pre-computed prediction found, fall back to real-time
          if (result.status === 'no_prediction') {
            console.log('No pre-computed prediction found, generating real-time prediction...');
            result = await generateRealTimePrediction(team1.nbaApiId, team2.nbaApiId, gameDate);
          }
        } catch (err) {
          console.log('Pre-computed prediction failed, falling back to real-time:', err.message);
          result = await generateRealTimePrediction(team1.nbaApiId, team2.nbaApiId, gameDate);
        }
      } else {
        // Generate real-time prediction
        result = await generateRealTimePrediction(team1.nbaApiId, team2.nbaApiId, gameDate);
      }
      
      console.log('Prediction result:', result);
    } catch (err) {
      console.error('Prediction failed:', err);
    }
  };

  const handleNewPrediction = () => {
    clearPrediction();
    setSelectedTeams(null);
  };

  const formatPredictionData = (predictionData) => {
    if (!predictionData) return null;

    // Handle different response formats
    if (predictionData.prediction) {
      // Pre-computed prediction format
      const pred = predictionData.prediction;
      return {
        team1Name: selectedTeams?.team1?.fullName || 'Team 1',
        team2Name: selectedTeams?.team2?.fullName || 'Team 2',
        team1Score: pred.team1PredictedScore || pred.team1_predicted_score || 105,
        team2Score: pred.team2PredictedScore || pred.team2_predicted_score || 102,
        confidence: pred.confidencePercentage ? pred.confidencePercentage / 100 : (pred.confidence || 0.75),
        predictedWinner: pred.predictedWinnerId ? 
          (pred.predictedWinnerId === selectedTeams?.team1?.nbaApiId ? selectedTeams.team1.fullName : selectedTeams.team2.fullName)
          : (pred.predicted_winner || selectedTeams?.team1?.fullName),
        modelVersion: pred.modelVersion || 'v2.0',
        isFresh: predictionData.isFresh !== false,
        chartUrl: predictionData.chartUrl,
        s3Data: predictionData.s3Data
      };
    } else {
      // Real-time prediction format
      return {
        team1Name: selectedTeams?.team1?.fullName || 'Team 1',
        team2Name: selectedTeams?.team2?.fullName || 'Team 2',
        team1Score: predictionData.team1_predicted_score || 105,
        team2Score: predictionData.team2_predicted_score || 102,
        confidence: predictionData.confidence || 0.75,
        predictedWinner: predictionData.predicted_winner || selectedTeams?.team1?.fullName,
        modelVersion: 'v2.0_realtime',
        isFresh: true,
        chartUrl: null,
        chartData: predictionData.chart_data
      };
    }
  };

  const predictionData = formatPredictionData(prediction);

  return (
    <div className="prediction-page">
      <div className="page-header">
        <h1 className="page-title">NBA Game Predictions</h1>
        <p className="page-description">
          Get AI-powered predictions for NBA matchups using advanced machine learning models
        </p>
        
        <div className="prediction-mode-toggle">
          <label className="mode-label">
            <input
              type="radio"
              name="predictionMode"
              value="precomputed"
              checked={predictionMode === 'precomputed'}
              onChange={(e) => setPredictionMode(e.target.value)}
              className="mode-radio"
            />
            Pre-computed Predictions (Faster)
          </label>
          <label className="mode-label">
            <input
              type="radio"
              name="predictionMode"
              value="realtime"
              checked={predictionMode === 'realtime'}
              onChange={(e) => setPredictionMode(e.target.value)}
              className="mode-radio"
            />
            Real-time Generation
          </label>
        </div>
      </div>

      <div className="prediction-content">
        {!prediction ? (
          // Team Selection Form
          <div className="prediction-form-section">
            <TeamSelectionForm
              onTeamsSelected={handleTeamsSelected}
              onPredictionRequest={handlePredictionRequest}
              loading={loading}
            />
          </div>
        ) : (
          // Prediction Results
          <div className="prediction-results">
            <div className="results-header">
              <h2 className="results-title">Prediction Results</h2>
              <div className="results-actions">
                <button 
                  onClick={handleNewPrediction}
                  className="btn btn-secondary"
                >
                  New Prediction
                </button>
              </div>
            </div>

            {loading && (
              <div className="prediction-loading">
                <LoadingSpinner size="lg" />
                <p>Generating prediction...</p>
              </div>
            )}

            {error && (
              <ErrorMessage 
                message={error}
                onRetry={() => selectedTeams && handlePredictionRequest(selectedTeams)}
              />
            )}

            {predictionData && (
              <>
                {/* Prediction Summary */}
                <div className="prediction-summary">
                  <div className="matchup-header">
                    <h3 className="matchup-title">
                      {predictionData.team1Name} vs {predictionData.team2Name}
                    </h3>
                    <div className="prediction-meta">
                      <span className="model-version">Model: {predictionData.modelVersion}</span>
                      <span className={`freshness-indicator ${predictionData.isFresh ? 'fresh' : 'stale'}`}>
                        {predictionData.isFresh ? '🔥 Fresh' : '⚠️ Older'}
                      </span>
                    </div>
                  </div>
                  
                  <div className="winner-prediction">
                    <div className="winner-label">Predicted Winner</div>
                    <div className="winner-name">{predictionData.predictedWinner}</div>
                    <div className="confidence-text">
                      {Math.round(predictionData.confidence * 100)}% Confidence
                    </div>
                  </div>
                </div>

                {/* Charts Grid */}
                <div className="charts-grid">
                  <div className="chart-card">
                    <h4 className="chart-card-title">Confidence Level</h4>
                    <ConfidenceGauge 
                      confidence={predictionData.confidence}
                      size={200}
                    />
                  </div>

                  <div className="chart-card">
                    <h4 className="chart-card-title">Predicted Scores</h4>
                    <ScoreComparison
                      team1Name={predictionData.team1Name}
                      team2Name={predictionData.team2Name}
                      team1Score={predictionData.team1Score}
                      team2Score={predictionData.team2Score}
                      height={250}
                    />
                  </div>

                  <div className="chart-card">
                    <h4 className="chart-card-title">Win Probability</h4>
                    <WinProbabilityPie
                      team1Name={predictionData.team1Name}
                      team2Name={predictionData.team2Name}
                      team1Probability={predictionData.team1Score > predictionData.team2Score ? predictionData.confidence : 1 - predictionData.confidence}
                      team2Probability={predictionData.team2Score > predictionData.team1Score ? predictionData.confidence : 1 - predictionData.confidence}
                      predictedWinner={predictionData.predictedWinner}
                      height={250}
                    />
                  </div>

                  <div className="chart-card">
                    <h4 className="chart-card-title">Team Performance</h4>
                    <TeamRadarChart
                      team1Name={predictionData.team1Name}
                      team2Name={predictionData.team2Name}
                      height={300}
                    />
                  </div>
                </div>

                {/* S3 Chart Image */}
                {predictionData.chartUrl && (
                  <div className="s3-chart-section">
                    <h3 className="section-title">Comprehensive Analysis</h3>
                    <PredictionChart
                      chartUrl={predictionData.chartUrl}
                      altText={`Prediction analysis for ${predictionData.team1Name} vs ${predictionData.team2Name}`}
                      className="main-prediction-chart"
                    />
                  </div>
                )}
              </>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default PredictionPage;