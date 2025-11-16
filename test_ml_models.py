"""
Test script to verify ML models are working
Run: python test_ml_models.py
"""
import numpy as np
from services.audio_service import get_audio_service
from services.forecasting_service import get_forecasting_service
from services.rl_service import get_rl_service
from pathlib import Path

def test_audio_model():
    print("\n" + "="*60)
    print("Testing Audio Classification Model")
    print("="*60)
    
    try:
        audio_service = get_audio_service()
        
        # Test with sample audio
        sample_path = "ml_models/sample_audio/active_sample.wav"
        
        if not Path(sample_path).exists():
            print(f"  Sample audio not found: {sample_path}")
            print("   Please add sample audio files to test")
            return False
        
        result = audio_service.classify_audio(sample_path)
        
        print(f"\n Classification Result:")
        print(f"  Status: {result['status']}")
        print(f"  Confidence: {result['confidence']}%")
        print(f"  Probabilities:")
        for status, prob in result['probabilities'].items():
            print(f"    {status}: {prob}%")
        
        return True
        
    except Exception as e:
        print(f"✗ Audio model test failed: {e}")
        return False


def test_forecasting_model():
    print("\n" + "="*60)
    print("Testing LSTM Forecasting Model")
    print("="*60)
    
    try:
        forecasting_service = get_forecasting_service()
        
        # Generate synthetic 24h history
        historical_data = []
        for hour in range(24):
            historical_data.append({
                "temperature": 34.0 + np.sin(hour * np.pi / 12) * 2,
                "humidity": 60.0 + np.cos(hour * np.pi / 12) * 5
            })
        
        result = forecasting_service.predict_future(historical_data)
        
        print(f"\n Forecast Result:")
        print(f"  Current: {result['current']['temperature']}°C, {result['current']['humidity']}%")
        print(f"  6-hour forecast:")
        for i, (temp, hum) in enumerate(zip(
            result['forecasts']['temperature'],
            result['forecasts']['humidity']
        ), 1):
            print(f"    +{i}h: {temp}°C, {hum}%")
        print(f"  Trends: Temp={result['trends']['temperature']}, Hum={result['trends']['humidity']}")
        
        return True
        
    except Exception as e:
        print(f" Forecasting model test failed: {e}")
        return False


def test_rl_model():
    print("\n" + "="*60)
    print("Testing PPO RL Model")
    print("="*60)
    
    try:
        rl_service = get_rl_service()
        
        # Mock data
        current_sensors = {
            "temperature": 34.5,
            "humidity": 62.0,
            "weight": 45.2
        }
        
        audio_classification = {
            "probabilities": {
                "active": 75.0,
                "inactive": 24.0,
                "queenless": 1.0
            },
            "queenless_risk": 1.0
        }
        
        forecast_data = {
            "forecasts": {
                "temperature": [35.1, 35.3, 35.5, 35.7, 35.9, 36.1],
                "humidity": [63, 64, 65, 65, 66, 66]
            },
            "trends": {
                "temperature": "increasing",
                "humidity": "stable"
            },
            "changes": {
                "temperature": 1.6,
                "humidity": 4
            }
        }
        
        context = {
            "day_of_year": 180,
            "hour_of_day": 14,
            "hours_since_action": 24,
            "health_status": 1
        }
        
        result = rl_service.get_recommendation(
            current_sensors,
            audio_classification,
            forecast_data,
            context
        )
        
        print(f"\n Recommendation Result:")
        print(f"  Action: {result['action']}")
        print(f"  Priority: {result['priority']}")
        print(f"  Reason: {result['reason']}")
        print(f"  Cost: ${result['cost']}")
        print(f"  Duration: {result['duration_hours']}h")
        
        return True
        
    except Exception as e:
        print(f" RL model test failed: {e}")
        return False


if __name__ == "__main__":
    print("\n ML Models Test Suite")
    print("="*60)
    
    results = {
        "Audio": test_audio_model(),
        "Forecasting": test_forecasting_model(),
        "RL": test_rl_model()
    }
    
    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)
    for model, passed in results.items():
        status = " PASSED" if passed else " FAILED"
        print(f"  {model}: {status}")
    
    all_passed = all(results.values())
    print("\n" + (" All tests passed!" if all_passed else "  Some tests failed"))
    print("="*60 + "\n")