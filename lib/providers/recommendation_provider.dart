import 'package:flutter/foundation.dart';
import '../models/recommendation_model.dart';

/// Manages recommendations and alerts
class RecommendationProvider with ChangeNotifier {
  List<RecommendationModel> _recommendations = [];

  List<RecommendationModel> get recommendations => _recommendations;
  List<RecommendationModel> get activeRecommendations =>
      _recommendations.where((r) => !r.isCompleted).toList();

  int get highPriorityCount =>
      activeRecommendations.where((r) => r.priority == 'high').length;
  int get mediumPriorityCount =>
      activeRecommendations.where((r) => r.priority == 'medium').length;
  int get lowPriorityCount =>
      activeRecommendations.where((r) => r.priority == 'low').length;

  RecommendationProvider() {
    _loadDemoData();
  }

  /// Load demo recommendation data
  void _loadDemoData() {
    _recommendations = [
      RecommendationModel(
        id: '1',      // ✅ CHANGED: 1 → '1' (String)
        hiveId: '3',  // ✅ CHANGED: 3 → '3' (String)
        priority: 'high',
        action: 'Inspect for swarming signs',
        reason: 'High temperature (38°C) detected',
        time: '2 hours ago',
      ),
      RecommendationModel(
        id: '2',      // ✅ CHANGED: 2 → '2' (String)
        hiveId: '3',  // ✅ CHANGED: 3 → '3' (String)
        priority: 'medium',
        action: 'Add ventilation',
        reason: 'Humidity below comfort zone',
        time: '4 hours ago',
      ),
      RecommendationModel(
        id: '3',      // ✅ CHANGED: 3 → '3' (String)
        hiveId: '2',  // ✅ CHANGED: 2 → '2' (String)
        priority: 'low',
        action: 'Consider harvest',
        reason: 'Weight increased 2kg in 7 days',
        time: '1 day ago',
      ),
      RecommendationModel(
        id: '4',      // ✅ CHANGED: 4 → '4' (String)
        hiveId: '1',  // ✅ CHANGED: 1 → '1' (String)
        priority: 'medium',
        action: 'Consider relocation',
        reason: 'Consistent morning shade affecting productivity',
        time: '3 days ago',
      ),
      RecommendationModel(
        id: '5',      // ✅ CHANGED: 5 → '5' (String)
        hiveId: '4',  // ✅ CHANGED: 4 → '4' (String)
        priority: 'low',
        action: 'Relocate to higher ground',
        reason: 'Moisture levels suggest poor drainage',
        time: '5 days ago',
      ),
    ];
    notifyListeners();
  }

  /// Get recommendations for specific hive
  List<RecommendationModel> getRecommendationsForHive(String hiveId) { // ✅ CHANGED: int → String
    return activeRecommendations.where((r) => r.hiveId == hiveId).toList();
  }

  /// Mark recommendation as completed
  void completeRecommendation(String id) { // ✅ CHANGED: int → String
    final index = _recommendations.indexWhere((r) => r.id == id);
    if (index != -1) {
      _recommendations[index].markCompleted();
      notifyListeners();
    }
  }

  /// Get recommendations by priority
  List<RecommendationModel> getRecommendationsByPriority(String priority) {
    return activeRecommendations.where((r) => r.priority == priority).toList();
  }
}