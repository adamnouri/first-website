import { useState, useEffect } from 'react';
import { useTeams } from '../../hooks/useTeams';
import LoadingSpinner from '../common/LoadingSpinner';
import ErrorMessage from '../common/ErrorMessage';

const TeamSelectionForm = ({ onTeamsSelected, onPredictionRequest, loading = false }) => {
  const { teams, loading: teamsLoading, error: teamsError, refetch } = useTeams();
  const [selectedTeam1, setSelectedTeam1] = useState('');
  const [selectedTeam2, setSelectedTeam2] = useState('');
  const [gameDate, setGameDate] = useState('');
  const [formError, setFormError] = useState(null);

  // Set default game date to today
  useEffect(() => {
    const today = new Date().toISOString().split('T')[0];
    setGameDate(today);
  }, []);

  // Notify parent when teams are selected
  useEffect(() => {
    if (selectedTeam1 && selectedTeam2 && selectedTeam1 !== selectedTeam2) {
      const team1 = teams.find(t => t.nbaApiId.toString() === selectedTeam1);
      const team2 = teams.find(t => t.nbaApiId.toString() === selectedTeam2);
      
      if (team1 && team2) {
        onTeamsSelected({ team1, team2 });
        setFormError(null);
      }
    } else {
      onTeamsSelected(null);
    }
  }, [selectedTeam1, selectedTeam2, teams, onTeamsSelected]);

  const handleSubmit = (e) => {
    e.preventDefault();
    setFormError(null);

    // Validation
    if (!selectedTeam1 || !selectedTeam2) {
      setFormError('Please select both teams');
      return;
    }

    if (selectedTeam1 === selectedTeam2) {
      setFormError('Please select different teams');
      return;
    }

    if (!gameDate) {
      setFormError('Please select a game date');
      return;
    }

    const team1 = teams.find(t => t.nbaApiId.toString() === selectedTeam1);
    const team2 = teams.find(t => t.nbaApiId.toString() === selectedTeam2);

    if (!team1 || !team2) {
      setFormError('Selected teams not found');
      return;
    }

    onPredictionRequest({
      team1,
      team2,
      gameDate
    });
  };

  const getAvailableTeams = (excludeTeamId) => {
    return teams.filter(team => team.nbaApiId.toString() !== excludeTeamId);
  };

  const clearSelections = () => {
    setSelectedTeam1('');
    setSelectedTeam2('');
    setFormError(null);
  };

  const swapTeams = () => {
    const temp = selectedTeam1;
    setSelectedTeam1(selectedTeam2);
    setSelectedTeam2(temp);
  };

  if (teamsLoading) {
    return (
      <div className="team-selection-loading">
        <LoadingSpinner size="lg" />
        <p>Loading NBA teams...</p>
      </div>
    );
  }

  if (teamsError) {
    return (
      <ErrorMessage 
        message={teamsError} 
        onRetry={refetch}
        className="team-selection-error"
      />
    );
  }

  return (
    <form onSubmit={handleSubmit} className="team-selection-form">
      <div className="form-header">
        <h2 className="form-title">Select Teams for Prediction</h2>
        <p className="form-description">
          Choose two NBA teams to get an AI-powered game prediction
        </p>
      </div>

      <div className="team-selection-grid">
        {/* Team 1 Selection */}
        <div className="form-group">
          <label htmlFor="team1" className="form-label">
            Team 1
          </label>
          <select
            id="team1"
            value={selectedTeam1}
            onChange={(e) => setSelectedTeam1(e.target.value)}
            className="form-select team-select"
            disabled={loading}
          >
            <option value="">Select first team...</option>
            {getAvailableTeams(selectedTeam2).map((team) => (
              <option key={team.nbaApiId} value={team.nbaApiId.toString()}>
                {team.fullName} ({team.abbreviation})
              </option>
            ))}
          </select>
        </div>

        {/* Swap Button */}
        <div className="swap-button-container">
          <button
            type="button"
            onClick={swapTeams}
            className="btn-swap"
            disabled={!selectedTeam1 || !selectedTeam2 || loading}
            title="Swap teams"
          >
            ⇄
          </button>
        </div>

        {/* Team 2 Selection */}
        <div className="form-group">
          <label htmlFor="team2" className="form-label">
            Team 2
          </label>
          <select
            id="team2"
            value={selectedTeam2}
            onChange={(e) => setSelectedTeam2(e.target.value)}
            className="form-select team-select"
            disabled={loading}
          >
            <option value="">Select second team...</option>
            {getAvailableTeams(selectedTeam1).map((team) => (
              <option key={team.nbaApiId} value={team.nbaApiId.toString()}>
                {team.fullName} ({team.abbreviation})
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Game Date */}
      <div className="form-group">
        <label htmlFor="gameDate" className="form-label">
          Game Date
        </label>
        <input
          type="date"
          id="gameDate"
          value={gameDate}
          onChange={(e) => setGameDate(e.target.value)}
          className="form-input"
          disabled={loading}
        />
      </div>

      {/* Form Errors */}
      {formError && (
        <div className="form-error">
          {formError}
        </div>
      )}

      {/* Form Actions */}
      <div className="form-actions">
        <button
          type="button"
          onClick={clearSelections}
          className="btn btn-secondary"
          disabled={loading || (!selectedTeam1 && !selectedTeam2)}
        >
          Clear
        </button>
        <button
          type="submit"
          className="btn btn-primary"
          disabled={loading || !selectedTeam1 || !selectedTeam2 || selectedTeam1 === selectedTeam2}
        >
          {loading ? (
            <>
              <LoadingSpinner size="sm" className="btn-spinner" />
              Generating...
            </>
          ) : (
            'Get Prediction'
          )}
        </button>
      </div>

      {/* Selection Summary */}
      {selectedTeam1 && selectedTeam2 && selectedTeam1 !== selectedTeam2 && (
        <div className="selection-summary">
          <div className="matchup-preview">
            <span className="team-name">
              {teams.find(t => t.nbaApiId.toString() === selectedTeam1)?.fullName}
            </span>
            <span className="vs-text">vs</span>
            <span className="team-name">
              {teams.find(t => t.nbaApiId.toString() === selectedTeam2)?.fullName}
            </span>
          </div>
          <div className="game-date-preview">
            Game Date: {new Date(gameDate).toLocaleDateString()}
          </div>
        </div>
      )}
    </form>
  );
};

export default TeamSelectionForm;