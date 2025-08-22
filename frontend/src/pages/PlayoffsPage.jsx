import { useState } from 'react';
import { usePlayoffs } from '../hooks/usePlayoffs';
import ChampionshipOdds from '../components/ChampionshipOdds';
import ConferenceStandings from '../components/ConferenceStandings';
import LoadingSpinner from '../components/common/LoadingSpinner';
import ErrorMessage from '../components/common/ErrorMessage';

const PlayoffsPage = () => {
  const [activeTab, setActiveTab] = useState('championship');
  const [simulations, setSimulations] = useState(1000);
  
  const {
    championshipOdds,
    standings,
    bracket,
    loading,
    errors,
    fetchChampionshipOdds,
    fetchStandings,
    fetchBracket
  } = usePlayoffs();

  const handleSimulationChange = (newSimulations) => {
    setSimulations(newSimulations);
  };

  const tabs = [
    { id: 'championship', label: 'Championship Odds', icon: '🏆' },
    { id: 'standings', label: 'Conference Standings', icon: '📊' },
    { id: 'bracket', label: 'Playoff Bracket', icon: '🏀' }
  ];

  const simulationOptions = [
    { value: 100, label: 'Fast (100 simulations)' },
    { value: 1000, label: 'Standard (1,000 simulations)' },
    { value: 5000, label: 'Detailed (5,000 simulations)' },
    { value: 10000, label: 'Comprehensive (10,000 simulations)' }
  ];

  const hasErrors = Object.keys(errors).length > 0;
  const currentError = errors[activeTab];
  const isCurrentLoading = loading[activeTab] || false;

  return (
    <div className="playoffs-page">
      {/* Page Header */}
      <div className="page-header">
        <h1 className="page-title">🏀 NBA Playoffs Predictions</h1>
        <p className="page-description">
          Advanced machine learning predictions for championship odds, conference standings, and playoff brackets
        </p>
        
        {/* Simulation Controls */}
        <div className="simulation-controls">
          <label htmlFor="simulations" className="control-label">
            Prediction Accuracy:
          </label>
          <select 
            id="simulations"
            value={simulations}
            onChange={(e) => handleSimulationChange(Number(e.target.value))}
            className="simulation-select"
          >
            {simulationOptions.map(option => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
          <span className="simulation-info">
            Higher simulation counts provide more accurate predictions but take longer to load
          </span>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="tab-navigation">
        {tabs.map(tab => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`tab-button ${activeTab === tab.id ? 'active' : ''}`}
          >
            <span className="tab-icon">{tab.icon}</span>
            <span className="tab-label">{tab.label}</span>
          </button>
        ))}
      </div>

      {/* Error Display */}
      {currentError && (
        <ErrorMessage 
          message={currentError}
          onRetry={() => {
            if (activeTab === 'championship') fetchChampionshipOdds(simulations, true);
            else if (activeTab === 'standings') fetchStandings('both', simulations, true);
            else if (activeTab === 'bracket') fetchBracket(false, true);
          }}
        />
      )}

      {/* Loading State */}
      {isCurrentLoading && (
        <div className="loading-section">
          <LoadingSpinner size="lg" />
          <p className="loading-text">
            Running {simulations.toLocaleString()} playoff simulations...
          </p>
        </div>
      )}

      {/* Tab Content */}
      <div className="tab-content">
        {activeTab === 'championship' && (
          <div className="championship-section">
            <div className="section-header">
              <h2 className="section-title">🏆 Championship Odds</h2>
              <p className="section-description">
                Probability of each team winning the NBA Championship based on playoff simulations
              </p>
              <button 
                onClick={() => fetchChampionshipOdds(simulations, true)}
                className="refresh-button"
                disabled={isCurrentLoading}
              >
                🔄 Refresh Odds
              </button>
            </div>
            <ChampionshipOdds 
              odds={championshipOdds} 
              loading={loading.odds}
              simulations={simulations}
            />
          </div>
        )}

        {activeTab === 'standings' && (
          <div className="standings-section">
            <div className="section-header">
              <h2 className="section-title">📊 Conference Standings</h2>
              <p className="section-description">
                Projected final regular season standings and playoff probabilities
              </p>
              <button 
                onClick={() => fetchStandings('both', simulations, true)}
                className="refresh-button"
                disabled={isCurrentLoading}
              >
                🔄 Refresh Standings
              </button>
            </div>
            <ConferenceStandings 
              standings={standings} 
              loading={loading.standings}
              simulations={simulations}
            />
          </div>
        )}

        {activeTab === 'bracket' && (
          <div className="bracket-section">
            <div className="section-header">
              <h2 className="section-title">🏀 Playoff Bracket</h2>
              <p className="section-description">
                Predicted playoff matchups and series outcomes
              </p>
              <button 
                onClick={() => fetchBracket(false, true)}
                className="refresh-button"
                disabled={isCurrentLoading}
              >
                🔄 Refresh Bracket
              </button>
            </div>
            
            {bracket ? (
              <div className="bracket-container">
                <div className="bracket-info">
                  <p><strong>Generated:</strong> {new Date(bracket.generated_at).toLocaleString()}</p>
                  <p><strong>Simulations:</strong> {simulations.toLocaleString()}</p>
                </div>
                
                {/* Play-in Tournament */}
                {bracket.play_in && (
                  <div className="play-in-section">
                    <h3>Play-In Tournament</h3>
                    <div className="play-in-games">
                      {Object.entries(bracket.play_in).map(([conference, games]) => (
                        <div key={conference} className="conference-play-in">
                          <h4>{conference} Conference</h4>
                          {Object.entries(games).map(([gameKey, game]) => (
                            <div key={gameKey} className="play-in-game">
                              <div className="matchup">{game.matchup}</div>
                              <div className="description">{game.description}</div>
                            </div>
                          ))}
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* First Round */}
                {bracket.first_round && (
                  <div className="first-round-section">
                    <h3>First Round</h3>
                    <div className="first-round-matchups">
                      {Object.entries(bracket.first_round).map(([conference, matchups]) => (
                        <div key={conference} className="conference-matchups">
                          <h4>{conference} Conference</h4>
                          {matchups.map((matchup, index) => (
                            <div key={index} className="playoff-matchup">
                              <div className="matchup-teams">{matchup.matchup}</div>
                              {matchup.series_prediction && (
                                <div className="series-prediction">
                                  <div className="predicted-winner">
                                    Predicted Winner: {matchup.series_prediction.predicted_winner?.team_abbreviation}
                                  </div>
                                  <div className="confidence">
                                    Confidence: {(matchup.series_prediction.confidence * 100).toFixed(1)}%
                                  </div>
                                  <div className="predicted-games">
                                    Games: {matchup.series_prediction.predicted_games}
                                  </div>
                                </div>
                              )}
                            </div>
                          ))}
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <div className="no-bracket">
                <p>No playoff bracket data available. Click "Refresh Bracket" to generate predictions.</p>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default PlayoffsPage;