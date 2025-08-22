import React, { useState, useEffect } from 'react';
import { Bar, Doughnut, Line } from 'react-chartjs-2';
import { usePlayoffs } from '../hooks/usePlayoffs';
import LoadingSpinner from './common/LoadingSpinner';
import ErrorMessage from './common/ErrorMessage';
import './ChampionshipOdds.css';

const ChampionshipOdds = ({ simulations = 5000 }) => {
  const { 
    championshipOdds,
    loading, 
    errors, 
    fetchChampionshipOdds, 
    isDataFresh,
    lastUpdated 
  } = usePlayoffs();

  const [simulationCount, setSimulationCount] = useState(simulations);
  const [viewMode, setViewMode] = useState('top10'); // 'top10', 'conference', 'all'
  const [chartType, setChartType] = useState('bar'); // 'bar', 'doughnut', 'line'

  useEffect(() => {
    if (!isDataFresh('odds', 60)) { // Cache for 60 minutes
      fetchChampionshipOdds(simulationCount);
    }
  }, [simulationCount, fetchChampionshipOdds, isDataFresh]);

  const handleRefresh = () => {
    fetchChampionshipOdds(simulationCount, true);
  };

  const getFilteredData = () => {
    if (!championshipOdds || championshipOdds.length === 0) return [];
    
    switch (viewMode) {
      case 'top10':
        return championshipOdds.slice(0, 10);
      case 'conference':
        return championshipOdds.filter(team => team.championship_probability > 0.001);
      case 'all':
        return championshipOdds;
      default:
        return championshipOdds.slice(0, 10);
    }
  };

  const formatPercentage = (value) => {
    if (value < 0.001) return '<0.1%';
    return `${(value * 100).toFixed(1)}%`;
  };

  const formatOdds = (probability) => {
    if (probability <= 0) return 'N/A';
    const odds = (1 / probability) - 1;
    if (odds < 1) return `1:${(1/odds).toFixed(1)}`;
    return `${odds.toFixed(0)}:1`;
  };

  const getChartData = () => {
    const filteredData = getFilteredData();
    const labels = filteredData.map(team => team.team_abbreviation);
    const data = filteredData.map(team => team.championship_probability * 100);
    
    const backgroundColors = filteredData.map((_, index) => {
      const colors = [
        '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF',
        '#FF9F40', '#FF6384', '#C9CBCF', '#4BC0C0', '#36A2EB'
      ];
      return colors[index % colors.length];
    });

    return {
      labels,
      datasets: [{
        label: 'Championship Probability (%)',
        data,
        backgroundColor: backgroundColors,
        borderColor: backgroundColors.map(color => color.replace('0.6', '1')),
        borderWidth: 2
      }]
    };
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: chartType === 'doughnut',
        position: 'right'
      },
      title: {
        display: true,
        text: 'Championship Probabilities',
        font: {
          size: 16,
          weight: 'bold'
        }
      },
      tooltip: {
        callbacks: {
          label: function(context) {
            const team = getFilteredData()[context.dataIndex];
            return [
              `${team.team_name}: ${formatPercentage(team.championship_probability)}`,
              `Odds: ${formatOdds(team.championship_probability)}`,
              `Conference: ${team.conference}`
            ];
          }
        }
      }
    },
    scales: chartType !== 'doughnut' ? {
      x: {
        title: {
          display: true,
          text: 'Teams'
        }
      },
      y: {
        title: {
          display: true,
          text: 'Probability (%)'
        },
        beginAtZero: true,
        max: Math.max(...getFilteredData().map(team => team.championship_probability * 100)) * 1.1
      }
    } : undefined
  };

  const renderTopContenders = () => {
    const topTeams = championshipOdds.slice(0, 5);
    
    return (
      <div className="top-contenders">
        <h3>Championship Favorites</h3>
        <div className="contenders-grid">
          {topTeams.map((team, index) => (
            <div key={team.team_id} className={`contender-card rank-${index + 1}`}>
              <div className="contender-rank">#{index + 1}</div>
              <div className="contender-info">
                <div className="team-name">{team.team_abbreviation}</div>
                <div className="team-full-name">{team.team_name}</div>
                <div className="probability">{formatPercentage(team.championship_probability)}</div>
                <div className="odds">Odds: {formatOdds(team.championship_probability)}</div>
                <div className="conference">{team.conference} Conference</div>
              </div>
              <div className="contender-visual">
                <div 
                  className="probability-circle"
                  style={{
                    background: `conic-gradient(#3498db 0deg ${team.championship_probability * 360}deg, #ecf0f1 ${team.championship_probability * 360}deg 360deg)`
                  }}
                >
                  <div className="circle-inner">
                    {formatPercentage(team.championship_probability)}
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  };

  const renderChart = () => {
    const chartData = getChartData();
    
    return (
      <div className="championship-chart">
        <div className="chart-controls">
          <div className="control-group">
            <label>View:</label>
            <select 
              value={viewMode}
              onChange={(e) => setViewMode(e.target.value)}
              className="control-select"
            >
              <option value="top10">Top 10 Teams</option>
              <option value="conference">Contenders Only</option>
              <option value="all">All Teams</option>
            </select>
          </div>
          
          <div className="control-group">
            <label>Chart Type:</label>
            <select 
              value={chartType}
              onChange={(e) => setChartType(e.target.value)}
              className="control-select"
            >
              <option value="bar">Bar Chart</option>
              <option value="doughnut">Doughnut Chart</option>
              <option value="line">Line Chart</option>
            </select>
          </div>
        </div>
        
        <div className="chart-container">
          {chartType === 'bar' && <Bar data={chartData} options={chartOptions} />}
          {chartType === 'doughnut' && <Doughnut data={chartData} options={chartOptions} />}
          {chartType === 'line' && <Line data={chartData} options={chartOptions} />}
        </div>
      </div>
    );
  };

  const renderFullTable = () => {
    const filteredData = getFilteredData();
    
    return (
      <div className="odds-table-container">
        <h3>Complete Championship Odds</h3>
        <div className="table-wrapper">
          <table className="odds-table">
            <thead>
              <tr>
                <th>Rank</th>
                <th>Team</th>
                <th>Conference</th>
                <th>Championship %</th>
                <th>Finals %</th>
                <th>Playoff %</th>
                <th>Betting Odds</th>
              </tr>
            </thead>
            <tbody>
              {filteredData.map((team, index) => (
                <tr key={team.team_id} className={index < 3 ? 'top-favorite' : ''}>
                  <td className="rank-cell">{index + 1}</td>
                  <td className="team-cell">
                    <div className="team-info">
                      <span className="team-abbreviation">{team.team_abbreviation}</span>
                      <span className="team-name">{team.team_name}</span>
                    </div>
                  </td>
                  <td className="conference-cell">{team.conference}</td>
                  <td className="percentage-cell highlight">
                    {formatPercentage(team.championship_probability)}
                  </td>
                  <td className="percentage-cell">
                    {formatPercentage(team.finals_probability || 0)}
                  </td>
                  <td className="percentage-cell">
                    {formatPercentage(team.playoff_probability || 0)}
                  </td>
                  <td className="odds-cell">
                    {formatOdds(team.championship_probability)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    );
  };

  if (loading.odds) {
    return (
      <div className="championship-odds">
        <LoadingSpinner size="lg" />
        <p>Calculating championship odds with {simulationCount.toLocaleString()} simulations...</p>
      </div>
    );
  }

  if (errors.odds) {
    return (
      <div className="championship-odds">
        <ErrorMessage 
          message={errors.odds} 
          onRetry={handleRefresh}
          className="odds-error"
        />
      </div>
    );
  }

  return (
    <div className="championship-odds">
      <div className="odds-header">
        <div className="header-content">
          <h2>Championship Odds</h2>
          <p className="header-description">
            Comprehensive championship probabilities based on {simulationCount.toLocaleString()} tournament simulations
          </p>
        </div>
        
        <div className="odds-controls">
          <div className="control-group">
            <label htmlFor="simulations-input">Simulations:</label>
            <select
              id="simulations-input"
              value={simulationCount}
              onChange={(e) => setSimulationCount(parseInt(e.target.value))}
              className="control-select"
            >
              <option value="1000">1,000</option>
              <option value="5000">5,000</option>
              <option value="10000">10,000</option>
              <option value="25000">25,000</option>
            </select>
          </div>
          
          <button 
            onClick={handleRefresh}
            className="refresh-button"
            disabled={loading.odds}
          >
            {loading.odds ? 'Calculating...' : 'Refresh Odds'}
          </button>
        </div>
      </div>

      {lastUpdated.odds && (
        <div className="odds-meta">
          <span className="last-updated">
            Last updated: {new Date(lastUpdated.odds).toLocaleString()}
          </span>
        </div>
      )}

      <div className="odds-content">
        {championshipOdds.length > 0 && renderTopContenders()}
        {championshipOdds.length > 0 && renderChart()}
        {championshipOdds.length > 0 && renderFullTable()}
      </div>
    </div>
  );
};

export default ChampionshipOdds;