import numpy as np
import pickle
from typing import List, Tuple, Dict
import tensorflow as tf
from pathlib import Path

class ForecastingService:
    """
    LSTM Time-series forecasting service
    Configuration from your notebook:
    - Lookback: 24 hours
    - Forecast horizon: 6 hours
    - Features: temperature, humidity
    """
    
    LOOKBACK_HOURS = 24
    FORECAST_HORIZON = 6
    FEATURES = ['temperature', 'humidity']
    
    def __init__(self, model_path: str, scaler_path: str):
        """Load LSTM model and scaler"""
        self.model = tf.keras.models.load_model(model_path)
        
        with open(scaler_path, 'rb') as f:
            self.scaler = pickle.load(f)
        
        print(f" LSTM model loaded from {model_path}")
        print(f" Scaler loaded from {scaler_path}")
    
    def prepare_sequence(self, historical_data: List[Dict]) -> np.ndarray:
        """
        Prepare 24-hour sequence for prediction
        
        Args:
            historical_data: List of dicts with 'temperature' and 'humidity'
                             Ordered from oldest to newest (24 readings)
        
        Returns:
            normalized_sequence: shape (1, 24, 2)
        """
        if len(historical_data) < self.LOOKBACK_HOURS:
            raise ValueError(
                f"Need {self.LOOKBACK_HOURS} historical readings, got {len(historical_data)}"
            )
        
        # Take last 24 readings
        recent_data = historical_data[-self.LOOKBACK_HOURS:]
        
        # Extract temperature and humidity
        sequence = np.array([
            [reading['temperature'], reading['humidity']]
            for reading in recent_data
        ])  # Shape: (24, 2)
        
        # Normalize using the scaler
        normalized_sequence = self.scaler.transform(sequence)
        
        # Add batch dimension: (1, 24, 2)
        normalized_sequence = np.expand_dims(normalized_sequence, axis=0)
        
        return normalized_sequence
    
    def predict_future(self, historical_data: List[Dict]) -> Dict:
        """
        Predict next 6 hours of temperature and humidity
        
        Returns:
            {
                'forecasts': {
                    'temperature': [35.1, 35.3, 35.5, 35.7, 35.9, 36.1],
                    'humidity': [63, 64, 65, 65, 66, 66]
                },
                'current': {
                    'temperature': 34.5,
                    'humidity': 62
                },
                'trends': {
                    'temperature': 'increasing',
                    'humidity': 'stable'
                },
                'changes': {
                    'temperature': 1.6,  # °C change over 6h
                    'humidity': 4        # % change over 6h
                }
            }
        """
        try:
            # Prepare sequence
            normalized_sequence = self.prepare_sequence(historical_data)
            
            # Predict
            predictions = self.model.predict(normalized_sequence, verbose=0)
            # predictions shape: (1, 6, 2) - 6 hours, 2 features
            
            # Denormalize predictions
            predictions_reshaped = predictions[0]  # (6, 2)
            denormalized = self.scaler.inverse_transform(predictions_reshaped)
            
            # Extract forecasts
            temperature_forecast = denormalized[:, 0].tolist()
            humidity_forecast = denormalized[:, 1].tolist()
            
            # Get current values (last reading)
            current_temp = historical_data[-1]['temperature']
            current_hum = historical_data[-1]['humidity']
            
            # Calculate trends
            temp_change = temperature_forecast[-1] - current_temp
            hum_change = humidity_forecast[-1] - current_hum
            
            temp_trend = self._get_trend(temp_change, threshold=0.5)
            hum_trend = self._get_trend(hum_change, threshold=2.0)
            
            # Build result
            result = {
                'forecasts': {
                    'temperature': [round(t, 1) for t in temperature_forecast],
                    'humidity': [round(h, 1) for h in humidity_forecast],
                    'hours': list(range(1, self.FORECAST_HORIZON + 1))
                },
                'current': {
                    'temperature': round(current_temp, 1),
                    'humidity': round(current_hum, 1)
                },
                'trends': {
                    'temperature': temp_trend,
                    'humidity': hum_trend
                },
                'changes': {
                    'temperature': round(temp_change, 1),
                    'humidity': round(hum_change, 1)
                },
                'alerts': self._generate_forecast_alerts(
                    temperature_forecast, 
                    humidity_forecast, 
                    temp_trend, 
                    hum_trend
                )
            }
            
            return result
            
        except Exception as e:
            raise Exception(f"Forecasting error: {str(e)}")
    
    def _get_trend(self, change: float, threshold: float) -> str:
        """Determine trend from change value"""
        if change > threshold:
            return 'increasing'
        elif change < -threshold:
            return 'decreasing'
        else:
            return 'stable'
    
    def _generate_forecast_alerts(
        self, 
        temp_forecast: List[float], 
        hum_forecast: List[float],
        temp_trend: str,
        hum_trend: str
    ) -> List[Dict]:
        """Generate alerts based on forecasts"""
        alerts = []
        
        # Temperature alerts (optimal: 32-36°C)
        max_temp = max(temp_forecast)
        min_temp = min(temp_forecast)
        
        if max_temp > 36:
            alerts.append({
                'type': 'temperature_high',
                'message': f'Temperature may reach {max_temp:.1f}°C (above 36°C)',
                'severity': 'high' if max_temp > 38 else 'medium'
            })
        
        if min_temp < 32:
            alerts.append({
                'type': 'temperature_low',
                'message': f'Temperature may drop to {min_temp:.1f}°C (below 32°C)',
                'severity': 'high' if min_temp < 30 else 'medium'
            })
        
        # Humidity alerts (optimal: 50-70%)
        max_hum = max(hum_forecast)
        min_hum = min(hum_forecast)
        
        if max_hum > 70:
            alerts.append({
                'type': 'humidity_high',
                'message': f'Humidity may reach {max_hum:.0f}% (above 70%)',
                'severity': 'medium'
            })
        
        if min_hum < 50:
            alerts.append({
                'type': 'humidity_low',
                'message': f'Humidity may drop to {min_hum:.0f}% (below 50%)',
                'severity': 'medium'
            })
        
        return alerts
    
    def validate_historical_data(self, data: List[Dict]) -> Tuple[bool, str]:
        """Validate historical data meets requirements"""
        if len(data) < self.LOOKBACK_HOURS:
            return False, f"Need {self.LOOKBACK_HOURS} readings, got {len(data)}"
        
        # Check each reading has required fields
        for i, reading in enumerate(data[-self.LOOKBACK_HOURS:]):
            if 'temperature' not in reading:
                return False, f"Reading {i} missing 'temperature'"
            if 'humidity' not in reading:
                return False, f"Reading {i} missing 'humidity'"
            
            # Check reasonable ranges
            temp = reading['temperature']
            hum = reading['humidity']
            
            if not (10 <= temp <= 50):
                return False, f"Temperature {temp}°C out of range (10-50°C)"
            if not (0 <= hum <= 100):
                return False, f"Humidity {hum}% out of range (0-100%)"
        
        return True, "Valid"


# Singleton instance
_forecasting_service_instance = None

def get_forecasting_service() -> ForecastingService:
    """Get singleton instance of ForecastingService"""
    global _forecasting_service_instance
    
    if _forecasting_service_instance is None:
        model_path = "ml_models/forecasting/lstm_forecaster.keras"
        scaler_path = "ml_models/forecasting/forecast_scaler.pkl"
        _forecasting_service_instance = ForecastingService(model_path, scaler_path)
    
    return _forecasting_service_instance