from datetime import datetime, timedelta
import random
from typing import List, Dict

def generate_mock_hives(user_id: str, count: int = 5) -> List[Dict]:
    """Generate mock hive data"""
    hives = []
    statuses = ["healthy", "healthy", "healthy", "warning", "critical"]
    locations = ["Sector A", "Sector B", "Sector C", "Sector D", "Sector E"]
    
    base_lat = -1.9403  # Kigali
    base_lng = 29.8739
    
    for i in range(count):
        status = statuses[i % len(statuses)]
        hive = {
            "name": f"Hive {chr(65 + i)}",  # Hive A, B, C, etc.
            "location": locations[i],
            "latitude": base_lat + random.uniform(-0.05, 0.05),
            "longitude": base_lng + random.uniform(-0.05, 0.05),
            "user_id": user_id,
            "status": status,
            "temperature": random.uniform(30, 38),
            "humidity": random.uniform(50, 75),
            "weight": random.uniform(38, 52),
            "alerts": 0 if status == "healthy" else random.randint(1, 3),
            "health_score": 90 if status == "healthy" else (70 if status == "warning" else 40),
            "last_updated": datetime.utcnow(),
            "queen_present": random.choice([True, True, True, False]),
            "swarming_probability": random.uniform(0, 0.8),
            "sound_health_status": random.choice(["Normal", "Normal", "Elevated", "Critical"]),
            "created_at": datetime.utcnow(),
        }
        hives.append(hive)
    
    return hives

def generate_mock_recommendations(user_id: str, hive_ids: List[str]) -> List[Dict]:
    """Generate mock recommendations"""
    actions = [
        ("INSPECT_HIVE", "Temperature outside optimal range", "high"),
        ("HARVEST_HONEY", "Honey level at 85% - ready for harvest", "medium"),
        ("CHECK_QUEEN", "No queen detected in last inspection", "critical"),
        ("FEED_COLONY", "Weight decreased by 15% in last week", "high"),
        ("MONITOR_CLOSELY", "Swarming probability at 65%", "medium"),
    ]
    
    recommendations = []
    for i, (action, reason, priority) in enumerate(actions[:len(hive_ids)]):
        rec = {
            "hive_id": hive_ids[i],
            "user_id": user_id,
            "action": action,
            "reason": reason,
            "priority": priority,
            "status": "active",
            "created_at": datetime.utcnow() - timedelta(hours=random.randint(1, 24)),
        }
        recommendations.append(rec)
    
    return recommendations

def generate_mock_harvests(user_id: str, hive_ids: List[str], hive_names: List[str]) -> List[Dict]:
    """Generate mock harvest data"""
    harvests = []
    qualities = ["excellent", "good", "average"]
    
    for month in range(6):
        for i, (hive_id, hive_name) in enumerate(zip(hive_ids[:3], hive_names[:3])):
            harvest = {
                "hive_id": hive_id,
                "user_id": user_id,
                "hive_name": hive_name,
                "amount_kg": random.uniform(15, 30),
                "quality": random.choice(qualities),
                "date": datetime.utcnow() - timedelta(days=30 * month + random.randint(0, 10)),
                "harvester_name": random.choice(["John Doe", "Jane Smith"]),
                "notes": "Regular harvest",
                "created_at": datetime.utcnow() - timedelta(days=30 * month),
            }
            harvests.append(harvest)
    
    return harvests

def generate_mock_history(hive_id: str, days: int = 7) -> List[Dict]:
    """Generate mock historical data for charts"""
    history = []
    
    for day in range(days):
        date = datetime.utcnow() - timedelta(days=days - day - 1)
        
        entry = {
            "hive_id": hive_id,
            "date": date,
            "temperature": random.uniform(32, 36),
            "humidity": random.uniform(55, 70),
            "weight": random.uniform(43, 48),
            "sound_frequency": random.uniform(200, 400),
        }
        history.append(entry)
    
    return history