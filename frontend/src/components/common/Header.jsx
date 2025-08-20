import { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Bars3Icon, XMarkIcon } from '@heroicons/react/24/outline';

const Header = () => {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const location = useLocation();

  const navItems = [
    { name: 'Home', path: '/' },
    { name: 'Predictions', path: '/predictions' },
    { name: 'History', path: '/history' },
    { name: 'Analytics', path: '/analytics' },
    { name: 'About', path: '/about' },
  ];

  const isActivePath = (path) => {
    return location.pathname === path;
  };

  const toggleMobileMenu = () => {
    setIsMobileMenuOpen(!isMobileMenuOpen);
  };

  return (
    <header className="header">
      <div className="header-container">
        <div className="header-content">
          <Link to="/" className="header-logo">
            <span className="logo-text">NBA Predictor</span>
          </Link>

          <nav className="nav-desktop">
            {navItems.map((item) => (
              <Link
                key={item.path}
                to={item.path}
                className={`nav-link ${isActivePath(item.path) ? 'nav-link-active' : ''}`}
              >
                {item.name}
              </Link>
            ))}
          </nav>

          <button
            className="mobile-menu-button"
            onClick={toggleMobileMenu}
            aria-label="Toggle mobile menu"
          >
            {isMobileMenuOpen ? (
              <XMarkIcon className="mobile-menu-icon" />
            ) : (
              <Bars3Icon className="mobile-menu-icon" />
            )}
          </button>
        </div>

        {isMobileMenuOpen && (
          <nav className="nav-mobile">
            {navItems.map((item) => (
              <Link
                key={item.path}
                to={item.path}
                className={`nav-link-mobile ${isActivePath(item.path) ? 'nav-link-mobile-active' : ''}`}
                onClick={() => setIsMobileMenuOpen(false)}
              >
                {item.name}
              </Link>
            ))}
          </nav>
        )}
      </div>
    </header>
  );
};

export default Header;