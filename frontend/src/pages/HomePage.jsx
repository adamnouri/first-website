import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useTeams } from '../hooks/useTeams';
import LoadingSpinner from '../components/common/LoadingSpinner';
import ErrorMessage from '../components/common/ErrorMessage';
import { ChartBarIcon, ClockIcon, TrophyIcon } from '@heroicons/react/24/outline';

const HomePage = () => {
  const { teams, loading, error, refetch } = useTeams();
  const [featuredTeams, setFeaturedTeams] = useState([]);

  useEffect(() => {
    if (teams.length > 0) {
      const shuffled = [...teams].sort(() => 0.5 - Math.random());
      setFeaturedTeams(shuffled.slice(0, 6));
    }
  }, [teams]);

  const features = [
    {
      icon: ChartBarIcon,
      title: 'Advanced Analytics',
      description: 'Machine learning models analyze team performance, player stats, and historical data to generate accurate predictions.'
    },
    {
      icon: ClockIcon,
      title: 'Real-time Updates',
      description: 'Get the latest predictions based on current team rosters, injuries, and recent performance trends.'
    },
    {
      icon: TrophyIcon,
      title: 'High Accuracy',
      description: 'Our models have been trained on years of NBA data to provide reliable predictions for game outcomes.'
    }
  ];

  const handleGetStarted = () => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  if (loading) {
    return (
      <div className="home-page">
        <div className="loading-container">
          <LoadingSpinner size="xl" />
          <p className="loading-text">Loading NBA teams...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="home-page">
        <ErrorMessage 
          message={error} 
          onRetry={refetch}
          className="home-error"
        />
      </div>
    );
  }

  return (
    <div className="home-page">
      <section className="hero-section">
        <div className="hero-content">
          <h1 className="hero-title">
            NBA Game Predictions
            <span className="hero-accent">Powered by AI</span>
          </h1>
          <p className="hero-description">
            Get accurate NBA game predictions using advanced machine learning algorithms. 
            Analyze team performance, player statistics, and historical data to make informed decisions.
          </p>
          <div className="hero-actions">
            <Link to="/predictions" className="btn btn-primary btn-large">
              View Predictions
            </Link>
            <Link to="/about" className="btn btn-secondary btn-large">
              Learn More
            </Link>
          </div>
        </div>
        <div className="hero-stats">
          <div className="stat-item">
            <span className="stat-number">{teams.length}</span>
            <span className="stat-label">NBA Teams</span>
          </div>
          <div className="stat-item">
            <span className="stat-number">85%</span>
            <span className="stat-label">Accuracy Rate</span>
          </div>
          <div className="stat-item">
            <span className="stat-number">1000+</span>
            <span className="stat-label">Predictions Made</span>
          </div>
        </div>
      </section>

      <section className="features-section">
        <div className="section-header">
          <h2 className="section-title">Why Choose Our Predictions?</h2>
          <p className="section-description">
            Our advanced machine learning models provide the most accurate NBA game predictions
          </p>
        </div>
        <div className="features-grid">
          {features.map((feature, index) => (
            <div key={index} className="feature-card">
              <div className="feature-icon">
                <feature.icon className="icon" />
              </div>
              <h3 className="feature-title">{feature.title}</h3>
              <p className="feature-description">{feature.description}</p>
            </div>
          ))}
        </div>
      </section>

      {featuredTeams.length > 0 && (
        <section className="teams-section">
          <div className="section-header">
            <h2 className="section-title">Featured Teams</h2>
            <p className="section-description">
              Sample of NBA teams in our prediction system
            </p>
          </div>
          <div className="teams-grid">
            {featuredTeams.map((team) => (
              <div key={team.id} className="team-card">
                <div className="team-info">
                  <h3 className="team-name">{team.fullName}</h3>
                  <p className="team-abbreviation">{team.abbreviation}</p>
                  <p className="team-city">{team.city}</p>
                </div>
                <div className="team-conference">
                  <span className={`conference-badge ${team.conference?.toLowerCase()}`}>
                    {team.conference}
                  </span>
                </div>
              </div>
            ))}
          </div>
          <div className="teams-action">
            <Link to="/predictions" className="btn btn-primary">
              View All Predictions
            </Link>
          </div>
        </section>
      )}

      <section className="cta-section">
        <div className="cta-content">
          <h2 className="cta-title">Ready to Make Better Predictions?</h2>
          <p className="cta-description">
            Join thousands of users who trust our AI-powered NBA predictions
          </p>
          <button onClick={handleGetStarted} className="btn btn-primary btn-large">
            Get Started Now
          </button>
        </div>
      </section>
    </div>
  );
};

export default HomePage;