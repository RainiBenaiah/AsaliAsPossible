import random
from typing import Dict, List
from datetime import datetime

class MLService:
    """
    Service to integrate ML models
    In production, this would load your trained models and make predictions
    For now, we'll use mock predictions based on your notebook's model structure
    """
    
    @staticmethod
    def predict_hive_health(temperature: float, humidity: float, weight: float) -> Dict:
        """
        Predict hive health based on sensor data
        Mimics your LSTM model predictions
        """
        # Simple rule-based logic (replace with actual model later)
        health_score = 100.0
        issues = []
        
        # Temperature check (optimal: 32-36°C)
        if temperature < 30 or temperature > 38:
            health_score -= 20
            issues.append("Temperature out of range")
        elif temperature < 32 or temperature > 36:
            health_score -= 10
            issues.append("Temperature suboptimal")
        
        # Humidity check (optimal: 50-70%)
        if humidity < 40 or humidity > 80:
            health_score -= 20
            issues.append("Humidity out of range")
        elif humidity < 50 or humidity > 70:
            health_score -= 10
            issues.append("Humidity suboptimal")
        
        # Weight check (optimal: 40-50kg)
        if weight < 35 or weight > 55:
            health_score -= 20
            issues.append("Weight concerning")
        elif weight < 40 or weight > 50:
            health_score -= 10
            issues.append("Weight monitoring needed")
        
        # Determine status
        if health_score >= 80:
            status = "healthy"
        elif health_score >= 60:
            status = "warning"
        else:
            status = "critical"
        
        return {
            "health_score": max(health_score, 0),
            "status": status,
            "issues": issues,
            "alerts": len([i for i in issues if "out of range" in i or "concerning" in i])
        }
    
    @staticmethod
    def analyze_sound(sound_frequency: float = None) -> Dict:
        """
        Analyze hive sound patterns
        Mimics your audio classification model
        """
        #  sound analysis (replace with actual model)
        if sound_frequency is None:
            sound_frequency = random.uniform(200, 400)
        
        # Simple logic for demo
        queen_present = sound_frequency < 350
        swarming_probability = max(0, (sound_frequency - 300) / 100)
        
        if sound_frequency < 250:
            health_status = "Normal"
        elif sound_frequency < 350:
            health_status = "Elevated"
        else:
            health_status = "Critical"
        
        return {
            "queen_present": queen_present,
            "swarming_probability": min(swarming_probability, 1.0),
            "sound_health_status": health_status,
            "sound_frequency": sound_frequency
        }
    
    @staticmethod
    def generate_recommendations(hive_data: Dict) -> List[Dict]:
        """
        Generate AI recommendations
        Mimics your RL model's action recommendations
        """
        recommendations = []
        
        temperature = hive_data.get("temperature", 34)
        humidity = hive_data.get("humidity", 60)
        weight = hive_data.get("weight", 45)
        queen_present = hive_data.get("queen_present", True)
        swarming_prob = hive_data.get("swarming_probability", 0)
        
        # Temperature-based recommendations
        if temperature > 36:
            recommendations.append({
                "action": "VENTILATE_HIVE",
                "reason": f"Temperature at {temperature:.1f}°C - above optimal range",
                "priority": "high" if temperature > 38 else "medium"
            })
        elif temperature < 32:
            recommendations.append({
                "action": "INSULATE_HIVE",
                "reason": f"Temperature at {temperature:.1f}°C - below optimal range",
                "priority": "high" if temperature < 30 else "medium"
            })
        
        # Humidity-based recommendations
        if humidity > 70:
            recommendations.append({
                "action": "IMPROVE_VENTILATION",
                "reason": f"Humidity at {humidity:.0f}% - too high",
                "priority": "medium"
            })
        elif humidity < 50:
            recommendations.append({
                "action": "ADD_WATER_SOURCE",
                "reason": f"Humidity at {humidity:.0f}% - too low",
                "priority": "medium"
            })
        
        # Weight-based recommendations
        if weight < 40:
            recommendations.append({
                "action": "FEED_COLONY",
                "reason": f"Hive weight at {weight:.1f}kg - colony may need supplemental feeding",
                "priority": "high"
            })
        elif weight > 50:
            recommendations.append({
                "action": "HARVEST_HONEY",
                "reason": f"Hive weight at {weight:.1f}kg - ready for harvest",
                "priority": "medium"
            })
        
        # Queen-based recommendations
        if not queen_present:
            recommendations.append({
                "action": "CHECK_QUEEN",
                "reason": "Queen presence uncertain - requires inspection",
                "priority": "critical"
            })
        
        # Swarming-based recommendations
        if swarming_prob > 0.7:
            recommendations.append({
                "action": "PREVENT_SWARMING",
                "reason": f"Swarming probability at {swarming_prob*100:.0f}% - immediate action needed",
                "priority": "critical"
            })
        elif swarming_prob > 0.4:
            recommendations.append({
                "action": "MONITOR_SWARMING",
                "reason": f"Swarming probability at {swarming_prob*100:.0f}% - monitor closely",
                "priority": "high"
            })
        
        return recommendations