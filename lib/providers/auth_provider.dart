import 'package:flutter/foundation.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../models/user_model.dart';

/// Manages user authentication state
class AuthProvider with ChangeNotifier {
  UserModel? _currentUser;
  bool _isLoading = false;
  String? _errorMessage;

  UserModel? get currentUser => _currentUser;
  bool get isLoading => _isLoading;
  String? get errorMessage => _errorMessage;
  bool get isAuthenticated => _currentUser != null;

  /// Login user with email and password
  Future<bool> login(String email, String password) async {
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();

    try {
      // Simulate API call
      await Future.delayed(const Duration(seconds: 1));

      // Demo credentials
      if (email == 'demo@asali.com' && password == 'demo123') {
        _currentUser = UserModel(
          id: '1',
          name: 'John Beekeeper',
          email: email,
          phoneNumber: '+250788123456',
          createdAt: DateTime.now(),
        );

        // Save login state
        final prefs = await SharedPreferences.getInstance();
        await prefs.setBool('isLoggedIn', true);
        await prefs.setString('userId', _currentUser!.id);

        _isLoading = false;
        notifyListeners();
        return true;
      } else {
        _errorMessage = 'Invalid email or password';
        _isLoading = false;
        notifyListeners();
        return false;
      }
    } catch (e) {
      _errorMessage = 'Login failed. Please try again.';
      _isLoading = false;
      notifyListeners();
      return false;
    }
  }

  /// NEW: Login with Google (Demo implementation)
  Future<bool> loginWithGoogle() async {
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();

    try {
      // Simulate Google Sign-In process
      await Future.delayed(const Duration(seconds: 2));

      // In real implementation, use google_sign_in package
      // For demo, create a Google user
      _currentUser = UserModel(
        id: DateTime.now().millisecondsSinceEpoch.toString(),
        name: 'Google User',
        email: 'user@gmail.com',
        phoneNumber: null,
        profileImageUrl: null, // In real app, get from Google
        createdAt: DateTime.now(),
      );

      // Save login state
      final prefs = await SharedPreferences.getInstance();
      await prefs.setBool('isLoggedIn', true);
      await prefs.setString('userId', _currentUser!.id);
      await prefs.setString('loginMethod', 'google'); // Track login method

      _isLoading = false;
      notifyListeners();
      return true;
    } catch (e) {
      _errorMessage = 'Google Sign-In failed. Please try again.';
      _isLoading = false;
      notifyListeners();
      return false;
    }
  }

  /// Register new user
  Future<bool> register(String name, String email, String password) async {
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();

    try {
      // Simulate API call
      await Future.delayed(const Duration(seconds: 1));

      _currentUser = UserModel(
        id: DateTime.now().millisecondsSinceEpoch.toString(),
        name: name,
        email: email,
        createdAt: DateTime.now(),
      );

      // Save login state
      final prefs = await SharedPreferences.getInstance();
      await prefs.setBool('isLoggedIn', true);
      await prefs.setString('userId', _currentUser!.id);
      await prefs.setString('loginMethod', 'email'); // Track login method

      _isLoading = false;
      notifyListeners();
      return true;
    } catch (e) {
      _errorMessage = 'Registration failed. Please try again.';
      _isLoading = false;
      notifyListeners();
      return false;
    }
  }

  /// Logout current user
  Future<void> logout() async {
    _currentUser = null;
    final prefs = await SharedPreferences.getInstance();

    // Check if user logged in with Google
    final loginMethod = prefs.getString('loginMethod');
    if (loginMethod == 'google') {
      // In real app, sign out from Google
      // await GoogleSignIn().signOut();
    }

    await prefs.clear();
    notifyListeners();
  }

  /// Check if user is already logged in
  Future<void> checkLoginStatus() async {
    final prefs = await SharedPreferences.getInstance();
    final isLoggedIn = prefs.getBool('isLoggedIn') ?? false;

    if (isLoggedIn) {
      // Load user data (in real app, fetch from API)
      final loginMethod = prefs.getString('loginMethod') ?? 'email';

      _currentUser = UserModel(
        id: prefs.getString('userId') ?? '1',
        name: loginMethod == 'google' ? 'Google User' : 'John Beekeeper',
        email: loginMethod == 'google' ? 'user@gmail.com' : 'demo@asali.com',
        phoneNumber: loginMethod == 'google' ? null : '+250788123456',
        createdAt: DateTime.now(),
      );
      notifyListeners();
    }
  }

  /// Update user profile
  Future<bool> updateProfile(String name, String? phoneNumber) async {
    if (_currentUser == null) return false;

    _isLoading = true;
    notifyListeners();

    try {
      // Simulate API call
      await Future.delayed(const Duration(seconds: 1));

      _currentUser = UserModel(
        id: _currentUser!.id,
        name: name,
        email: _currentUser!.email,
        phoneNumber: phoneNumber,
        profileImageUrl: _currentUser!.profileImageUrl,
        createdAt: _currentUser!.createdAt,
      );

      _isLoading = false;
      notifyListeners();
      return true;
    } catch (e) {
      _isLoading = false;
      notifyListeners();
      return false;
    }
  }

/*
  // FUTURE: Real Google Sign-In Implementation
  // Uncomment and use when ready to implement real Google Sign-In

  final GoogleSignIn _googleSignIn = GoogleSignIn();

  Future<bool> loginWithGoogleReal() async {
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();

    try {
      final GoogleSignInAccount? googleUser = await _googleSignIn.signIn();

      if (googleUser == null) {
        _errorMessage = 'Google Sign-In cancelled';
        _isLoading = false;
        notifyListeners();
        return false;
      }

      final GoogleSignInAuthentication googleAuth = await googleUser.authentication;

      // Send googleAuth.idToken to your backend for verification
      // Backend should return user data

      _currentUser = UserModel(
        id: googleUser.id,
        name: googleUser.displayName ?? 'Google User',
        email: googleUser.email,
        profileImageUrl: googleUser.photoUrl,
        createdAt: DateTime.now(),
      );

      final prefs = await SharedPreferences.getInstance();
      await prefs.setBool('isLoggedIn', true);
      await prefs.setString('userId', _currentUser!.id);
      await prefs.setString('loginMethod', 'google');

      _isLoading = false;
      notifyListeners();
      return true;
    } catch (e) {
      _errorMessage = 'Google Sign-In failed: $e';
      _isLoading = false;
      notifyListeners();
      return false;
    }
  }
  */
}