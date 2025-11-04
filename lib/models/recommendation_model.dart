import 'package:flutter/material.dart';

/// Represents an actionable recommendation for a hive
class RecommendationModel {
  final String id;        // ✅ CHANGED: int → String
  final String hiveId;    // ✅ CHANGED: int → String
  final String priority; // 'high', 'medium', 'low'
  final String action;
  final String reason;
  final String time;
  bool isCompleted;

  RecommendationModel({
    required this.id,
    required this.hiveId,
    required this.priority,
    required this.action,
    required this.reason,
    required this.time,
    this.isCompleted = false,
  });

  /// Create a RecommendationModel from JSON data
  factory RecommendationModel.fromJson(Map<String, dynamic> json) {
    return RecommendationModel(
      id: json['id'].toString(),        // ✅ Convert to String
      hiveId: json['hiveId'].toString(), // ✅ Convert to String
      priority: json['priority'],
      action: json['action'],
      reason: json['reason'],
      time: json['time'],
      isCompleted: json['isCompleted'] ?? false,
    );
  }

  /// Convert RecommendationModel to JSON
  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'hiveId': hiveId,
      'priority': priority,
      'action': action,
      'reason': reason,
      'time': time,
      'isCompleted': isCompleted,
    };
  }

  /// Get priority color
  Color getPriorityColor() {
    switch (priority) {
      case 'high':
        return const Color(0xFFEF4444);
      case 'medium':
        return const Color(0xFFF59E0B);
      case 'low':
        return const Color(0xFF3B82F6);
      default:
        return const Color(0xFF6B7280);
    }
  }

  /// Get priority background color
  Color getPriorityBackgroundColor() {
    switch (priority) {
      case 'high':
        return const Color(0xFFFEE2E2);
      case 'medium':
        return const Color(0xFFFEF3C7);
      case 'low':
        return const Color(0xFFDBEAFE);
      default:
        return const Color(0xFFF3F4F6);
    }
  }

  /// Get priority icon
  IconData getPriorityIcon() {
    switch (priority) {
      case 'high':
        return Icons.warning_amber_rounded;
      case 'medium':
        return Icons.info_outline_rounded;
      case 'low':
        return Icons.lightbulb_outline_rounded;
      default:
        return Icons.notifications_outlined;
    }
  }

  /// Mark recommendation as completed
  void markCompleted() {
    isCompleted = true;
  }
}