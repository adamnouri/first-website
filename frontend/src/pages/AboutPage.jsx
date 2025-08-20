const AboutPage = () => {
  return (
    <div className="about-page">
      <div className="page-header">
        <h1 className="page-title">About NBA Predictor</h1>
        <p className="page-description">
          Learn about our AI-powered NBA prediction system
        </p>
      </div>
      
      <div className="about-content">
        <section className="about-section">
          <h2 className="section-title">Our Mission</h2>
          <p className="section-text">
            We leverage advanced machine learning algorithms to provide accurate, data-driven predictions 
            for NBA games. Our system analyzes team performance, player statistics, historical data, and 
            real-time factors to generate reliable forecasts.
          </p>
        </section>

        <section className="about-section">
          <h2 className="section-title">How It Works</h2>
          <div className="process-steps">
            <div className="step">
              <h3 className="step-title">Data Collection</h3>
              <p className="step-description">
                We gather comprehensive data from NBA APIs, including team stats, player performance, 
                and historical game results.
              </p>
            </div>
            <div className="step">
              <h3 className="step-title">Model Training</h3>
              <p className="step-description">
                Our machine learning models are trained on years of NBA data to identify patterns 
                and predictive factors.
              </p>
            </div>
            <div className="step">
              <h3 className="step-title">Prediction Generation</h3>
              <p className="step-description">
                The trained models analyze current data to generate accurate predictions for 
                upcoming games.
              </p>
            </div>
          </div>
        </section>

        <section className="about-section">
          <h2 className="section-title">Technology Stack</h2>
          <div className="tech-grid">
            <div className="tech-item">
              <h4>Backend</h4>
              <p>Java Spring Boot, PostgreSQL</p>
            </div>
            <div className="tech-item">
              <h4>Machine Learning</h4>
              <p>Python, Flask, Scikit-learn</p>
            </div>
            <div className="tech-item">
              <h4>Frontend</h4>
              <p>React, React Router</p>
            </div>
            <div className="tech-item">
              <h4>Cloud Storage</h4>
              <p>AWS S3</p>
            </div>
          </div>
        </section>
      </div>
    </div>
  );
};

export default AboutPage;