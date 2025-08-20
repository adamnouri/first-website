const Footer = () => {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="footer">
      <div className="footer-container">
        <div className="footer-content">
          <div className="footer-section">
            <h3 className="footer-title">NBA Predictor</h3>
            <p className="footer-description">
              Advanced machine learning predictions for NBA games using real-time data analysis.
            </p>
          </div>

          <div className="footer-section">
            <h4 className="footer-heading">Quick Links</h4>
            <ul className="footer-links">
              <li>
                <a href="/" className="footer-link">Home</a>
              </li>
              <li>
                <a href="/predictions" className="footer-link">Predictions</a>
              </li>
              <li>
                <a href="/analytics" className="footer-link">Analytics</a>
              </li>
              <li>
                <a href="/about" className="footer-link">About</a>
              </li>
            </ul>
          </div>

          <div className="footer-section">
            <h4 className="footer-heading">Features</h4>
            <ul className="footer-links">
              <li>
                <span className="footer-link">Real-time Predictions</span>
              </li>
              <li>
                <span className="footer-link">Historical Analysis</span>
              </li>
              <li>
                <span className="footer-link">Team Statistics</span>
              </li>
              <li>
                <span className="footer-link">Performance Metrics</span>
              </li>
            </ul>
          </div>
        </div>

        <div className="footer-bottom">
          <p className="footer-copyright">
            © {currentYear} NBA Predictor. All rights reserved.
          </p>
          <p className="footer-disclaimer">
            For entertainment purposes only. Not affiliated with the NBA.
          </p>
        </div>
      </div>
    </footer>
  );
};

export default Footer;