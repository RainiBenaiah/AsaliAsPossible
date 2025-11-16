"""
RL Storage Service
Saves PPO RL training data and episodes to MongoDB Atlas
"""

from datetime import datetime
from typing import Dict, List, Optional
from bson import ObjectId
import uuid


async def create_rl_episode(hive_id: str, user_id: str) -> str:
    """
    Create a new RL training episode
    
    Args:
        hive_id: Hive ID
        user_id: User email
    
    Returns:
        Episode ID
    """
    episode_id = f"ep_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
    
    from database.connection import get_rl_episodes_collection
    
    episodes_collection = get_rl_episodes_collection()
    
    episode_doc = {
        "episode_id": episode_id,
        "hive_id": hive_id,
        "user_id": user_id,
        "started_at": datetime.utcnow(),
        "status": "active",
        "total_steps": 0,
        "total_reward": 0.0,
        "actions_taken": {},
        "health_progression": []
    }
    
    await episodes_collection.insert_one(episode_doc)
    
    print(f"Created RL episode: {episode_id}")
    
    return episode_id


async def save_rl_step(
    episode_id: str,
    hive_id: str,
    user_id: str,
    state: Dict,
    action: str,
    action_encoded: int,
    reward: float,
    reward_components: Dict,
    next_state: Dict,
    done: bool,
    step: int,
    value_estimate: float = None,
    action_log_prob: float = None,
    advantage: float = None
):
    """
    Save a single RL training step
    
    Args:
        episode_id: Episode ID
        hive_id: Hive ID
        user_id: User email
        state: Current state observation
        action: Action taken (string)
        action_encoded: Action index
        reward: Reward received
        reward_components: Breakdown of reward
        next_state: Next state observation
        done: Whether episode is done
        step: Step number in episode
        value_estimate: Value function estimate
        action_log_prob: Log probability of action
        advantage: Advantage estimate
    
    Returns:
        Document ID of saved step
    """
    from database.connection import get_rl_training_collection
    
    training_collection = get_rl_training_collection()
    
    step_doc = {
        "episode_id": episode_id,
        "hive_id": hive_id,
        "user_id": user_id,
        "timestamp": datetime.utcnow(),
        
        # State
        "state": state,
        
        # Action
        "action": action,
        "action_encoded": action_encoded,
        
        # Reward
        "reward": reward,
        "reward_components": reward_components,
        
        # Next state
        "next_state": next_state,
        
        # Episode info
        "episode_step": step,
        "done": done,
        
        # PPO specific
        "value_estimate": value_estimate,
        "action_log_prob": action_log_prob,
        "advantage": advantage,
        
        "metadata": {
            "training_version": "ppo_v1.0"
        }
    }
    
    result = await training_collection.insert_one(step_doc)
    
    return str(result.inserted_id)


async def update_rl_episode(
    episode_id: str,
    total_reward: float = None,
    actions_taken: Dict = None,
    health_score: float = None,
    training_metrics: Dict = None
):
    """
    Update RL episode with accumulated statistics
    
    Args:
        episode_id: Episode ID
        total_reward: Cumulative reward
        actions_taken: Action counts
        health_score: Current health score
        training_metrics: Training metrics (loss, etc.)
    
    Returns:
        Success boolean
    """
    from database.connection import get_rl_episodes_collection
    
    episodes_collection = get_rl_episodes_collection()
    
    update_doc = {}
    
    if total_reward is not None:
        update_doc["total_reward"] = total_reward
        update_doc["total_steps"] = {"$inc": 1}
    
    if actions_taken is not None:
        update_doc["actions_taken"] = actions_taken
    
    if health_score is not None:
        update_doc["$push"] = {
            "health_progression": {
                "timestamp": datetime.utcnow(),
                "health_score": health_score
            }
        }
    
    if training_metrics is not None:
        update_doc["training_info"] = training_metrics
    
    result = await episodes_collection.update_one(
        {"episode_id": episode_id},
        {"$set": update_doc}
    )
    
    return result.modified_count > 0


async def complete_rl_episode(
    episode_id: str,
    final_metrics: Dict,
    training_metrics: Dict = None
):
    """
    Mark episode as complete and save final statistics
    
    Args:
        episode_id: Episode ID
        final_metrics: Final episode metrics
        training_metrics: Training performance metrics
    
    Returns:
        Success boolean
    """
    from database.connection import get_rl_episodes_collection, get_rl_training_collection
    
    episodes_collection = get_rl_episodes_collection()
    training_collection = get_rl_training_collection()
    
    # Get episode start time
    episode = await episodes_collection.find_one({"episode_id": episode_id})
    
    if not episode:
        return False
    
    # Count total steps
    total_steps = await training_collection.count_documents({"episode_id": episode_id})
    
    # Calculate average reward
    pipeline = [
        {"$match": {"episode_id": episode_id}},
        {"$group": {
            "_id": None,
            "avg_reward": {"$avg": "$reward"},
            "total_reward": {"$sum": "$reward"}
        }}
    ]
    
    cursor = training_collection.aggregate(pipeline)
    results = await cursor.to_list(length=1)
    
    avg_reward = results[0]["avg_reward"] if results else 0
    total_reward = results[0]["total_reward"] if results else 0
    
    # Update episode
    ended_at = datetime.utcnow()
    duration_minutes = (ended_at - episode["started_at"]).total_seconds() / 60
    
    update_doc = {
        "status": "completed",
        "ended_at": ended_at,
        "duration_minutes": duration_minutes,
        "total_steps": total_steps,
        "total_reward": total_reward,
        "average_reward": avg_reward,
        "final_metrics": final_metrics
    }
    
    if training_metrics:
        update_doc["training_info"] = training_metrics
    
    result = await episodes_collection.update_one(
        {"episode_id": episode_id},
        {"$set": update_doc}
    )
    
    print(f"Episode {episode_id} completed: {total_steps} steps, reward: {total_reward:.2f}")
    
    return result.modified_count > 0


async def get_rl_episode_data(episode_id: str):
    """
    Get all data for an RL episode
    
    Args:
        episode_id: Episode ID
    
    Returns:
        Dictionary with episode and all steps
    """
    from database.connection import get_rl_episodes_collection, get_rl_training_collection
    
    episodes_collection = get_rl_episodes_collection()
    training_collection = get_rl_training_collection()
    
    # Get episode
    episode = await episodes_collection.find_one({"episode_id": episode_id})
    
    if not episode:
        return None
    
    # Get all steps
    cursor = training_collection.find({"episode_id": episode_id}).sort("episode_step", 1)
    steps = await cursor.to_list(length=10000)
    
    # Convert ObjectIds
    episode["_id"] = str(episode["_id"])
    for step in steps:
        step["_id"] = str(step["_id"])
    
    return {
        "episode": episode,
        "steps": steps
    }


async def get_rl_training_statistics(hive_id: str = None, user_id: str = None, limit: int = 10):
    """
    Get RL training statistics
    
    Args:
        hive_id: Optional hive filter
        user_id: Optional user filter
        limit: Number of recent episodes
    
    Returns:
        Statistics dictionary
    """
    from database.connection import get_rl_episodes_collection
    
    episodes_collection = get_rl_episodes_collection()
    
    # Build query
    query = {"status": "completed"}
    if hive_id:
        query["hive_id"] = hive_id
    if user_id:
        query["user_id"] = user_id
    
    # Get recent episodes
    cursor = episodes_collection.find(query).sort("started_at", -1).limit(limit)
    episodes = await cursor.to_list(length=limit)
    
    if not episodes:
        return {"error": "No completed episodes found"}
    
    # Calculate statistics
    total_episodes = len(episodes)
    avg_reward = sum(ep.get("total_reward", 0) for ep in episodes) / total_episodes
    avg_steps = sum(ep.get("total_steps", 0) for ep in episodes) / total_episodes
    
    # Best episode
    best_episode = max(episodes, key=lambda ep: ep.get("total_reward", 0))
    
    stats = {
        "total_episodes": total_episodes,
        "average_reward": round(avg_reward, 2),
        "average_steps": round(avg_steps, 1),
        "best_episode": {
            "episode_id": best_episode["episode_id"],
            "reward": best_episode.get("total_reward", 0),
            "steps": best_episode.get("total_steps", 0),
            "date": best_episode.get("started_at")
        },
        "recent_episodes": [
            {
                "episode_id": ep["episode_id"],
                "reward": ep.get("total_reward", 0),
                "steps": ep.get("total_steps", 0),
                "duration_minutes": ep.get("duration_minutes", 0),
                "date": ep.get("started_at")
            }
            for ep in episodes[:5]
        ]
    }
    
    return stats


async def cleanup_old_rl_data(days_to_keep: int = 90):
    """
    Remove RL training data older than specified days
    
    Args:
        days_to_keep: Number of days to keep
    
    Returns:
        Number of episodes and steps deleted
    """
    from database.connection import get_rl_episodes_collection, get_rl_training_collection
    from datetime import timedelta
    
    episodes_collection = get_rl_episodes_collection()
    training_collection = get_rl_training_collection()
    
    cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)
    
    # Find old episodes
    cursor = episodes_collection.find({
        "started_at": {"$lt": cutoff_date}
    })
    old_episodes = await cursor.to_list(length=10000)
    old_episode_ids = [ep["episode_id"] for ep in old_episodes]
    
    # Delete episodes
    episodes_result = await episodes_collection.delete_many({
        "episode_id": {"$in": old_episode_ids}
    })
    
    # Delete training steps
    steps_result = await training_collection.delete_many({
        "episode_id": {"$in": old_episode_ids}
    })
    
    print(f"Cleaned up {episodes_result.deleted_count} episodes and {steps_result.deleted_count} training steps")
    
    return {
        "episodes_deleted": episodes_result.deleted_count,
        "steps_deleted": steps_result.deleted_count
    }