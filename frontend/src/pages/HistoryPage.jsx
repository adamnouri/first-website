import { useState } from 'react';
import { usePredictionHistory } from '../hooks/usePredictionHistory';
import { useTeams } from '../hooks/useTeams';
import LoadingSpinner from '../components/common/LoadingSpinner';
import ErrorMessage from '../components/common/ErrorMessage';
import PredictionChart from '../components/charts/PredictionChart';

const HistoryPage = () => {
  const {
    loading,
    error,
    predictions,
    totalElements,
    totalPages,
    currentPage,
    pageSize,
    filters,
    goToPage,
    changePageSize,
    updateFilters,
    clearFilters,
    refreshHistory,
    hasNextPage,
    hasPreviousPage
  } = usePredictionHistory();

  const { teams } = useTeams();
  const [selectedPrediction, setSelectedPrediction] = useState(null);
  const [showChartModal, setShowChartModal] = useState(false);

  const handleFilterChange = (newFilters) => {
    updateFilters(newFilters);
  };

  const getTeamName = (nbaApiId) => {
    const team = teams.find(t => t.nbaApiId === nbaApiId);
    return team ? team.fullName : `Team ${nbaApiId}`;
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  const getAccuracyBadge = (prediction) => {
    if (prediction.actualWinnerId === null) {
      return <span className="accuracy-badge pending">Pending</span>;
    }
    
    const isAccurate = prediction.predictionAccuracy === true;
    return (
      <span className={`accuracy-badge ${isAccurate ? 'accurate' : 'inaccurate'}`}>
        {isAccurate ? '✓ Accurate' : '✗ Inaccurate'}
      </span>
    );
  };

  const handleChartView = (prediction) => {
    setSelectedPrediction(prediction);
    setShowChartModal(true);
  };

  const closeChartModal = () => {
    setShowChartModal(false);
    setSelectedPrediction(null);
  };

  const getPaginationNumbers = () => {
    const pages = [];
    const maxVisible = 5;
    const startPage = Math.max(0, currentPage - Math.floor(maxVisible / 2));
    const endPage = Math.min(totalPages - 1, startPage + maxVisible - 1);

    for (let i = startPage; i <= endPage; i++) {
      pages.push(i);
    }
    return pages;
  };

  return (
    <div className="history-page">
      <div className="page-header">
        <h1 className="page-title">Prediction History</h1>
        <p className="page-description">
          Browse past predictions and analyze model accuracy over time
        </p>
      </div>

      {/* Filters */}
      <div className="history-filters">
        <div className="filter-group">
          <label className="filter-label">Start Date</label>
          <input
            type="date"
            value={filters.startDate || ''}
            onChange={(e) => handleFilterChange({ startDate: e.target.value })}
            className="filter-input"
          />
        </div>

        <div className="filter-group">
          <label className="filter-label">End Date</label>
          <input
            type="date"
            value={filters.endDate || ''}
            onChange={(e) => handleFilterChange({ endDate: e.target.value })}
            className="filter-input"
          />
        </div>

        <div className="filter-group">
          <label className="filter-label">Team</label>
          <select
            value={filters.teamId || ''}
            onChange={(e) => handleFilterChange({ teamId: e.target.value || null })}
            className="filter-select"
          >
            <option value="">All Teams</option>
            {teams.map(team => (
              <option key={team.nbaApiId} value={team.nbaApiId}>
                {team.fullName}
              </option>
            ))}
          </select>
        </div>

        <div className="filter-group">
          <label className="filter-label">Accuracy</label>
          <select
            value={filters.accuracyFilter || ''}
            onChange={(e) => handleFilterChange({ accuracyFilter: e.target.value || null })}
            className="filter-select"
          >
            <option value="">All Predictions</option>
            <option value="accurate">Accurate Only</option>
            <option value="inaccurate">Inaccurate Only</option>
          </select>
        </div>

        <div className="filter-actions">
          <button onClick={clearFilters} className="btn btn-secondary">
            Clear Filters
          </button>
          <button onClick={refreshHistory} className="btn btn-primary">
            Refresh
          </button>
        </div>
      </div>

      {/* Results Summary */}
      <div className="history-summary">
        <div className="summary-stats">
          <span className="stat-item">
            <span className="stat-number">{totalElements}</span>
            <span className="stat-label">Total Predictions</span>
          </span>
          <span className="stat-item">
            <span className="stat-number">{predictions.length}</span>
            <span className="stat-label">On This Page</span>
          </span>
          <span className="stat-item">
            <span className="stat-number">{totalPages}</span>
            <span className="stat-label">Total Pages</span>
          </span>
        </div>

        <div className="page-size-selector">
          <label className="page-size-label">Per Page:</label>
          <select
            value={pageSize}
            onChange={(e) => changePageSize(Number(e.target.value))}
            className="page-size-select"
          >
            <option value={10}>10</option>
            <option value={20}>20</option>
            <option value={50}>50</option>
            <option value={100}>100</option>
          </select>
        </div>
      </div>

      {/* Loading State */}
      {loading && (
        <div className="history-loading">
          <LoadingSpinner size="lg" />
          <p>Loading prediction history...</p>
        </div>
      )}

      {/* Error State */}
      {error && (
        <ErrorMessage 
          message={error}
          onRetry={refreshHistory}
          className="history-error"
        />
      )}

      {/* Predictions Table */}
      {!loading && !error && (
        <>
          <div className="predictions-table-container">
            <table className="predictions-table">
              <thead>
                <tr>
                  <th>Date</th>
                  <th>Matchup</th>
                  <th>Prediction</th>
                  <th>Actual Result</th>
                  <th>Confidence</th>
                  <th>Accuracy</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {predictions.map((prediction) => (
                  <tr key={prediction.id} className="prediction-row">
                    <td className="date-cell">
                      {formatDate(prediction.gameDate || prediction.predictionGeneratedAt)}
                    </td>
                    
                    <td className="matchup-cell">
                      <div className="matchup-info">
                        <div className="team-name">{getTeamName(prediction.team1Id)}</div>
                        <div className="vs-text">vs</div>
                        <div className="team-name">{getTeamName(prediction.team2Id)}</div>
                      </div>
                    </td>
                    
                    <td className="prediction-cell">
                      <div className="prediction-info">
                        <div className="predicted-winner">
                          {getTeamName(prediction.predictedWinnerId)}
                        </div>
                        <div className="predicted-scores">
                          {prediction.team1PredictedScore} - {prediction.team2PredictedScore}
                        </div>
                      </div>
                    </td>
                    
                    <td className="actual-cell">
                      {prediction.actualWinnerId ? (
                        <div className="actual-info">
                          <div className="actual-winner">
                            {getTeamName(prediction.actualWinnerId)}
                          </div>
                          <div className="actual-scores">
                            {prediction.actualTeam1Score} - {prediction.actualTeam2Score}
                          </div>
                        </div>
                      ) : (
                        <span className="pending-result">Pending</span>
                      )}
                    </td>
                    
                    <td className="confidence-cell">
                      <div className="confidence-indicator">
                        <div 
                          className="confidence-bar"
                          style={{ 
                            width: `${prediction.confidencePercentage || 75}%`,
                            backgroundColor: prediction.confidencePercentage >= 80 ? '#10B981' : 
                                           prediction.confidencePercentage >= 60 ? '#F59E0B' : '#EF4444'
                          }}
                        ></div>
                        <span className="confidence-text">
                          {prediction.confidencePercentage || 75}%
                        </span>
                      </div>
                    </td>
                    
                    <td className="accuracy-cell">
                      {getAccuracyBadge(prediction)}
                    </td>
                    
                    <td className="actions-cell">
                      {prediction.s3ChartPath && (
                        <button
                          onClick={() => handleChartView(prediction)}
                          className="btn btn-sm chart-btn"
                          title="View Chart"
                        >
                          📊
                        </button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Empty State */}
          {predictions.length === 0 && (
            <div className="empty-state">
              <div className="empty-icon">📊</div>
              <h3 className="empty-title">No Predictions Found</h3>
              <p className="empty-description">
                No predictions match your current filters. Try adjusting your search criteria.
              </p>
            </div>
          )}

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="pagination">
              <button
                onClick={() => goToPage(currentPage - 1)}
                disabled={!hasPreviousPage}
                className="pagination-btn"
              >
                Previous
              </button>

              <div className="pagination-numbers">
                {getPaginationNumbers().map(pageNum => (
                  <button
                    key={pageNum}
                    onClick={() => goToPage(pageNum)}
                    className={`pagination-number ${pageNum === currentPage ? 'active' : ''}`}
                  >
                    {pageNum + 1}
                  </button>
                ))}
              </div>

              <button
                onClick={() => goToPage(currentPage + 1)}
                disabled={!hasNextPage}
                className="pagination-btn"
              >
                Next
              </button>
            </div>
          )}
        </>
      )}

      {/* Chart Modal */}
      {showChartModal && selectedPrediction && (
        <div className="chart-modal-overlay" onClick={closeChartModal}>
          <div className="chart-modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3 className="modal-title">
                {getTeamName(selectedPrediction.team1Id)} vs {getTeamName(selectedPrediction.team2Id)}
              </h3>
              <button onClick={closeChartModal} className="modal-close">
                ×
              </button>
            </div>
            <div className="modal-body">
              <PredictionChart
                chartUrl={selectedPrediction.s3ChartPath}
                altText={`Prediction chart for ${getTeamName(selectedPrediction.team1Id)} vs ${getTeamName(selectedPrediction.team2Id)}`}
              />
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default HistoryPage;