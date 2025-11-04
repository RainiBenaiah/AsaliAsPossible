import 'package:flutter/material.dart';

/// Model representing a beehive with comprehensive monitoring data
class HiveModel {
  final String id;
  final String name;
  final String location;
  final double latitude;   // For map positioning
  final double longitude;  // For map positioning
  final String status;     // 'healthy', 'warning', 'critical'
  final double temperature;
  final double humidity;
  final double weight;
  final int alerts;
  final bool queenPresent; // ✅ NEW: Queen presence indicator
  final double soundLevel; // ✅ NEW: Sound level monitoring (dB)
  final double healthScore; // ✅ NEW: Overall health score (0-100)

  HiveModel({
    required this.id,
    required this.name,
    required this.location,
    required this.latitude,
    required this.longitude,
    required this.status,
    required this.temperature,
    required this.humidity,
    required this.weight,
    this.alerts = 0,
    this.queenPresent = true,      // ✅ NEW: Default to true
    this.soundLevel = 0.0,          // ✅ NEW: Default sound level
    this.healthScore = 85.0,        // ✅ NEW: Default health score
  });

  /// Get status color based on hive health
  Color getStatusColor() {
    switch (status.toLowerCase()) {
      case 'healthy':
        return Colors.green;
      case 'warning':
        return Colors.orange;
      case 'critical':
        return Colors.red;
      default:
        return Colors.grey;
    }
  }

  // ✅ NEW: Additional helper methods

  /// Check if temperature is in optimal range (32-36°C)
  bool get isTemperatureOptimal => temperature >= 32 && temperature <= 36;

  /// Check if humidity is in optimal range (55-65%)
  bool get isHumidityOptimal => humidity >= 55 && humidity <= 65;

  /// Get temperature status message
  String get temperatureStatus {
    if (temperature > 36) return 'Too Hot';
    if (temperature < 32) return 'Too Cold';
    return 'Optimal';
  }

  /// Get humidity status message
  String get humidityStatus {
    if (humidity > 65) return 'Too Humid';
    if (humidity < 55) return 'Too Dry';
    return 'Optimal';
  }

  /// Get weight status message
  String get weightStatus {
    if (weight > 45) return 'Heavy';
    if (weight > 30) return 'Good';
    return 'Light';
  }

  /// Get health score color
  Color getHealthScoreColor() {
    if (healthScore >= 80) return Colors.green;
    if (healthScore >= 60) return Colors.orange;
    return Colors.red;
  }

  /// Get health score status
  String get healthScoreStatus {
    if (healthScore >= 80) return 'Excellent';
    if (healthScore >= 60) return 'Good';
    if (healthScore >= 40) return 'Fair';
    return 'Poor';
  }

  /// Create HiveModel from JSON
  factory HiveModel.fromJson(Map<String, dynamic> json) {
    return HiveModel(
      id: json['id']?.toString() ?? '',
      name: json['name'] ?? '',
      location: json['location'] ?? '',
      latitude: (json['latitude'] ?? 0.0).toDouble(),
      longitude: (json['longitude'] ?? 0.0).toDouble(),
      status: json['status'] ?? 'healthy',
      temperature: (json['temperature'] ?? 0.0).toDouble(),
      humidity: (json['humidity'] ?? 0.0).toDouble(),
      weight: (json['weight'] ?? 0.0).toDouble(),
      alerts: json['alerts'] ?? 0,
      queenPresent: json['queenPresent'] ?? json['queen'] ?? true,
      soundLevel: (json['soundLevel'] ?? 0.0).toDouble(),
      healthScore: (json['healthScore'] ?? 85.0).toDouble(),
    );
  }

  /// Convert HiveModel to JSON
  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'location': location,
      'latitude': latitude,
      'longitude': longitude,
      'status': status,
      'temperature': temperature,
      'humidity': humidity,
      'weight': weight,
      'alerts': alerts,
      'queenPresent': queenPresent,
      'soundLevel': soundLevel,
      'healthScore': healthScore,
    };
  }

  /// Create a copy of HiveModel with updated fields
  HiveModel copyWith({
    String? id,
    String? name,
    String? location,
    double? latitude,
    double? longitude,
    String? status,
    double? temperature,
    double? humidity,
    double? weight,
    int? alerts,
    bool? queenPresent,
    double? soundLevel,
    double? healthScore,
  }) {
    return HiveModel(
      id: id ?? this.id,
      name: name ?? this.name,
      location: location ?? this.location,
      latitude: latitude ?? this.latitude,
      longitude: longitude ?? this.longitude,
      status: status ?? this.status,
      temperature: temperature ?? this.temperature,
      humidity: humidity ?? this.humidity,
      weight: weight ?? this.weight,
      alerts: alerts ?? this.alerts,
      queenPresent: queenPresent ?? this.queenPresent,
      soundLevel: soundLevel ?? this.soundLevel,
      healthScore: healthScore ?? this.healthScore,
    );
  }

  @override
  String toString() {
    return 'HiveModel(id: $id, name: $name, status: $status, temp: $temperature°C, '
        'humidity: $humidity%, weight: ${weight}kg, healthScore: $healthScore)';
  }

  @override
  bool operator ==(Object other) {
    if (identical(this, other)) return true;
    return other is HiveModel && other.id == id;
  }

  @override
  int get hashCode => id.hashCode;
}