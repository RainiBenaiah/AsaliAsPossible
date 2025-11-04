import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';

/// Manages app theme (dark/light mode)
class ThemeProvider with ChangeNotifier {
  bool _isDarkMode = false;

  bool get isDarkMode => _isDarkMode;

  ThemeProvider() {
    _loadThemePreference();
  }

  /// Load saved theme preference
  Future<void> _loadThemePreference() async {
    final prefs = await SharedPreferences.getInstance();
    _isDarkMode = prefs.getBool('isDarkMode') ?? false;
    notifyListeners();
  }

  /// Toggle between dark and light mode
  Future<void> toggleTheme() async {
    _isDarkMode = !_isDarkMode;
    final prefs = await SharedPreferences.getInstance();
    await prefs.setBool('isDarkMode', _isDarkMode);
    notifyListeners();
  }

  /// Get theme data based on current mode
  ThemeData get themeData {
    return _isDarkMode ? _darkTheme : _lightTheme;
  }

  /// Light theme configuration
  static final ThemeData _lightTheme = ThemeData(
    brightness: Brightness.light,
    primaryColor: const Color(0xFFF59E0B),
    scaffoldBackgroundColor: const Color(0xFFF9FAFB),
    cardColor: Colors.white,
    colorScheme: const ColorScheme.light(
      primary: Color(0xFFF59E0B),
      secondary: Color(0xFFFB923C),
      surface: Colors.white,
      background: Color(0xFFF9FAFB),
    ),
  );

  /// Dark theme configuration
  static final ThemeData _darkTheme = ThemeData(
    brightness: Brightness.dark,
    primaryColor: const Color(0xFFF59E0B),
    scaffoldBackgroundColor: const Color(0xFF111827),
    cardColor: const Color(0xFF1F2937),
    colorScheme: const ColorScheme.dark(
      primary: Color(0xFFF59E0B),
      secondary: Color(0xFFFB923C),
      surface: Color(0xFF1F2937),
      background: Color(0xFF111827),
    ),
  );
}