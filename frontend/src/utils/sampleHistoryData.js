// Sample data to test the history functionality
// This can be used to populate the history page for demonstration

export const addSamplePredictions = (addPrediction) => {
  const samplePredictions = [
    {
      gameDate: '2024-01-15',
      team1Id: 1610612747, // Lakers
      team2Id: 1610612744, // Warriors
      team1Name: 'Los Angeles Lakers',
      team2Name: 'Golden State Warriors',
      predictedWinnerId: 1610612747,
      predictedWinnerName: 'Los Angeles Lakers',
      team1PredictedScore: 112,
      team2PredictedScore: 108,
      confidencePercentage: 75,
      s3ChartPath: 'https://sample-s3-bucket.s3.amazonaws.com/prediction-charts/lakers-vs-warriors-20240115.png',
      // Simulate completed game
      actualWinnerId: 1610612747, // Lakers won
      actualTeam1Score: 115,
      actualTeam2Score: 109,
      predictionAccuracy: true
    },
    {
      gameDate: '2024-01-14',
      team1Id: 1610612738, // Celtics
      team2Id: 1610612748, // Heat
      team1Name: 'Boston Celtics',
      team2Name: 'Miami Heat',
      predictedWinnerId: 1610612738,
      predictedWinnerName: 'Boston Celtics',
      team1PredictedScore: 118,
      team2PredictedScore: 102,
      confidencePercentage: 85,
      s3ChartPath: 'https://sample-s3-bucket.s3.amazonaws.com/prediction-charts/celtics-vs-heat-20240114.png',
      // Simulate completed game with wrong prediction
      actualWinnerId: 1610612748, // Heat won (upset)
      actualTeam1Score: 105,
      actualTeam2Score: 110,
      predictionAccuracy: false
    },
    {
      gameDate: new Date().toISOString().split('T')[0], // Today's game
      team1Id: 1610612743, // Nuggets
      team2Id: 1610612760, // Thunder
      team1Name: 'Denver Nuggets',
      team2Name: 'Oklahoma City Thunder',
      predictedWinnerId: 1610612743,
      predictedWinnerName: 'Denver Nuggets',
      team1PredictedScore: 125,
      team2PredictedScore: 118,
      confidencePercentage: 68,
      s3ChartPath: null, // No chart yet - pending game
      // Pending game - no actual results
      actualWinnerId: null,
      actualTeam1Score: null,
      actualTeam2Score: null,
      predictionAccuracy: null
    }
  ];

  // Add each sample prediction
  samplePredictions.forEach(prediction => {
    addPrediction(prediction);
  });
};

// Helper function to integrate with prediction pages
export const savePredictionToHistory = (addPrediction, predictionData) => {
  // This function can be called from your prediction pages
  // when a user makes a new prediction
  const historyEntry = {
    gameDate: predictionData.gameDate || new Date().toISOString().split('T')[0],
    team1Id: predictionData.team1Id,
    team2Id: predictionData.team2Id,
    team1Name: predictionData.team1Name,
    team2Name: predictionData.team2Name,
    predictedWinnerId: predictionData.predictedWinnerId,
    predictedWinnerName: predictionData.predictedWinnerName,
    team1PredictedScore: predictionData.team1PredictedScore,
    team2PredictedScore: predictionData.team2PredictedScore,
    confidencePercentage: predictionData.confidencePercentage,
    s3ChartPath: predictionData.s3ChartPath || null,
    // Initial state - results will be updated later
    actualWinnerId: null,
    actualTeam1Score: null,
    actualTeam2Score: null,
    predictionAccuracy: null
  };

  addPrediction(historyEntry);
};