"""
RL Service - Enhanced with Hybrid Recommendations
State: 78 dimensions (26 per hive * 3 hives)
Features:
- Rule-based overrides for critical situations
- ML model for normal operations  
- Stochastic mode for variety
- Sanity checks to verify actions
"""

import numpy as np
from typing import Dict, List
from enum import Enum
from datetime import datetime
import pickle
from pathlib import Path

try:
    from stable_baselines3 import PPO
    PPO_AVAILABLE = True
except ImportError:
    PPO_AVAILABLE = False
    print(" stable-baselines3 not available")

class HiveAction(Enum):
    """All possible actions - matching training notebook"""
    DO_NOTHING = 0
    INSPECT_HIVE = 1
    ADD_FOOD = 2
    ADD_MEDICATION = 3
    ADJUST_VENTILATION = 4
    CONTROL_TEMPERATURE = 5
    INTRODUCE_QUEEN = 6
    SPLIT_COLONY = 7
    RELOCATE_HIVE = 8
    COMBINE_WEAK_COLONIES = 9
    HARVEST_HONEY = 10
    EMERGENCY_INTERVENTION = 11

# Action metadata from training notebook
ACTION_METADATA = {
    HiveAction.DO_NOTHING: {
        'name': 'Do Nothing',
        'description': 'Monitor hive without intervention',
        'priority': 'low',
        'cost': 0,
        'duration_hours': 0
    },
    HiveAction.INSPECT_HIVE: {
        'name': 'Inspect Hive',
        'description': 'Visual inspection to assess colony status',
        'priority': 'low',
        'cost': 5,
        'duration_hours': 1
    },
    HiveAction.ADD_FOOD: {
        'name': 'Add Food',
        'description': 'Provide sugar syrup or pollen substitute',
        'priority': 'medium',
        'cost': 10,
        'duration_hours': 1
    },
    HiveAction.ADD_MEDICATION: {
        'name': 'Add Medication',
        'description': 'Treat for Varroa mites, nosema, or other diseases',
        'priority': 'high',
        'cost': 20,
        'duration_hours': 2
    },
    HiveAction.ADJUST_VENTILATION: {
        'name': 'Adjust Ventilation',
        'description': 'Modify hive entrance or add ventilation',
        'priority': 'medium',
        'cost': 5,
        'duration_hours': 1
    },
    HiveAction.CONTROL_TEMPERATURE: {
        'name': 'Control Temperature',
        'description': 'Add insulation or shading to regulate temperature',
        'priority': 'medium',
        'cost': 15,
        'duration_hours': 2
    },
    HiveAction.INTRODUCE_QUEEN: {
        'name': 'Introduce Queen',
        'description': 'Add new queen to queenless colony',
        'priority': 'high',
        'cost': 50,
        'duration_hours': 3
    },
    HiveAction.SPLIT_COLONY: {
        'name': 'Split Colony',
        'description': 'Divide strong colony to prevent swarming',
        'priority': 'medium',
        'cost': 30,
        'duration_hours': 4
    },
    HiveAction.RELOCATE_HIVE: {
        'name': 'Relocate Hive',
        'description': 'Move hive to better location',
        'priority': 'low',
        'cost': 40,
        'duration_hours': 6
    },
    HiveAction.COMBINE_WEAK_COLONIES: {
        'name': 'Combine Weak Colonies',
        'description': 'Merge weak hive with strong one',
        'priority': 'high',
        'cost': 25,
        'duration_hours': 3
    },
    HiveAction.HARVEST_HONEY: {
        'name': 'Harvest Honey',
        'description': 'Extract honey when production is sufficient',
        'priority': 'low',
        'cost': 20,
        'duration_hours': 4
    },
    HiveAction.EMERGENCY_INTERVENTION: {
        'name': 'Emergency Intervention',
        'description': 'Critical action for colony collapse risk',
        'priority': 'critical',
        'cost': 100,
        'duration_hours': 6
    }
}

class RLService:
    """
    PPO Reinforcement Learning service with Hybrid Approach
    - Uses rules for critical situations
    - Uses ML for normal operations
    - Adds variety through stochastic predictions
    - Verifies actions make sense
    """
    
    STATE_PER_HIVE = 26
    N_HIVES_TRAINED = 3  # Model was trained with 3 hives
    TOTAL_STATE_SIZE = STATE_PER_HIVE * N_HIVES_TRAINED  # 78
    
    #  CONFIGURATION - ADJUST THESE TO TUNE BEHAVIOR
    USE_STOCHASTIC = True  # Set to False for deterministic (more consistent)
    HARVEST_WEIGHT_THRESHOLD = 47.0  # Minimum kg for harvest (was 45.0, now stricter)
    HARVEST_HONEY_LEVEL_THRESHOLD = 0.65  # Minimum honey level for harvest
    
    def __init__(self, model_path: str):
        """Load PPO model"""
        self.model = None
        self.model_path = model_path
        
        if not PPO_AVAILABLE:
            print(" PPO not available - using rule-based recommendations")
            return
        
        try:
            self.model = PPO.load(model_path)
            print(f" PPO model loaded from {model_path}")
            
            # Verify observation space
            expected_shape = self.model.observation_space.shape[0]
            if expected_shape != self.TOTAL_STATE_SIZE:
                print(f" Model expects {expected_shape} features, but we provide {self.TOTAL_STATE_SIZE}")
                print(f"   Model may not work correctly")
        except Exception as e:
            print(f" Failed to load PPO model: {e}")
            print(f"   Using rule-based recommendations")
            self.model = None
    
    def get_recommendation(
        self,
        current_sensors: Dict,
        audio_classification: Dict,
        forecast_data: Dict,
        context: Dict = None
    ) -> Dict:
        """
        Get action recommendation using HYBRID approach:
        1. Rules for critical conditions (override ML)
        2. ML model for normal operations (with stochastic variety)
        3. Sanity checks to prevent wrong actions
        """
        
        # Default context if not provided
        if context is None:
            now = datetime.utcnow()
            context = {
                'day_of_year': now.timetuple().tm_yday,
                'hour_of_day': now.hour,
                'hours_since_action': 24,
                'health_status': 1
            }
        
        # Extract key metrics for logging and rules
        temp = current_sensors.get('temperature', 34.0)
        humidity = current_sensors.get('humidity', 65.0)
        weight = current_sensors.get('weight', 45.0)
        queenless_risk = audio_classification.get('queenless_risk', 0)
        
        # Calculate honey level (how model sees it)
        honey_level = np.clip((weight - 38) / 12, 0, 1)
        
        print(f"\n    Hive Conditions:")
        print(f"      Temp: {temp:.1f}°C | Humidity: {humidity:.1f}% | Weight: {weight:.1f}kg")
        print(f"      Honey level: {honey_level:.2f} | Queenless risk: {queenless_risk:.1f}%")
        
        # ==================================================================
        # PHASE 1: CRITICAL CONDITIONS - Use Rules (Override ML)
        # ==================================================================
        
        #  CRITICAL: Queenless colony
        if queenless_risk > 50:
            print(f"       CRITICAL: Queenless detected → INTRODUCE_QUEEN")
            return self._build_recommendation_dict(
                HiveAction.INTRODUCE_QUEEN,
                'critical',
                f"Queenless risk at {queenless_risk:.1f}%, colony needs new queen urgently",
                rule_based=True
            )
        
        #  HIGH: Temperature out of range
        if temp > 38:
            print(f"       HIGH: Overheating ({temp:.1f}°C) → CONTROL_TEMPERATURE")
            return self._build_recommendation_dict(
                HiveAction.CONTROL_TEMPERATURE,
                'high',
                f"Temperature too high at {temp:.1f}°C (optimal: 32-36°C)",
                rule_based=True
            )
        
        if temp < 30:
            print(f"        HIGH: Too cold ({temp:.1f}°C) → CONTROL_TEMPERATURE")
            return self._build_recommendation_dict(
                HiveAction.CONTROL_TEMPERATURE,
                'high',
                f"Temperature too low at {temp:.1f}°C (optimal: 32-36°C)",
                rule_based=True
            )
        
        #  HIGH: Colony starving
        if weight < 38:
            print(f"       HIGH: Weight critically low ({weight:.1f}kg) → ADD_FOOD")
            return self._build_recommendation_dict(
                HiveAction.ADD_FOOD,
                'high',
                f"Weight critically low at {weight:.1f}kg, colony needs feeding",
                rule_based=True
            )
        
        # ==================================================================
        # PHASE 2: NORMAL CONDITIONS - Use ML Model
        # ==================================================================
        
        if self.model is None:
            print(f"        Model not available, using rules")
            return self._get_rule_based_recommendation(
                current_sensors, audio_classification, forecast_data, context
            )
        
        try:
            # Build 78-dimensional state
            state = self.build_state_vector_78(
                current_sensors,
                audio_classification,
                forecast_data,
                context
            )
            
            #  Predict action with stochastic mode for variety
            action_index, _states = self.model.predict(
                state, 
                deterministic=not self.USE_STOCHASTIC 
            )
            action_index = int(action_index)
            
            # Decode action
            hive_idx = action_index // len(HiveAction)
            action_type_idx = action_index % len(HiveAction)
            action_enum = HiveAction(action_type_idx)
            
            mode = "stochastic" if self.USE_STOCHASTIC else "deterministic"
            print(f"       Model suggests: {action_enum.name} ({mode})")
            
            # ==================================================================
            # PHASE 3: SANITY CHECKS - Verify ML suggestion makes sense
            # ==================================================================
            
            #  Check 1: Don't harvest if not ready
            if action_enum == HiveAction.HARVEST_HONEY:
                if weight < self.HARVEST_WEIGHT_THRESHOLD:
                    print(f"        Override: Weight {weight:.1f}kg < {self.HARVEST_WEIGHT_THRESHOLD}kg threshold")
                    print(f"       Changed to INSPECT_HIVE")
                    action_enum = HiveAction.INSPECT_HIVE
                elif honey_level < self.HARVEST_HONEY_LEVEL_THRESHOLD:
                    print(f"        Override: Honey level {honey_level:.2f} < {self.HARVEST_HONEY_LEVEL_THRESHOLD} threshold")
                    print(f"       Changed to INSPECT_HIVE")
                    action_enum = HiveAction.INSPECT_HIVE
                else:
                    print(f"       HARVEST verified: weight={weight:.1f}kg, honey_level={honey_level:.2f}")
            
            #  Check 2: Don't do nothing if there are issues
            if action_enum == HiveAction.DO_NOTHING:
                if temp > 36 or temp < 32:
                    print(f"        Override: Temp {temp:.1f}°C out of ideal range (32-36°C)")
                    print(f"       Changed to CONTROL_TEMPERATURE")
                    action_enum = HiveAction.CONTROL_TEMPERATURE
                elif humidity > 70 or humidity < 50:
                    print(f"        Override: Humidity {humidity:.1f}% out of range (50-70%)")
                    print(f"      → Changed to ADJUST_VENTILATION")
                    action_enum = HiveAction.ADJUST_VENTILATION
                elif weight < 40:
                    print(f"        Override: Weight {weight:.1f}kg is low")
                    print(f"       Changed to ADD_FOOD")
                    action_enum = HiveAction.ADD_FOOD
            
            #  Check 3: Don't introduce queen if already present
            if action_enum == HiveAction.INTRODUCE_QUEEN:
                if audio_classification.get('queen_present', True) and queenless_risk < 30:
                    print(f"        Override: Queen likely present (risk only {queenless_risk:.1f}%)")
                    print(f"       Changed to INSPECT_HIVE")
                    action_enum = HiveAction.INSPECT_HIVE
            
            #  Check 4: Verify ADD_FOOD is appropriate
            if action_enum == HiveAction.ADD_FOOD:
                if weight > 48:
                    print(f"        Override: Weight {weight:.1f}kg is already high")
                    print(f"       Changed to INSPECT_HIVE")
                    action_enum = HiveAction.INSPECT_HIVE
            
            print(f"       Action approved: {action_enum.name}")
            
            # Build final recommendation
            action_meta = ACTION_METADATA[action_enum]
            reason = self._generate_reason(
                action_enum,
                current_sensors,
                audio_classification,
                forecast_data
            )
            
            return {
                'action': action_meta['name'].upper().replace(' ', '_'),
                'action_index': action_enum.value,
                'priority': action_meta['priority'],
                'description': action_meta['description'],
                'reason': reason,
                'confidence': 80 if self.USE_STOCHASTIC else 90,
                'cost': action_meta['cost'],
                'duration_hours': action_meta['duration_hours'],
                'mock_mode': False,
                'model_used': 'PPO-Stochastic' if self.USE_STOCHASTIC else 'PPO-Deterministic',
                'hive_suggested': hive_idx,
                'sanity_checked': True
            }
            
        except Exception as e:
            print(f"        ML failed: {e}")
            print(f"       Falling back to rules")
            import traceback
            traceback.print_exc()
            return self._get_rule_based_recommendation(
                current_sensors,
                audio_classification,
                forecast_data,
                context
            )
    
    def _build_recommendation_dict(
        self,
        action: HiveAction,
        priority: str,
        reason: str,
        rule_based: bool = True
    ) -> Dict:
        """Helper to build recommendation dictionary"""
        action_meta = ACTION_METADATA[action]
        
        return {
            'action': action_meta['name'].upper().replace(' ', '_'),
            'action_index': action.value,
            'priority': priority,
            'description': action_meta['description'],
            'reason': reason,
            'confidence': 95,  # High confidence for rule-based
            'cost': action_meta['cost'],
            'duration_hours': action_meta['duration_hours'],
            'mock_mode': False,
            'model_used': 'Rules' if rule_based else 'Hybrid',
            'sanity_checked': False
        }
    
    def build_state_vector_78(
        self,
        current_sensors: Dict,
        audio_classification: Dict,
        forecast_data: Dict,
        context: Dict
    ) -> np.ndarray:
        """
        Build 78-dimensional state vector matching training notebook
        26 features per hive × 3 hives = 78 total
        
        Per hive (26 features):
        - Audio (4): 3 class probabilities + max confidence
        - Current sensors (2): temp, humidity (normalized)
        - Rolling stats (8): temp/humidity 6h and 24h means and stds
        - Time features (5): hour, day, month, day_of_week, is_weekend
        - Hive status (3): honey_level, colony_strength, days_since_action
        - LSTM forecasts (4): temp_6h, hum_6h, temp_trend, hum_trend
        """
        state = []
        
        # Build state for 3 hives (model expects this)
        # Hive 0 = real hive, Hives 1-2 = dummy hives with same values
        for hive_idx in range(self.N_HIVES_TRAINED):
            hive_state = []
            
            # 1. Audio features (4 dimensions)
            probs = audio_classification.get('probabilities', {})
            active_prob = probs.get('active', 50.0) / 100.0
            inactive_prob = probs.get('inactive', 25.0) / 100.0
            queenless_prob = probs.get('queenless', 25.0) / 100.0
            max_confidence = max(active_prob, inactive_prob, queenless_prob)
            
            hive_state.extend([
                active_prob,
                inactive_prob,
                queenless_prob,
                max_confidence
            ])
            
            # 2. Current sensors (2 dimensions - normalized)
            temp = current_sensors.get('temperature', 34.0)
            humidity = current_sensors.get('humidity', 65.0)
            hive_state.extend([
                temp / 50.0,  # Normalize to 0-1 range
                humidity / 100.0
            ])
            
            # 3. Rolling stats (8 dimensions)
            # Use current values as approximation if rolling stats not available
            hive_state.extend([
                temp / 50.0,  # temp_roll6h_mean
                1.0 / 10.0,   # temp_roll6h_std (assume 1°C std)
                temp / 50.0,  # temp_roll24h_mean
                1.0 / 10.0,   # temp_roll24h_std
                humidity / 100.0,  # humidity_roll6h_mean
                5.0 / 20.0,   # humidity_roll6h_std (assume 5% std)
                humidity / 100.0,  # humidity_roll24h_mean
                5.0 / 20.0    # humidity_roll24h_std
            ])
            
            # 4. Time features (5 dimensions)
            now = datetime.utcnow()
            hour = context.get('hour_of_day', now.hour)
            day = now.day
            month = now.month
            day_of_week = now.weekday()
            is_weekend = 1.0 if day_of_week >= 5 else 0.0
            
            hive_state.extend([
                hour / 24.0,
                day / 31.0,
                month / 12.0,
                day_of_week / 7.0,
                is_weekend
            ])
            
            # 5. Hive status (3 dimensions)
            # Estimate based on available data
            weight = current_sensors.get('weight', 45.0)
            honey_level = np.clip((weight - 38) / 12, 0, 1)  # 38-50kg range
            
            health_status = context.get('health_status', 1)
            colony_strength = 0.9 if health_status == 2 else (0.6 if health_status == 1 else 0.3)
            
            days_since_action = context.get('hours_since_action', 24) / 24.0
            
            hive_state.extend([
                honey_level,
                colony_strength,
                days_since_action / 30.0  # Normalize to 0-1 (30 days max)
            ])
            
            # 6. LSTM forecasts (4 dimensions)
            # Extract 6-hour forecasts from forecast_data
            forecasts = forecast_data.get('forecasts', {})
            temp_forecasts = forecasts.get('temperature', [temp] * 6)
            hum_forecasts = forecasts.get('humidity', [humidity] * 6)
            
            # Get 6-hour ahead prediction (index 5)
            temp_6h = temp_forecasts[min(5, len(temp_forecasts)-1)]
            hum_6h = hum_forecasts[min(5, len(hum_forecasts)-1)]
            
            # Calculate trends
            temp_trend = temp_6h - temp
            hum_trend = hum_6h - humidity
            
            hive_state.extend([
                temp_6h / 50.0,
                hum_6h / 100.0,
                np.clip(temp_trend / 10.0, -1, 1),  # Normalize trend
                np.clip(hum_trend / 20.0, -1, 1)
            ])
            
            # Add this hive's 26 features to state
            state.extend(hive_state)
        
        # Should be exactly 78 dimensions (26 × 3)
        state_array = np.array(state, dtype=np.float32)
        
        if len(state_array) != self.TOTAL_STATE_SIZE:
            print(f"⚠ Warning: State size is {len(state_array)}, expected {self.TOTAL_STATE_SIZE}")
        
        return state_array
    
    def _get_rule_based_recommendation(
        self,
        current_sensors: Dict,
        audio_classification: Dict,
        forecast_data: Dict,
        context: Dict
    ) -> Dict:
        """Rule-based recommendation fallback"""
        temp = current_sensors['temperature']
        hum = current_sensors['humidity']
        weight = current_sensors['weight']
        queenless_risk = audio_classification.get('queenless_risk', 0)
        
        # Determine action based on conditions
        action = None
        priority = 'medium'
        
        # Critical conditions
        if queenless_risk > 50:
            action = HiveAction.INTRODUCE_QUEEN
            priority = 'critical'
        elif temp > 38 or temp < 30:
            action = HiveAction.CONTROL_TEMPERATURE
            priority = 'high'
        elif weight < 38:
            action = HiveAction.ADD_FOOD
            priority = 'high'
        # Warning conditions
        elif temp > 36 or temp < 32:
            action = HiveAction.CONTROL_TEMPERATURE
            priority = 'medium'
        elif hum > 70 or hum < 50:
            action = HiveAction.ADJUST_VENTILATION
            priority = 'medium'
        elif weight < 40:
            action = HiveAction.ADD_FOOD
            priority = 'medium'
        elif weight > self.HARVEST_WEIGHT_THRESHOLD:
            action = HiveAction.HARVEST_HONEY
            priority = 'low'
        # Default action
        else:
            action = HiveAction.INSPECT_HIVE
            priority = 'low'
        
        action_meta = ACTION_METADATA[action]
        reason = self._generate_reason(action, current_sensors, audio_classification, forecast_data)
        
        return {
            'action': action_meta['name'].upper().replace(' ', '_'),
            'action_index': action.value,
            'priority': priority,
            'description': action_meta['description'],
            'reason': reason,
            'confidence': 85,
            'cost': action_meta['cost'],
            'duration_hours': action_meta['duration_hours'],
            'mock_mode': True,
            'model_used': 'Rules-Only'
        }
    
    def _generate_reason(
        self,
        action: HiveAction,
        sensors: Dict,
        audio: Dict,
        forecast: Dict
    ) -> str:
        """Generate reason for action"""
        temp = sensors['temperature']
        hum = sensors['humidity']
        weight = sensors['weight']
        queenless_risk = audio.get('queenless_risk', 0)
        
        trends = forecast.get('trends', {})
        temp_trend = trends.get('temperature', 'stable')
        
        reasons = {
            HiveAction.DO_NOTHING: "All parameters within optimal range, colony healthy",
            HiveAction.INSPECT_HIVE: "Routine inspection recommended",
            HiveAction.ADD_FOOD: f"Weight at {weight:.1f}kg, colony may need supplemental feeding",
            HiveAction.ADD_MEDICATION: "Health indicators suggest potential disease risk",
            HiveAction.ADJUST_VENTILATION: f"Humidity at {hum:.0f}%, ventilation adjustment needed",
            HiveAction.CONTROL_TEMPERATURE: f"Temperature {temp_trend} (currently {temp:.1f}°C)",
            HiveAction.INTRODUCE_QUEEN: f"Queenless risk at {queenless_risk:.1f}%, colony needs new queen",
            HiveAction.SPLIT_COLONY: f"Colony strong, splitting recommended to prevent swarming",
            HiveAction.RELOCATE_HIVE: "Environmental conditions suggest relocation beneficial",
            HiveAction.COMBINE_WEAK_COLONIES: f"Weight low at {weight:.1f}kg, consider combining",
            HiveAction.HARVEST_HONEY: f"Weight at {weight:.1f}kg indicates honey ready for harvest",
            HiveAction.EMERGENCY_INTERVENTION: "Critical conditions detected: immediate action required"
        }
        
        return reasons.get(action, "Action recommended based on current conditions")


# Singleton instance
_rl_service_instance = None

def get_rl_service() -> RLService:
    """Get singleton instance of RLService"""
    global _rl_service_instance
    
    if _rl_service_instance is None:
        model_path = "ml_models/rl/ppo_beehive_final.zip"
        _rl_service_instance = RLService(model_path)
    
    return _rl_service_instance