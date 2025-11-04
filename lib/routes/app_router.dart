import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import '../screens/landing_screen.dart';
import '../screens/login_screen.dart';
import '../screens/register_screen.dart';
import '../screens/dashboard_screen.dart';
import '../screens/hive_detail_screen.dart';
import '../screens/recommendations_screen.dart';
import '../screens/analytics_screen.dart';
import '../screens/settings_screen.dart';
import '../screens/profile_screen.dart';
import '../screens/map_view_screen.dart';
import '../screens/harvest_management_screen.dart'; // ✅ NEW

/// App routing configuration
class AppRouter {
  static final GoRouter router = GoRouter(
    initialLocation: '/landing',
    routes: [
      // Landing/Splash Screen
      GoRoute(
        path: '/landing',
        name: 'landing',
        builder: (context, state) => const LandingScreen(),
      ),

      // Authentication Routes
      GoRoute(
        path: '/login',
        name: 'login',
        builder: (context, state) => const LoginScreen(),
      ),
      GoRoute(
        path: '/register',
        name: 'register',
        builder: (context, state) => const RegisterScreen(),
      ),

      // Main App Routes
      GoRoute(
        path: '/dashboard',
        name: 'dashboard',
        builder: (context, state) => const DashboardScreen(),
      ),
      GoRoute(
        path: '/hive/:id',
        name: 'hiveDetail',
        builder: (context, state) {
          final id = state.pathParameters['id']!; // ✅ String ID
          return HiveDetailScreen(hiveId: id);
        },
      ),

      // Map View Route
      GoRoute(
        path: '/map',
        name: 'map',
        builder: (context, state) => const MapViewScreen(),
      ),

      // ✅ NEW: Harvest Management Route
      GoRoute(
        path: '/harvest',
        name: 'harvest',
        builder: (context, state) => const HarvestManagementScreen(),
      ),

      GoRoute(
        path: '/recommendations',
        name: 'recommendations',
        builder: (context, state) => const RecommendationsScreen(),
      ),
      GoRoute(
        path: '/analytics',
        name: 'analytics',
        builder: (context, state) => const AnalyticsScreen(),
      ),
      GoRoute(
        path: '/settings',
        name: 'settings',
        builder: (context, state) => const SettingsScreen(),
      ),
      GoRoute(
        path: '/profile',
        name: 'profile',
        builder: (context, state) => const ProfileScreen(),
      ),
    ],
    errorBuilder: (context, state) => Scaffold(
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(Icons.error_outline, size: 64, color: Colors.grey),
            const SizedBox(height: 16),
            Text(
              'Page not found',
              style: TextStyle(fontSize: 18, color: Colors.grey[600]),
            ),
            const SizedBox(height: 8),
            Text(
              state.uri.toString(),
              style: TextStyle(fontSize: 12, color: Colors.grey[400]),
            ),
          ],
        ),
      ),
    ),
  );
}