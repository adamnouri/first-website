import React from 'react';
import './TournamentBracket.css';

/**
 * TournamentBracket Component
 * 
 * Simple visual tournament bracket display for NBA playoff data.
 */
const TournamentBracket = ({ bracket, simulations }) => {
  console.log('TournamentBracket rendered with:', { bracket, simulations });
  
  if (!bracket) {
    console.log('TournamentBracket: No bracket data, showing empty state');
    return (
      <div className="tournament-bracket-empty">
        <p>No bracket data available. Click "Refresh Bracket" to generate predictions.</p>
      </div>
    );
  }

  console.log('TournamentBracket: Rendering with bracket data');
  console.log('Bracket structure keys:', Object.keys(bracket));
  console.log('Full bracket object:', JSON.stringify(bracket, null, 2));

  return (
    <div className="tournament-bracket-container">
      <div className="bracket-header">
        <h3>🏀 NBA Playoff Tournament Bracket</h3>
        <div className="bracket-info">
          <span><strong>Generated:</strong> {new Date(bracket.generated_at).toLocaleString()}</span>
          <span><strong>Simulations:</strong> {simulations?.toLocaleString()}</span>
        </div>
      </div>
      
      {/* Visual Bracket Display */}
      <div className="bracket-wrapper">
        <div className="bracket-rounds">
          
          {/* First Round */}
          <div className="round-section">
            <h3 className="round-title">First Round</h3>
            <div className="round-grid">
              <div className="conference-section eastern-conference">
                <h4>Eastern Conference</h4>
                {bracket.first_round?.Eastern?.map((matchup, index) => (
                  <div key={index} className="matchup-card">
                    <div className={`team-row ${matchup.series_prediction?.predicted_winner?.team_abbreviation === matchup.higher_seed?.team_abbreviation ? 'team-winner' : 'team-loser'}`}>
                      {matchup.higher_seed?.team_abbreviation} {matchup.series_prediction?.predicted_winner?.team_abbreviation === matchup.higher_seed?.team_abbreviation && '✓'}
                    </div>
                    <div className={`team-row ${matchup.series_prediction?.predicted_winner?.team_abbreviation === matchup.lower_seed?.team_abbreviation ? 'team-winner' : 'team-loser'}`}>
                      {matchup.lower_seed?.team_abbreviation} {matchup.series_prediction?.predicted_winner?.team_abbreviation === matchup.lower_seed?.team_abbreviation && '✓'}
                    </div>
                    {matchup.series_prediction?.confidence && (
                      <div className="confidence-info">
                        Confidence: {(matchup.series_prediction.confidence * 100).toFixed(1)}%
                      </div>
                    )}
                  </div>
                ))}
              </div>
              
              <div className="conference-section western-conference">
                <h4>Western Conference</h4>
                {bracket.first_round?.Western?.map((matchup, index) => (
                  <div key={index} className="matchup-card">
                    <div className={`team-row ${matchup.series_prediction?.predicted_winner?.team_abbreviation === matchup.higher_seed?.team_abbreviation ? 'team-winner' : 'team-loser'}`}>
                      {matchup.higher_seed?.team_abbreviation} {matchup.series_prediction?.predicted_winner?.team_abbreviation === matchup.higher_seed?.team_abbreviation && '✓'}
                    </div>
                    <div className={`team-row ${matchup.series_prediction?.predicted_winner?.team_abbreviation === matchup.lower_seed?.team_abbreviation ? 'team-winner' : 'team-loser'}`}>
                      {matchup.lower_seed?.team_abbreviation} {matchup.series_prediction?.predicted_winner?.team_abbreviation === matchup.lower_seed?.team_abbreviation && '✓'}
                    </div>
                    {matchup.series_prediction?.confidence && (
                      <div className="confidence-info">
                        Confidence: {(matchup.series_prediction.confidence * 100).toFixed(1)}%
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Conference Semifinals */}
          {(bracket.conference_semifinals?.Eastern?.length > 0 || bracket.conference_semifinals?.Western?.length > 0) && (
            <div className="round-section">
              <h3 className="round-title">Conference Semifinals</h3>
              <div className="round-grid">
                <div className="conference-section eastern-conference">
                  <h4>Eastern Conference</h4>
                  {bracket.conference_semifinals?.Eastern?.map((matchup, index) => (
                    <div key={index} className="matchup-card">
                      <div className={`team-row ${matchup.series_prediction?.predicted_winner?.team_abbreviation === matchup.team1?.team_abbreviation ? 'team-winner' : 'team-loser'}`}>
                        {matchup.team1?.team_abbreviation} {matchup.series_prediction?.predicted_winner?.team_abbreviation === matchup.team1?.team_abbreviation && '✓'}
                      </div>
                      <div className={`team-row ${matchup.series_prediction?.predicted_winner?.team_abbreviation === matchup.team2?.team_abbreviation ? 'team-winner' : 'team-loser'}`}>
                        {matchup.team2?.team_abbreviation} {matchup.series_prediction?.predicted_winner?.team_abbreviation === matchup.team2?.team_abbreviation && '✓'}
                      </div>
                      {matchup.series_prediction?.confidence && (
                        <div className="confidence-info">
                          Confidence: {(matchup.series_prediction.confidence * 100).toFixed(1)}%
                        </div>
                      )}
                    </div>
                  ))}
                </div>
                
                <div className="conference-section western-conference">
                  <h4>Western Conference</h4>
                  {bracket.conference_semifinals?.Western?.map((matchup, index) => (
                    <div key={index} className="matchup-card">
                      <div className={`team-row ${matchup.series_prediction?.predicted_winner?.team_abbreviation === matchup.team1?.team_abbreviation ? 'team-winner' : 'team-loser'}`}>
                        {matchup.team1?.team_abbreviation} {matchup.series_prediction?.predicted_winner?.team_abbreviation === matchup.team1?.team_abbreviation && '✓'}
                      </div>
                      <div className={`team-row ${matchup.series_prediction?.predicted_winner?.team_abbreviation === matchup.team2?.team_abbreviation ? 'team-winner' : 'team-loser'}`}>
                        {matchup.team2?.team_abbreviation} {matchup.series_prediction?.predicted_winner?.team_abbreviation === matchup.team2?.team_abbreviation && '✓'}
                      </div>
                      {matchup.series_prediction?.confidence && (
                        <div className="confidence-info">
                          Confidence: {(matchup.series_prediction.confidence * 100).toFixed(1)}%
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* Conference Finals */}
          {(bracket.conference_finals?.Eastern || bracket.conference_finals?.Western) && (
            <div className="round-section">
              <h3 className="round-title">Conference Finals</h3>
              <div className="round-grid">
                <div className="conference-section eastern-conference">
                  <h4>Eastern Conference</h4>
                  {bracket.conference_finals?.Eastern && (
                    <div className="matchup-card">
                      <div className={`team-row ${bracket.conference_finals.Eastern.series_prediction?.predicted_winner?.team_abbreviation === bracket.conference_finals.Eastern.team1?.team_abbreviation ? 'team-winner' : 'team-loser'}`}>
                        {bracket.conference_finals.Eastern.team1?.team_abbreviation} {bracket.conference_finals.Eastern.series_prediction?.predicted_winner?.team_abbreviation === bracket.conference_finals.Eastern.team1?.team_abbreviation && '✓'}
                      </div>
                      <div className={`team-row ${bracket.conference_finals.Eastern.series_prediction?.predicted_winner?.team_abbreviation === bracket.conference_finals.Eastern.team2?.team_abbreviation ? 'team-winner' : 'team-loser'}`}>
                        {bracket.conference_finals.Eastern.team2?.team_abbreviation} {bracket.conference_finals.Eastern.series_prediction?.predicted_winner?.team_abbreviation === bracket.conference_finals.Eastern.team2?.team_abbreviation && '✓'}
                      </div>
                      {bracket.conference_finals.Eastern.series_prediction?.confidence && (
                        <div className="confidence-info">
                          Confidence: {(bracket.conference_finals.Eastern.series_prediction.confidence * 100).toFixed(1)}%
                        </div>
                      )}
                    </div>
                  )}
                </div>
                
                <div className="conference-section western-conference">
                  <h4>Western Conference</h4>
                  {bracket.conference_finals?.Western && (
                    <div className="matchup-card">
                      <div className={`team-row ${bracket.conference_finals.Western.series_prediction?.predicted_winner?.team_abbreviation === bracket.conference_finals.Western.team1?.team_abbreviation ? 'team-winner' : 'team-loser'}`}>
                        {bracket.conference_finals.Western.team1?.team_abbreviation} {bracket.conference_finals.Western.series_prediction?.predicted_winner?.team_abbreviation === bracket.conference_finals.Western.team1?.team_abbreviation && '✓'}
                      </div>
                      <div className={`team-row ${bracket.conference_finals.Western.series_prediction?.predicted_winner?.team_abbreviation === bracket.conference_finals.Western.team2?.team_abbreviation ? 'team-winner' : 'team-loser'}`}>
                        {bracket.conference_finals.Western.team2?.team_abbreviation} {bracket.conference_finals.Western.series_prediction?.predicted_winner?.team_abbreviation === bracket.conference_finals.Western.team2?.team_abbreviation && '✓'}
                      </div>
                      {bracket.conference_finals.Western.series_prediction?.confidence && (
                        <div className="confidence-info">
                          Confidence: {(bracket.conference_finals.Western.series_prediction.confidence * 100).toFixed(1)}%
                        </div>
                      )}
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}

          {/* NBA Finals */}
          {bracket.nba_finals?.matchup && (
            <div className="round-section">
              <h3 className="round-title">NBA Finals</h3>
              <div className="finals-section">
                <div className="matchup-card finals-card">
                  <div className={`team-row ${bracket.nba_finals.series_prediction?.predicted_winner?.team_abbreviation === bracket.nba_finals.eastern_champion?.team_abbreviation ? 'team-winner' : 'team-loser'}`}>
                    {bracket.nba_finals.eastern_champion?.team_abbreviation} {bracket.nba_finals.series_prediction?.predicted_winner?.team_abbreviation === bracket.nba_finals.eastern_champion?.team_abbreviation && '✓'}
                  </div>
                  <div className={`team-row ${bracket.nba_finals.series_prediction?.predicted_winner?.team_abbreviation === bracket.nba_finals.western_champion?.team_abbreviation ? 'team-winner' : 'team-loser'}`}>
                    {bracket.nba_finals.western_champion?.team_abbreviation} {bracket.nba_finals.series_prediction?.predicted_winner?.team_abbreviation === bracket.nba_finals.western_champion?.team_abbreviation && '✓'}
                  </div>
                  {bracket.nba_finals.series_prediction?.confidence && (
                    <div className="confidence-info">
                      Confidence: {(bracket.nba_finals.series_prediction.confidence * 100).toFixed(1)}%
                    </div>
                  )}
                  <div className="champion-info">
                    <strong>🏆 Predicted Champion: {bracket.nba_finals.series_prediction?.predicted_winner?.team_abbreviation}</strong>
                  </div>
                </div>
              </div>
            </div>
          )}

        </div>
      </div>
      
      {/* Legend */}
      <div className="bracket-legend">
        <div className="legend-item">
          <div className="legend-color winner"></div>
          <span>Predicted Winner</span>
        </div>
        <div className="legend-item">
          <div className="legend-color loser"></div>
          <span>Predicted Loser</span>
        </div>
      </div>
    </div>
  );
};

export default TournamentBracket;