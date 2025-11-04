import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:provider/provider.dart';
import '../providers/hive_provider.dart';
import '../providers/recommendation_provider.dart';
import '../providers/theme_provider.dart';

/// Enhanced Interactive Landing Screen with animations
class LandingScreen extends StatefulWidget {
  const LandingScreen({super.key});

  @override
  State<LandingScreen> createState() => _LandingScreenState();
}

class _LandingScreenState extends State<LandingScreen>
    with SingleTickerProviderStateMixin {
  late AnimationController _animationController;
  late Animation<double> _fadeAnimation;
  late Animation<Offset> _slideAnimation;
  late Animation<double> _scaleAnimation;

  @override
  void initState() {
    super.initState();
    _animationController = AnimationController(
      duration: const Duration(milliseconds: 1200),
      vsync: this,
    );

    _fadeAnimation = Tween<double>(begin: 0.0, end: 1.0).animate(
      CurvedAnimation(
        parent: _animationController,
        curve: const Interval(0.0, 0.5, curve: Curves.easeOut),
      ),
    );

    _slideAnimation = Tween<Offset>(
      begin: const Offset(0, 0.3),
      end: Offset.zero,
    ).animate(
      CurvedAnimation(
        parent: _animationController,
        curve: const Interval(0.2, 0.8, curve: Curves.easeOutCubic),
      ),
    );

    _scaleAnimation = Tween<double>(begin: 0.8, end: 1.0).animate(
      CurvedAnimation(
        parent: _animationController,
        curve: const Interval(0.3, 1.0, curve: Curves.easeOutBack),
      ),
    );

    _animationController.forward();
  }

  @override
  void dispose() {
    _animationController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final hiveProvider = Provider.of<HiveProvider>(context);
    final recProvider = Provider.of<RecommendationProvider>(context);
    final themeProvider = Provider.of<ThemeProvider>(context);
    final isDark = themeProvider.isDarkMode;

    return Scaffold(
      body: Container(
        decoration: BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
            colors: isDark
                ? [
              const Color(0xFF1F2937),
              const Color(0xFF111827),
              const Color(0xFF0F172A),
            ]
                : [
              const Color(0xFFFFFBEB),
              const Color(0xFFFEF3C7),
              const Color(0xFFFED7AA),
            ],
          ),
        ),
        child: SafeArea(
          child: SingleChildScrollView(
            // ✅ FIX: Added ScrollView
            physics: const BouncingScrollPhysics(), // ✅ Smooth bouncy scroll
            child: Padding(
              padding: const EdgeInsets.all(24.0),
              child: Column(
                children: [
                  // Dark Mode Toggle with animation
                  FadeTransition(
                    opacity: _fadeAnimation,
                    child: Align(
                      alignment: Alignment.topRight,
                      child: TweenAnimationBuilder<double>(
                        tween: Tween(begin: 0.0, end: 1.0),
                        duration: const Duration(milliseconds: 500),
                        builder: (context, value, child) {
                          return Transform.rotate(
                            angle: value * 3.14159,
                            child: child,
                          );
                        },
                        child: IconButton(
                          icon: Icon(
                            isDark ? Icons.light_mode : Icons.dark_mode,
                            color: isDark
                                ? Colors.amber
                                : const Color(0xFF78350F),
                            size: 28,
                          ),
                          onPressed: () => themeProvider.toggleTheme(),
                          tooltip: isDark ? 'Light Mode' : 'Dark Mode',
                        ),
                      ),
                    ),
                  ),

                  const SizedBox(height: 20),

                  // Animated App Logo/Icon
                  ScaleTransition(
                    scale: _scaleAnimation,
                    child: Hero(
                      tag: 'app_logo',
                      child: TweenAnimationBuilder<double>(
                        tween: Tween(begin: 0.0, end: 1.0),
                        duration: const Duration(seconds: 2),
                        builder: (context, value, child) {
                          return Transform.scale(
                            scale: 1.0 + (0.1 * (1 - (value - 0.5).abs() * 2)),
                            child: Container(
                              width: 100,
                              height: 100,
                              decoration: BoxDecoration(
                                color: isDark
                                    ? Colors.amber.withOpacity(0.2)
                                    : Colors.white,
                                shape: BoxShape.circle,
                                boxShadow: [
                                  BoxShadow(
                                    color: (isDark
                                        ? Colors.amber
                                        : const Color(0xFFFFA500))
                                        .withOpacity(0.3),
                                    blurRadius: 20,
                                    spreadRadius: 5,
                                  ),
                                ],
                              ),
                              child: const Center(
                                child: Text(
                                  '🐝',
                                  style: TextStyle(fontSize: 60),
                                ),
                              ),
                            ),
                          );
                        },
                      ),
                    ),
                  ),

                  const SizedBox(height: 24),

                  // Animated Title
                  FadeTransition(
                    opacity: _fadeAnimation,
                    child: SlideTransition(
                      position: _slideAnimation,
                      child: Column(
                        children: [
                          Text(
                            'AsaliAsPossible',
                            style: TextStyle(
                              fontSize: 36,
                              fontWeight: FontWeight.bold,
                              color: isDark
                                  ? Colors.amber
                                  : const Color(0xFF78350F),
                              letterSpacing: -1,
                            ),
                          ),
                          const SizedBox(height: 8),
                          Text(
                            'Smart Beehive Monitoring',
                            style: TextStyle(
                              fontSize: 18,
                              color: isDark
                                  ? Colors.amber[200]
                                  : const Color(0xFFB45309),
                              letterSpacing: 0.5,
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),

                  const SizedBox(height: 32),

                  // Welcome Card with hover effect
                  FadeTransition(
                    opacity: _fadeAnimation,
                    child: ScaleTransition(
                      scale: _scaleAnimation,
                      child: _InteractiveCard(
                        isDark: isDark,
                        child: Column(
                          children: [
                            Text(
                              'Welcome Back',
                              style: TextStyle(
                                fontSize: 24,
                                fontWeight: FontWeight.bold,
                                color: isDark
                                    ? Colors.white
                                    : const Color(0xFF1F2937),
                              ),
                            ),
                            const SizedBox(height: 12),
                            Text(
                              'Monitor your hives, get smart recommendations, and maximize honey production with AI-powered insights.',
                              textAlign: TextAlign.center,
                              style: TextStyle(
                                fontSize: 14,
                                height: 1.5,
                                color: isDark
                                    ? Colors.grey[400]
                                    : const Color(0xFF6B7280),
                              ),
                            ),
                            const SizedBox(height: 24),

                            // Animated Get Started Button
                            SizedBox(
                              width: double.infinity,
                              child: _AnimatedButton(
                                onPressed: () => context.go('/login'),
                                text: 'Get Started',
                                isDark: isDark,
                              ),
                            ),

                            const SizedBox(height: 20),

                            // Quick Stats with animation
                            Row(
                              mainAxisAlignment: MainAxisAlignment.spaceAround,
                              children: [
                                _AnimatedStatCard(
                                  value: '${hiveProvider.hives.length}',
                                  label: 'Hives',
                                  color: const Color(0xFFF59E0B),
                                  isDark: isDark,
                                  delay: 0,
                                ),
                                _AnimatedStatCard(
                                  value: '${hiveProvider.healthyHivesCount}',
                                  label: 'Healthy',
                                  color: const Color(0xFF10B981),
                                  isDark: isDark,
                                  delay: 100,
                                ),
                                _AnimatedStatCard(
                                  value: '${recProvider.highPriorityCount}',
                                  label: 'Alerts',
                                  color: const Color(0xFFEF4444),
                                  isDark: isDark,
                                  delay: 200,
                                ),
                              ],
                            ),
                          ],
                        ),
                      ),
                    ),
                  ),

                  const SizedBox(height: 24),

                  // Features Highlight with stagger animation
                  FadeTransition(
                    opacity: _fadeAnimation,
                    child: Container(
                      padding: const EdgeInsets.all(16),
                      decoration: BoxDecoration(
                        color: isDark
                            ? const Color(0xFF374151).withOpacity(0.5)
                            : Colors.white.withOpacity(0.7),
                        borderRadius: BorderRadius.circular(16),
                        border: Border.all(
                          color: isDark
                              ? Colors.amber.withOpacity(0.3)
                              : const Color(0xFFF59E0B).withOpacity(0.3),
                        ),
                      ),
                      child: Column(
                        children: [
                          _AnimatedFeatureItem(
                            icon: Icons.analytics,
                            text: 'Real-time Analytics',
                            isDark: isDark,
                            delay: 0,
                          ),
                          const SizedBox(height: 8),
                          _AnimatedFeatureItem(
                            icon: Icons.map,
                            text: 'GPS Location Tracking',
                            isDark: isDark,
                            delay: 100,
                          ),
                          const SizedBox(height: 8),
                          _AnimatedFeatureItem(
                            icon: Icons.cloud,
                            text: 'Weather Alerts',
                            isDark: isDark,
                            delay: 200,
                          ),
                          const SizedBox(height: 8),
                          _AnimatedFeatureItem(
                            icon: Icons.school,
                            text: 'Educational Content',
                            isDark: isDark,
                            delay: 300,
                          ),
                        ],
                      ),
                    ),
                  ),

                  const SizedBox(height: 20),

                  // Offline Mode Info
                  FadeTransition(
                    opacity: _fadeAnimation,
                    child: Row(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Icon(
                          Icons.wifi_off,
                          size: 20,
                          color: isDark
                              ? Colors.grey[400]
                              : const Color(0xFF92400E),
                        ),
                        const SizedBox(width: 8),
                        Text(
                          'Offline mode available',
                          style: TextStyle(
                            fontSize: 14,
                            color: isDark
                                ? Colors.grey[400]
                                : const Color(0xFF92400E),
                          ),
                        ),
                      ],
                    ),
                  ),

                  const SizedBox(height: 20),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}

// ✨ Interactive Card with scale animation on tap
class _InteractiveCard extends StatefulWidget {
  final Widget child;
  final bool isDark;

  const _InteractiveCard({
    required this.child,
    required this.isDark,
  });

  @override
  State<_InteractiveCard> createState() => _InteractiveCardState();
}

class _InteractiveCardState extends State<_InteractiveCard> {
  bool _isPressed = false;

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTapDown: (_) => setState(() => _isPressed = true),
      onTapUp: (_) => setState(() => _isPressed = false),
      onTapCancel: () => setState(() => _isPressed = false),
      child: AnimatedScale(
        scale: _isPressed ? 0.98 : 1.0,
        duration: const Duration(milliseconds: 100),
        child: Container(
          padding: const EdgeInsets.all(24),
          decoration: BoxDecoration(
            color: widget.isDark ? const Color(0xFF374151) : Colors.white,
            borderRadius: BorderRadius.circular(24),
            boxShadow: [
              BoxShadow(
                color: Colors.black.withOpacity(widget.isDark ? 0.3 : 0.1),
                blurRadius: _isPressed ? 10 : 20,
                offset: Offset(0, _isPressed ? 5 : 10),
              ),
            ],
          ),
          child: widget.child,
        ),
      ),
    );
  }
}

// ✨ Animated Button with ripple effect
class _AnimatedButton extends StatefulWidget {
  final VoidCallback onPressed;
  final String text;
  final bool isDark;

  const _AnimatedButton({
    required this.onPressed,
    required this.text,
    required this.isDark,
  });

  @override
  State<_AnimatedButton> createState() => _AnimatedButtonState();
}

class _AnimatedButtonState extends State<_AnimatedButton> {
  bool _isHovered = false;

  @override
  Widget build(BuildContext context) {
    return MouseRegion(
      onEnter: (_) => setState(() => _isHovered = true),
      onExit: (_) => setState(() => _isHovered = false),
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 200),
        transform: Matrix4.identity()..scale(_isHovered ? 1.05 : 1.0),
        child: ElevatedButton(
          onPressed: widget.onPressed,
          style: ElevatedButton.styleFrom(
            padding: const EdgeInsets.symmetric(vertical: 16),
            backgroundColor: const Color(0xFFFFA500),
            foregroundColor: Colors.white,
            elevation: _isHovered ? 8 : 4,
            shadowColor: const Color(0xFFFFA500).withOpacity(0.5),
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(12),
            ),
          ),
          child: Text(
            widget.text,
            style: const TextStyle(
              fontSize: 16,
              fontWeight: FontWeight.w600,
              letterSpacing: 0.5,
            ),
          ),
        ),
      ),
    );
  }
}

// ✨ Animated Stat Card with delayed fade-in
class _AnimatedStatCard extends StatefulWidget {
  final String value;
  final String label;
  final Color color;
  final bool isDark;
  final int delay;

  const _AnimatedStatCard({
    required this.value,
    required this.label,
    required this.color,
    required this.isDark,
    required this.delay,
  });

  @override
  State<_AnimatedStatCard> createState() => _AnimatedStatCardState();
}

class _AnimatedStatCardState extends State<_AnimatedStatCard>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<double> _animation;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      duration: const Duration(milliseconds: 800),
      vsync: this,
    );

    _animation = Tween<double>(begin: 0.0, end: 1.0).animate(
      CurvedAnimation(parent: _controller, curve: Curves.easeOut),
    );

    Future.delayed(Duration(milliseconds: widget.delay), () {
      if (mounted) _controller.forward();
    });
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return FadeTransition(
      opacity: _animation,
      child: ScaleTransition(
        scale: _animation,
        child: Column(
          children: [
            TweenAnimationBuilder<int>(
              tween: IntTween(begin: 0, end: int.tryParse(widget.value) ?? 0),
              duration: const Duration(milliseconds: 1000),
              builder: (context, value, child) {
                return Text(
                  '$value',
                  style: TextStyle(
                    fontSize: 28,
                    fontWeight: FontWeight.bold,
                    color: widget.color,
                  ),
                );
              },
            ),
            const SizedBox(height: 4),
            Text(
              widget.label,
              style: TextStyle(
                fontSize: 12,
                color: widget.isDark
                    ? Colors.grey[400]
                    : const Color(0xFF6B7280),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

// ✨ Animated Feature Item with slide-in effect
class _AnimatedFeatureItem extends StatefulWidget {
  final IconData icon;
  final String text;
  final bool isDark;
  final int delay;

  const _AnimatedFeatureItem({
    required this.icon,
    required this.text,
    required this.isDark,
    required this.delay,
  });

  @override
  State<_AnimatedFeatureItem> createState() => _AnimatedFeatureItemState();
}

class _AnimatedFeatureItemState extends State<_AnimatedFeatureItem>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<Offset> _slideAnimation;
  late Animation<double> _fadeAnimation;
  bool _isHovered = false;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      duration: const Duration(milliseconds: 600),
      vsync: this,
    );

    _slideAnimation = Tween<Offset>(
      begin: const Offset(-0.3, 0),
      end: Offset.zero,
    ).animate(CurvedAnimation(
      parent: _controller,
      curve: Curves.easeOutCubic,
    ));

    _fadeAnimation = Tween<double>(begin: 0.0, end: 1.0).animate(
      CurvedAnimation(parent: _controller, curve: Curves.easeOut),
    );

    Future.delayed(Duration(milliseconds: widget.delay), () {
      if (mounted) _controller.forward();
    });
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return MouseRegion(
      onEnter: (_) => setState(() => _isHovered = true),
      onExit: (_) => setState(() => _isHovered = false),
      child: FadeTransition(
        opacity: _fadeAnimation,
        child: SlideTransition(
          position: _slideAnimation,
          child: AnimatedContainer(
            duration: const Duration(milliseconds: 200),
            padding: const EdgeInsets.all(8),
            decoration: BoxDecoration(
              color: _isHovered
                  ? (widget.isDark
                  ? Colors.amber.withOpacity(0.1)
                  : const Color(0xFFFFA500).withOpacity(0.1))
                  : Colors.transparent,
              borderRadius: BorderRadius.circular(8),
            ),
            child: Row(
              children: [
                Icon(
                  widget.icon,
                  size: 20,
                  color: widget.isDark
                      ? Colors.amber
                      : const Color(0xFFF59E0B),
                ),
                const SizedBox(width: 12),
                Text(
                  widget.text,
                  style: TextStyle(
                    fontSize: 14,
                    color: widget.isDark
                        ? Colors.grey[300]
                        : const Color(0xFF374151),
                    fontWeight: FontWeight.w500,
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}