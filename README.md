
# AsaliAsPossible

An intelligent reinforcement learning framework for autonomous beehive management in Rwanda, integrating IoT sensors, machine learning models, and a mobile application to optimize honey production and colony health.

## Project Documentation

You can access the full file here:

 [Click to open Drive File](https://drive.google.com/file/d/1wdo2T2OF1RMT0yb9hE8LMkoJHRzFofu7/view?usp=sharing)


## Overview

AsaliAsPossible is a comprehensive beehive monitoring system that combines multiple machine learning models to provide real-time insights and automated recommendations for beekeepers. The system analyzes audio data, sensor readings, and historical patterns to make intelligent decisions about hive management.

## System Architecture

The system consists of three core machine learning components working in concert:

**1. Audio Classification (CNN-LSTM)**
- Analyzes beehive sounds using Mel-frequency cepstral coefficients (MFCC)
- Detects queen status, swarming risk, and colony health indicators
- Achieves 77% general classification accuracy and 98% confidence for queenless hive detection
- Processes audio spectrograms for pattern recognition

**2. Time Series Forecasting (LSTM)**
- Predicts future hive conditions based on historical sensor data
- Forecasts temperature, humidity, and weight trends
- Uses rolling statistics and temporal features
- Enables proactive management decisions

**3. Reinforcement Learning Agent (PPO)**
- Makes autonomous management recommendations
- Processes 35 environmental and biological features
- Outputs 13 possible actions including feeding, harvesting, and health maintenance
- Learns optimal strategies through reward-based training

## Features

**Real-Time Monitoring**
- Live temperature, humidity, and weight tracking
- Audio-based health assessment
- Interactive dashboard with visualizations

**Predictive Analytics**
- Weather-informed forecasting
- Weight trend analysis
- Harvest timing optimization

**Intelligent Recommendations**
- AI-driven management actions
- Context-aware decision support
- Risk alerts and notifications

**Hive Management**
- Multiple hive tracking via interactive map
- Harvest history and analytics
- Historical data entry and analysis

**Mobile Interface**
- Cross-platform Flutter application
- Responsive design with dark mode support
- Offline capability with data synchronization

## Technology Stack

**Mobile Application**
- Flutter
- Provider (state management)
- FL Chart (data visualization)
- Google Maps integration

**Backend**
- FastAPI (Python)
- MongoDB Atlas (database)
- RESTful API architecture

**Machine Learning**
- TensorFlow/Keras (CNN-LSTM, LSTM models)
- Stable-Baselines3 (PPO reinforcement learning)
- Librosa (audio processing)
- NumPy, Pandas (data processing)

**Deployment**
- Docker containerization
- Cloud-based model serving
- Real-time data processing pipeline

## Installation

**Prerequisites**
- Python 3.8+
- Flutter SDK
- MongoDB Atlas account
- Node.js (for additional tooling)

**Backend Setup**
```bash
# Clone repository
git clone https://github.com/RainiBenaiah/asaliaspossible.git
cd asaliaspossible/backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Edit .env with your MongoDB credentials

# Run backend server
uvicorn main:app --reload
```

**Mobile App Setup**
```bash
cd asaliaspossible/mobile

# Install dependencies
flutter pub get

# Run on device/emulator
flutter run
```

## ML Models

**Audio Classification Model**
- Architecture: CNN-LSTM hybrid
- Input: MFCC features from audio spectrograms
- Output: Colony health classifications
- Training data: 26,840 audio files (34 GB)

**Forecasting Model**
- Architecture: LSTM recurrent neural network
- Input: 24-hour historical sensor readings
- Output: Future temperature, humidity, weight predictions
- Features: Rolling means, standard deviations, temporal patterns

**RL Agent**
- Algorithm: Proximal Policy Optimization (PPO)
- State space: 35 features (sensor data, model predictions, environmental factors)
- Action space: 13 management interventions
- Training: Reward-based optimization for honey production and colony health

## API Endpoints
```
POST /api/auth/register          - User registration
POST /api/auth/login             - User authentication
GET  /api/hives                  - List all hives
POST /api/hives                  - Create new hive
GET  /api/hives/{id}             - Get hive details
POST /api/hives/{id}/audio       - Upload audio for analysis
POST /api/hives/{id}/historical  - Add sensor readings
GET  /api/hives/{id}/forecast    - Get predictions
GET  /api/hives/{id}/recommendations - Get RL recommendations
```

## Project Structure
```
asaliaspossible/
├── backend/
│   ├── main.py                 # FastAPI application
│   ├── models/
│   │   ├── audio_classifier.py
│   │   ├── lstm_forecaster.py
│   │   └── rl_agent.py
│   ├── ml_models/              # Trained model weights
│   ├── routes/                 # API endpoints
│   └── utils/                  # Helper functions
├── mobile/
│   ├── lib/
│   │   ├── screens/            # UI screens
│   │   ├── providers/          # State management
│   │   ├── services/           # API integration
│   │   └── models/             # Data models
│   └── assets/                 # Images and resources
└── docs/                       # Documentation
```

## Data Processing Pipeline

1. **Data Collection**: IoT sensors capture temperature, humidity, weight; microphones record audio
2. **Preprocessing**: Audio converted to MFCC spectrograms; sensor data normalized and aggregated
3. **Feature Extraction**: CNN-LSTM extracts audio patterns; LSTM processes temporal sequences
4. **Feature Fusion**: All model outputs combined into unified state representation
5. **Decision Making**: PPO agent evaluates state and selects optimal action
6. **Execution**: Recommendations sent to mobile app; user receives notifications
7. **Feedback Loop**: User actions and outcomes used to retrain models

## Contributing

Contributions are welcome. Please follow these steps:

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a pull request

## License

This project is part of an academic capstone at African Leadership University.

## Contact

For questions or collaboration opportunities, please reach out through the repository issues or contacts provided in the documentation.

## Acknowledgments

- African Leadership University for academic support
- Rwandan beekeeping cooperatives for domain expertise and data collection
- Open-source ML community for tools and frameworks
