// screens/recommendations_screen.dart
import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:provider/provider.dart';
import '../providers/recommendation_provider.dart';
import '../providers/hive_provider.dart';

/// Screen displaying all recommendations organized by priority
class RecommendationsScreen extends StatelessWidget {
  const RecommendationsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final recProvider = Provider.of<RecommendationProvider>(context);
    final hiveProvider = Provider.of<HiveProvider>(context);

    final highPriority = recProvider.getRecommendationsByPriority('high');
    final mediumPriority = recProvider.getRecommendationsByPriority('medium');
    final lowPriority = recProvider.getRecommendationsByPriority('low');

    return Scaffold(
      body: Container(
        decoration: const BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topCenter,
            end: Alignment.center,
            colors: [
              Color(0xFFF59E0B),
              Color(0xFFFB923C),
            ],
          ),
        ),
        child: SafeArea(
          child: Column(
            children: [
              // Header
              Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  children: [
                    Row(
                      children: [
                        IconButton(
                          icon: const Icon(Icons.arrow_back, color: Colors.white),
                          onPressed: () => context.pop(),
                        ),
                        const Text(
                          'Recommendations',
                          style: TextStyle(
                            color: Colors.white,
                            fontSize: 20,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 16),
                    Row(
                      children: [
                        Expanded(
                          child: _PriorityStatCard(
                            count: highPriority.length,
                            label: 'High Priority',
                          ),
                        ),
                        const SizedBox(width: 12),
                        Expanded(
                          child: _PriorityStatCard(
                            count: mediumPriority.length,
                            label: 'Medium',
                          ),
                        ),
                        const SizedBox(width: 12),
                        Expanded(
                          child: _PriorityStatCard(
                            count: lowPriority.length,
                            label: 'Low',
                          ),
                        ),
                      ],
                    ),
                  ],
                ),
              ),

              // Content
              Expanded(
                child: Container(
                  decoration: const BoxDecoration(
                    color: Color(0xFFF9FAFB),
                    borderRadius: BorderRadius.only(
                      topLeft: Radius.circular(24),
                      topRight: Radius.circular(24),
                    ),
                  ),
                  child: recProvider.activeRecommendations.isEmpty
                      ? Center(
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        const Text('🎉', style: TextStyle(fontSize: 60)),
                        const SizedBox(height: 16),
                        const Text(
                          'All caught up!',
                          style: TextStyle(
                            fontSize: 24,
                            fontWeight: FontWeight.bold,
                            color: Color(0xFF1F2937),
                          ),
                        ),
                        const SizedBox(height: 8),
                        Text(
                          'No active recommendations at the moment.\nYour hives are looking great!',
                          textAlign: TextAlign.center,
                          style: TextStyle(
                            fontSize: 14,
                            color: Colors.grey[600],
                          ),
                        ),
                      ],
                    ),
                  )
                      : ListView(
                    padding: const EdgeInsets.all(16),
                    children: [
                      if (highPriority.isNotEmpty) ...[
                        _buildPrioritySection(
                          context,
                          'High Priority Actions',
                          highPriority,
                          recProvider,
                          hiveProvider,
                          isPulsing: true,
                        ),
                        const SizedBox(height: 16),
                      ],
                      if (mediumPriority.isNotEmpty) ...[
                        _buildPrioritySection(
                          context,
                          'Medium Priority',
                          mediumPriority,
                          recProvider,
                          hiveProvider,
                        ),
                        const SizedBox(height: 16),
                      ],
                      if (lowPriority.isNotEmpty) ...[
                        _buildPrioritySection(
                          context,
                          'Low Priority',
                          lowPriority,
                          recProvider,
                          hiveProvider,
                        ),
                      ],
                    ],
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildPrioritySection(
      BuildContext context,
      String title,
      List recommendations,
      RecommendationProvider recProvider,
      HiveProvider hiveProvider,
      {bool isPulsing = false}
      ) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                if (isPulsing)
                  const Icon(Icons.warning_amber_rounded, color: Color(0xFFEF4444)),
                const SizedBox(width: 8),
                Text(
                  title,
                  style: TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                    color: isPulsing ? const Color(0xFFEF4444) : const Color(0xFF1F2937),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            ...recommendations.map((rec) {
              final hive = hiveProvider.getHiveById(rec.hiveId);
              return Container(
                margin: const EdgeInsets.only(bottom: 12),
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: rec.getPriorityBackgroundColor(),
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(
                    color: rec.getPriorityColor().withOpacity(0.3),
                    width: isPulsing ? 2 : 1,
                  ),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Expanded(
                          child: Text(
                            rec.action,
                            style: TextStyle(
                              fontWeight: FontWeight.bold,
                              fontSize: 15,
                              color: rec.getPriorityColor(),
                            ),
                          ),
                        ),
                        Row(
                          children: [
                            ElevatedButton(
                              onPressed: () => context.push('/hive/${rec.hiveId}'),
                              style: ElevatedButton.styleFrom(
                                backgroundColor: rec.getPriorityColor(),
                                padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                                minimumSize: Size.zero,
                                tapTargetSize: MaterialTapTargetSize.shrinkWrap,
                              ),
                              child: const Text(
                                'View Hive',
                                style: TextStyle(fontSize: 11),
                              ),
                            ),
                            IconButton(
                              icon: const Icon(Icons.check_circle, size: 24),
                              color: rec.getPriorityColor(),
                              onPressed: () {
                                recProvider.completeRecommendation(rec.id);
                                ScaffoldMessenger.of(context).showSnackBar(
                                  const SnackBar(
                                    content: Text('Recommendation completed'),
                                    duration: Duration(seconds: 2),
                                  ),
                                );
                              },
                            ),
                          ],
                        ),
                      ],
                    ),
                    const SizedBox(height: 8),
                    Text(
                      rec.reason,
                      style: TextStyle(
                        fontSize: 13,
                        color: rec.getPriorityColor().withOpacity(0.8),
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      '${rec.time} • ${hive?.name ?? 'Unknown Hive'}',
                      style: TextStyle(
                        fontSize: 11,
                        color: rec.getPriorityColor().withOpacity(0.6),
                      ),
                    ),
                  ],
                ),
              );
            }).toList(),
          ],
        ),
      ),
    );
  }
}

class _PriorityStatCard extends StatelessWidget {
  final int count;
  final String label;

  const _PriorityStatCard({
    required this.count,
    required this.label,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Colors.white.withOpacity(0.2),
        borderRadius: BorderRadius.circular(12),
      ),
      child: Column(
        children: [
          Text(
            count.toString(),
            style: const TextStyle(
              fontSize: 20,
              fontWeight: FontWeight.bold,
              color: Colors.white,
            ),
          ),
          const SizedBox(height: 4),
          Text(
            label,
            style: TextStyle(
              fontSize: 11,
              color: Colors.white.withOpacity(0.9),
            ),
            textAlign: TextAlign.center,
          ),
        ],
      ),
    );
  }
}