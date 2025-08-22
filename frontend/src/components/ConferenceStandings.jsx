import React, { useState, useEffect } from 'react';
import { usePlayoffs } from '../hooks/usePlayoffs';
import LoadingSpinner from './common/LoadingSpinner';
import ErrorMessage from './common/ErrorMessage';
import './ConferenceStandings.css';

const ConferenceStandings = ({ conference = 'both', simulations = 1000 }) => {
  const { 
    standings, 
    loading, 
    errors, 
    fetchStandings, 
    isDataFresh,
    lastUpdated 
  } = usePlayoffs();

  const [selectedConference, setSelectedConference] = useState(conference);
  const [simulationCount, setSimulationCount] = useState(simulations);
  const [sortConfig, setSortConfig] = useState({ key: 'rank', direction: 'asc' });

  useEffect(() => {
    if (!isDataFresh('standings', 30)) {
      fetchStandings(selectedConference, simulationCount);
    }
  }, [selectedConference, simulationCount, fetchStandings, isDataFresh]);

  const handleRefresh = () => {
    fetchStandings(selectedConference, simulationCount, true);
  };

  const handleSort = (key) => {
    let direction = 'asc';
    if (sortConfig.key === key && sortConfig.direction === 'asc') {
      direction = 'desc';
    }
    setSortConfig({ key, direction });
  };

  const sortedStandings = (conferenceTeams) => {
    if (!conferenceTeams) return [];
    
    return [...conferenceTeams].sort((a, b) => {
      const aValue = a[sortConfig.key];
      const bValue = b[sortConfig.key];
      
      if (aValue < bValue) {
        return sortConfig.direction === 'asc' ? -1 : 1;
      }
      if (aValue > bValue) {
        return sortConfig.direction === 'asc' ? 1 : -1;
      }
      return 0;
    });
  };

  const formatPercentage = (value) => {
    return `${(value * 100).toFixed(1)}%`;
  };

  const formatRecord = (wins, losses) => {
    return `${wins}-${losses}`;
  };

  const getPlayoffStatus = (rank, playoffProb) => {
    if (rank <= 6) return 'playoff-lock';
    if (rank <= 10 && playoffProb > 0.3) return 'playoff-race';
    if (playoffProb > 0.1) return 'playoff-bubble';
    return 'playoff-out';
  };

  const getPlayoffStatusText = (rank, playoffProb) => {
    if (rank <= 6) return 'Playoff Lock';
    if (rank <= 10 && playoffProb > 0.3) return 'Play-in Race';
    if (playoffProb > 0.1) return 'On Bubble';
    return 'Eliminated';
  };

  const renderStandingsTable = (conferenceTeams, conferenceName) => {
    const sorted = sortedStandings(conferenceTeams);
    
    return (
      <div className="conference-table-container">
        <div className="conference-header">
          <h3>{conferenceName} Conference</h3>
          <span className="team-count">{sorted.length} teams</span>
        </div>
        
        <div className="table-wrapper">
          <table className="standings-table">
            <thead>
              <tr>
                <th 
                  className={`sortable ${sortConfig.key === 'rank' ? sortConfig.direction : ''}`}
                  onClick={() => handleSort('rank')}
                >
                  Rank
                </th>
                <th>Team</th>
                <th 
                  className={`sortable ${sortConfig.key === 'projected_wins' ? sortConfig.direction : ''}`}
                  onClick={() => handleSort('projected_wins')}
                >
                  Record
                </th>
                <th 
                  className={`sortable ${sortConfig.key === 'win_percentage' ? sortConfig.direction : ''}`}
                  onClick={() => handleSort('win_percentage')}
                >
                  Win %
                </th>
                <th 
                  className={`sortable ${sortConfig.key === 'playoff_probability' ? sortConfig.direction : ''}`}
                  onClick={() => handleSort('playoff_probability')}
                >
                  Playoff %
                </th>
                <th 
                  className={`sortable ${sortConfig.key === 'championship_odds' ? sortConfig.direction : ''}`}
                  onClick={() => handleSort('championship_odds')}
                >
                  Title Odds
                </th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {sorted.map((team) => (
                <tr 
                  key={team.team_id} 
                  className={`team-row ${getPlayoffStatus(team.rank, team.playoff_probability)}`}
                >
                  <td className="rank-cell">
                    <span className="rank-number">{team.rank}</span>
                  </td>
                  <td className="team-cell">
                    <div className="team-info">
                      <span className="team-abbreviation">{team.team_abbreviation}</span>
                      <span className="team-name">{team.team_name}</span>
                    </div>
                  </td>
                  <td className="record-cell">
                    {formatRecord(team.projected_wins, team.projected_losses)}
                  </td>
                  <td className="percentage-cell">
                    {formatPercentage(team.win_percentage)}
                  </td>
                  <td className="percentage-cell">
                    <div className="probability-bar">
                      <div 
                        className="probability-fill"
                        style={{ width: `${team.playoff_probability * 100}%` }}
                      ></div>
                      <span className="probability-text">
                        {formatPercentage(team.playoff_probability)}
                      </span>
                    </div>
                  </td>
                  <td className="percentage-cell">
                    {formatPercentage(team.championship_odds)}
                  </td>
                  <td className="status-cell">
                    <span className={`status-badge ${getPlayoffStatus(team.rank, team.playoff_probability)}`}>
                      {getPlayoffStatusText(team.rank, team.playoff_probability)}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    );
  };

  if (loading.standings) {
    return (
      <div className="conference-standings">
        <LoadingSpinner size="lg" />
        <p>Generating conference standings...</p>
      </div>
    );
  }

  if (errors.standings) {
    return (
      <div className="conference-standings">
        <ErrorMessage 
          message={errors.standings} 
          onRetry={handleRefresh}
          className="standings-error"
        />
      </div>
    );
  }

  return (
    <div className="conference-standings">
      <div className="standings-header">
        <div className="header-content">
          <h2>Conference Standings</h2>
          <p className="header-description">
            Projected final standings based on {simulationCount.toLocaleString()} simulations
          </p>
        </div>
        
        <div className="standings-controls">
          <div className="control-group">
            <label htmlFor="conference-select">Conference:</label>
            <select 
              id="conference-select"
              value={selectedConference}
              onChange={(e) => setSelectedConference(e.target.value)}
              className="control-select"
            >
              <option value="both">Both Conferences</option>
              <option value="eastern">Eastern Conference</option>
              <option value="western">Western Conference</option>
            </select>
          </div>
          
          <div className="control-group">
            <label htmlFor="simulations-input">Simulations:</label>
            <select
              id="simulations-input"
              value={simulationCount}
              onChange={(e) => setSimulationCount(parseInt(e.target.value))}
              className="control-select"
            >
              <option value="500">500</option>
              <option value="1000">1,000</option>
              <option value="2500">2,500</option>
              <option value="5000">5,000</option>
            </select>
          </div>
          
          <button 
            onClick={handleRefresh}
            className="refresh-button"
            disabled={loading.standings}
          >
            {loading.standings ? 'Updating...' : 'Refresh'}
          </button>
        </div>
      </div>

      {lastUpdated.standings && (
        <div className="standings-meta">
          <span className="last-updated">
            Last updated: {new Date(lastUpdated.standings).toLocaleString()}
          </span>
        </div>
      )}

      <div className="standings-content">
        {selectedConference === 'both' ? (
          <div className="both-conferences">
            {standings.Eastern && renderStandingsTable(standings.Eastern, 'Eastern')}
            {standings.Western && renderStandingsTable(standings.Western, 'Western')}
          </div>
        ) : selectedConference === 'eastern' ? (
          standings.Eastern && renderStandingsTable(standings.Eastern, 'Eastern')
        ) : (
          standings.Western && renderStandingsTable(standings.Western, 'Western')
        )}
      </div>

      <div className="standings-legend">
        <h4>Playoff Status Legend</h4>
        <div className="legend-items">
          <div className="legend-item">
            <span className="legend-color playoff-lock"></span>
            <span>Playoff Lock (Top 6)</span>
          </div>
          <div className="legend-item">
            <span className="legend-color playoff-race"></span>
            <span>Play-in Race (7-10)</span>
          </div>
          <div className="legend-item">
            <span className="legend-color playoff-bubble"></span>
            <span>On Bubble</span>
          </div>
          <div className="legend-item">
            <span className="legend-color playoff-out"></span>
            <span>Eliminated</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ConferenceStandings;