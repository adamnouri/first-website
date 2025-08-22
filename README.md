# 🏀 NBA Prediction Application

A comprehensive full-stack NBA game prediction application featuring **machine learning-powered playoff predictions**, real-time game analysis, and championship probability calculations.

## ⚡ Key Features

### 🏆 **Playoff Prediction System** (Latest Feature)
- **Conference Seeding**: Predicted final standings for Eastern/Western conferences (1-15 rankings)
- **Tournament Brackets**: Complete playoff bracket generation with play-in tournament support
- **Championship Odds**: Monte Carlo simulation-based championship probabilities for all 30 teams
- **Series Predictions**: 7-game playoff series predictions with game-by-game breakdowns
- **Tournament Simulation**: Full playoff tournament simulation with upset analysis

### 🎯 **Game Predictions**
- Real-time NBA game outcome predictions using advanced ML models
- Team-vs-team matchup analysis with confidence scores
- Historical prediction accuracy tracking
- Batch prediction processing for upcoming games

### 📊 **Data & Analytics**
- AWS S3 integration for prediction storage and chart generation
- PostgreSQL database for team data and prediction metadata
- Interactive charts and visualizations
- Performance analytics and model accuracy metrics

## 🏗️ Architecture

```
React Frontend (Port 3000) ↔ Spring Boot Backend (Port 8080) ↔ Python ML Service (Port 5000)
                                        ↓
                              PostgreSQL Database + AWS S3 Storage
```

### Technology Stack
- **Frontend**: React 18, Chart.js, Axios, Custom Hooks
- **Backend**: Spring Boot, JPA/Hibernate, PostgreSQL  
- **ML Service**: Python Flask, scikit-learn, XGBoost, NumPy/Pandas
- **Storage**: AWS S3, PostgreSQL
- **DevOps**: Docker, Docker Compose

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- AWS Account with S3 access
- Node.js 18+, Python 3.8+, Java 21+

### 1. Clone & Setup
```bash
git clone <repository-url>
cd first-website
cp .env.example .env  # Add your AWS credentials
```

### 2. Start Services
```bash
# Start PostgreSQL database
docker-compose up -d

# Start Spring Boot backend
cd backend/NBA-Model && mvn spring-boot:run

# Start Python ML service  
cd ml-service && pip install -r requirements.txt && python app.py

# Start React frontend
cd frontend && npm install && npm run dev
```

### 3. Access Application
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8080
- **ML Service**: http://localhost:5000

## 📡 API Endpoints

### Game Predictions
```bash
POST /predict                    # Single game prediction
POST /batch/generate-predictions # Batch predictions with S3 storage
GET  /teams/rankings            # Team strength rankings
```

### Playoff Predictions
```bash
GET  /playoffs/conference-standings  # Eastern/Western conference predicted standings
GET  /playoffs/bracket              # Complete tournament bracket
GET  /playoffs/championship-odds    # Championship probability calculations
POST /playoffs/series-prediction    # Predict 7-game playoff series
POST /playoffs/simulate-tournament  # Full tournament simulation
```

### Team & Analytics
```bash
GET /api/v1/teams               # All NBA teams
GET /api/v1/predictions/history # Prediction history
GET /api/v1/predictions/accuracy # Model accuracy stats
```

## 🎮 Usage Examples

### Conference Standings
```javascript
// Get Eastern Conference predicted standings
const standings = await predictionService.getEasternConferenceStandings(1000);
// Returns: Teams 1-15 with projected wins/losses and playoff probability
```

### Playoff Bracket
```javascript
// Generate interactive tournament bracket
const bracket = await predictionService.generatePlayoffBracket();
// Returns: Complete bracket with play-in, all rounds, and predicted winners
```

### Championship Odds
```javascript
// Calculate championship probabilities (5000 simulations)
const odds = await predictionService.getChampionshipOdds(5000);
// Returns: Championship probability for all 30 teams
```

### Series Prediction
```javascript
// Predict Lakers vs Celtics playoff series
const series = await predictionService.predictPlayoffSeries(
  1610612747, // Lakers
  1610612738, // Celtics  
  'nba_finals'
);
// Returns: Series winner, game-by-game predictions, series length
```

## 📁 Project Structure

```
first-website/
├── frontend/                   # React application
│   ├── src/
│   │   ├── components/        # React components
│   │   ├── services/          # API service layer
│   │   ├── hooks/             # Custom React hooks (usePlayoffs, etc.)
│   │   └── styles/            # CSS styling
├── backend/NBA-Model/         # Spring Boot application  
│   └── src/main/java/com/better/nbamodel/
│       ├── entity/            # JPA entities (Team, Prediction, etc.)
│       ├── controller/        # REST controllers
│       ├── service/           # Business logic
│       └── repository/        # Data access layer
└── ml-service/                # Python ML service
    ├── app.py                 # Flask application
    └── services/              # ML prediction services
        ├── playoff_predictor.py         # Playoff simulation logic
        ├── championship_calculator.py   # Championship odds calculation
        └── enhanced_prediction_service.py # Core ML models
```

## 🔄 Data Flow

1. **User selects teams** → Frontend team selection interface
2. **Prediction request** → React → Spring Boot → Python ML Service  
3. **ML processing** → Playoff simulation, bracket generation, odds calculation
4. **Storage** → Predictions saved to PostgreSQL, charts stored in S3
5. **Response** → Real-time prediction results with visualizations

## 🏆 Playoff Features Deep Dive

### Conference Standings Simulation
- Simulates remaining regular season games using team strength ratings
- Generates projected win-loss records for all 30 teams
- Calculates playoff probability based on historical performance thresholds
- Separates Eastern and Western conference analysis

### Tournament Bracket Generation  
- Creates complete playoff bracket structure
- Includes play-in tournament for 7th-10th seeds
- Predicts winners for each round using series simulation
- Supports both Eastern and Western conference brackets

### Championship Probability Engine
- Monte Carlo simulation with 5000+ tournament runs
- Calculates championship odds for all teams
- Tracks round-by-round advancement probabilities  
- Identifies most likely championship scenarios and potential upsets

### Series Prediction System
- Predicts outcome of 7-game playoff series
- Game-by-game breakdown with home court advantage
- Accounts for playoff vs regular season performance differences
- Provides series length prediction and confidence metrics

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/playoff-enhancement`)
3. Commit changes (`git commit -am 'Add playoff bracket visualization'`)
4. Push to branch (`git push origin feature/playoff-enhancement`)  
5. Create Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**Built with ❤️ for NBA fans and data enthusiasts**
