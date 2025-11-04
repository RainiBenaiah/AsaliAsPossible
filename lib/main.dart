import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:google_fonts/google_fonts.dart';
import 'providers/auth_provider.dart';
import 'providers/hive_provider.dart';
import 'providers/recommendation_provider.dart';
import 'providers/theme_provider.dart'; // NEW IMPORT
import 'routes/app_router.dart';

void main() {
  runApp(const AsaliAsPossibleApp());
}

class AsaliAsPossibleApp extends StatelessWidget {
  const AsaliAsPossibleApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MultiProvider(
      providers: [
        ChangeNotifierProvider(create: (_) => AuthProvider()),
        ChangeNotifierProvider(create: (_) => HiveProvider()),
        ChangeNotifierProvider(create: (_) => RecommendationProvider()),
        ChangeNotifierProvider(create: (_) => ThemeProvider()), // NEW PROVIDER
      ],
      child: Consumer<ThemeProvider>( // WRAP WITH CONSUMER
        builder: (context, themeProvider, child) {
          return MaterialApp.router(
            title: 'AsaliAsPossible',
            debugShowCheckedModeBanner: false,
            // Light Theme
            theme: ThemeData(
              brightness: Brightness.light,
              primarySwatch: Colors.amber,
              primaryColor: const Color(0xFFF59E0B),
              scaffoldBackgroundColor: const Color(0xFFF9FAFB),
              colorScheme: ColorScheme.fromSeed(
                seedColor: const Color(0xFFF59E0B),
                secondary: const Color(0xFFFB923C),
                brightness: Brightness.light,
              ),
              textTheme: GoogleFonts.interTextTheme(),
              appBarTheme: const AppBarTheme(
                elevation: 0,
                centerTitle: false,
                backgroundColor: Color(0xFFF59E0B),
                foregroundColor: Colors.white,
              ),
              cardTheme: CardThemeData(
                elevation: 2,
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(16),
                ),
                color: Colors.white,
              ),
              elevatedButtonTheme: ElevatedButtonThemeData(
                style: ElevatedButton.styleFrom(
                  backgroundColor: const Color(0xFFF59E0B),
                  foregroundColor: Colors.white,
                  padding: const EdgeInsets.symmetric(horizontal: 32, vertical: 16),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(12),
                  ),
                  elevation: 4,
                ),
              ),
            ),
            // Dark Theme
            darkTheme: ThemeData(
              brightness: Brightness.dark,
              primarySwatch: Colors.amber,
              primaryColor: const Color(0xFFF59E0B),
              scaffoldBackgroundColor: const Color(0xFF111827),
              colorScheme: ColorScheme.fromSeed(
                seedColor: const Color(0xFFF59E0B),
                secondary: const Color(0xFFFB923C),
                brightness: Brightness.dark,
                surface: const Color(0xFF1F2937),
                background: const Color(0xFF111827),
              ),
              textTheme: GoogleFonts.interTextTheme(ThemeData.dark().textTheme),
              appBarTheme: const AppBarTheme(
                elevation: 0,
                centerTitle: false,
                backgroundColor: Color(0xFF1F2937),
                foregroundColor: Colors.white,
              ),
              cardTheme: CardThemeData(
                elevation: 2,
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(16),
                ),
                color: const Color(0xFF1F2937),
              ),
              elevatedButtonTheme: ElevatedButtonThemeData(
                style: ElevatedButton.styleFrom(
                  backgroundColor: const Color(0xFFF59E0B),
                  foregroundColor: Colors.white,
                  padding: const EdgeInsets.symmetric(horizontal: 32, vertical: 16),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(12),
                  ),
                  elevation: 4,
                ),
              ),
            ),
            // Use theme mode from provider
            themeMode: themeProvider.isDarkMode ? ThemeMode.dark : ThemeMode.light,
            routerConfig: AppRouter.router,
          );
        },
      ),
    );
  }
}