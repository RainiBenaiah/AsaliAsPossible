import 'package:flutter/material.dart';
import '../models/hive_model.dart';

/// Provider for managing hive data and state
class HiveProvider with ChangeNotifier {
  List<HiveModel> _hives = [];
  bool _isOffline = false;
  bool _isLoading = false;

  List<HiveModel> get hives => _hives;
  bool get isOffline => _isOffline;
  bool get isLoading => _isLoading;

  // ✅ Existing getters (keeping for backward compatibility)
  int get healthyHivesCount =>
      _hives.where((hive) => hive.status == 'healthy').length;

  int get warningHivesCount =>
      _hives.where((hive) => hive.status == 'warning').length;

  int get totalAlerts => _hives.fold(0, (sum, hive) => sum + hive.alerts);

  // ✅ NEW: Getters for Analytics and Map View screens
  int get healthyHiveCount =>
      _hives.where((hive) => hive.status == 'healthy').length;

  int get warningHiveCount =>
      _hives.where((hive) => hive.status == 'warning').length;

  int get criticalHiveCount =>
      _hives.where((hive) => hive.status == 'critical').length;

  // ✅ NEW: Average metrics for Analytics screen
  double get averageTemperature {
    if (_hives.isEmpty) return 0.0;
    final total = _hives.fold<double>(0, (sum, hive) => sum + hive.temperature);
    return total / _hives.length;
  }

  double get averageHumidity {
    if (_hives.isEmpty) return 0.0;
    final total = _hives.fold<double>(0, (sum, hive) => sum + hive.humidity);
    return total / _hives.length;
  }

  double get averageWeight {
    if (_hives.isEmpty) return 0.0;
    final total = _hives.fold<double>(0, (sum, hive) => sum + hive.weight);
    return total / _hives.length;
  }

  // ✅ NEW: Total hive count
  int get totalHives => _hives.length;

  // ✅ NEW: Get hives by status
  List<HiveModel> get healthyHives =>
      _hives.where((hive) => hive.status == 'healthy').toList();

  List<HiveModel> get warningHives =>
      _hives.where((hive) => hive.status == 'warning').toList();

  List<HiveModel> get criticalHives =>
      _hives.where((hive) => hive.status == 'critical').toList();

  HiveProvider() {
    _loadMockData();
  }

  /// Load mock data for testing (replace with actual API call later)
  void _loadMockData() {
    _hives = [
      HiveModel(
        id: '1',
        name: 'Hive Alpha',
        location: 'North Garden',
        latitude: -1.9403,  // Kigali coordinates (adjust for your actual locations)
        longitude: 29.8739,
        status: 'healthy',
        temperature: 34.5,
        humidity: 65.0,
        weight: 45.2,
        alerts: 0,
      ),
      HiveModel(
        id: '2',
        name: 'Hive Beta',
        location: 'South Field',
        latitude: -1.9453,  // Slightly south
        longitude: 29.8789,
        status: 'warning',
        temperature: 36.8,
        humidity: 58.0,
        weight: 42.8,
        alerts: 1,
      ),
      HiveModel(
        id: '3',
        name: 'Hive Gamma',
        location: 'East Meadow',
        latitude: -1.9353,  // Slightly north
        longitude: 29.8839, // Slightly east
        status: 'healthy',
        temperature: 33.2,
        humidity: 68.0,
        weight: 48.5,
        alerts: 0,
      ),
      HiveModel(
        id: '4',
        name: 'Hive Delta',
        location: 'West Grove',
        latitude: -1.9503,  // South-west
        longitude: 29.8689,
        status: 'critical',
        temperature: 38.5,
        humidity: 52.0,
        weight: 38.2,
        alerts: 3,
      ),
      HiveModel(
        id: '5',
        name: 'Hive Epsilon',
        location: 'Central Plot',
        latitude: -1.9403,  // Center
        longitude: 29.8789,
        status: 'healthy',
        temperature: 34.8,
        humidity: 64.0,
        weight: 46.7,
        alerts: 0,
      ),
    ];
    notifyListeners();
  }

  /// Refresh hive data (simulate API call)
  Future<void> refreshHives() async {
    _isLoading = true;
    notifyListeners();

    // Simulate network delay
    await Future.delayed(const Duration(seconds: 1));

    // In a real app, you would fetch from API here
    _loadMockData();

    _isLoading = false;
    notifyListeners();
  }

  /// Get a specific hive by ID
  HiveModel? getHiveById(String id) {
    try {
      return _hives.firstWhere((hive) => hive.id == id);
    } catch (e) {
      return null;
    }
  }

  /// Add a new hive
  void addHive(HiveModel hive) {
    _hives.add(hive);
    notifyListeners();
  }

  /// Update an existing hive
  void updateHive(HiveModel updatedHive) {
    final index = _hives.indexWhere((hive) => hive.id == updatedHive.id);
    if (index != -1) {
      _hives[index] = updatedHive;
      notifyListeners();
    }
  }

  /// Delete a hive
  void deleteHive(String id) {
    _hives.removeWhere((hive) => hive.id == id);
    notifyListeners();
  }

  /// Set offline status
  void setOffline(bool offline) {
    _isOffline = offline;
    notifyListeners();
  }

  /// Fetch hives from API (to be implemented)
  Future<void> fetchHivesFromApi() async {
    try {
      _isLoading = true;
      notifyListeners();

      // TODO: Implement actual API call
      // final response = await http.get(Uri.parse('your-api-endpoint'));
      // if (response.statusCode == 200) {
      //   final data = json.decode(response.body);
      //   _hives = (data as List)
      //       .map((item) => HiveModel.fromJson(item))
      //       .toList();
      // }

      _isLoading = false;
      _isOffline = false;
      notifyListeners();
    } catch (e) {
      _isLoading = false;
      _isOffline = true;
      notifyListeners();
      debugPrint('Error fetching hives: $e');
    }
  }
}