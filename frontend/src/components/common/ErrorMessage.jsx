import { ExclamationTriangleIcon } from '@heroicons/react/24/outline';

const ErrorMessage = ({ message, onRetry, className = '' }) => {
  return (
    <div className={`error-message ${className}`}>
      <div className="error-content">
        <ExclamationTriangleIcon className="error-icon" />
        <div className="error-text">
          <p className="error-title">Something went wrong</p>
          <p className="error-description">{message}</p>
        </div>
      </div>
      {onRetry && (
        <button onClick={onRetry} className="btn btn-secondary error-retry-btn">
          Try Again
        </button>
      )}
    </div>
  );
};

export default ErrorMessage;