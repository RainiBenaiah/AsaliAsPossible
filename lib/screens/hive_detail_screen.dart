import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:fl_chart/fl_chart.dart';
import 'package:go_router/go_router.dart';
import '../providers/hive_provider.dart';
import '../providers/recommendation_provider.dart';
import '../models/hive_model.dart';

/// Detailed view of a single hive with visualizations and analytics
class HiveDetailScreen extends StatefulWidget {
  final String hiveId;

  const HiveDetailScreen({
    super.key,
    required this.hiveId,
  });

  @override
  State<HiveDetailScreen> createState() => _HiveDetailScreenState();
}

class _HiveDetailScreenState extends State<HiveDetailScreen> {
  String _selectedTimeRange = '7D'; // 7D, 30D, 3M, 1Y

  @override
  Widget build(BuildContext context) {
    final hiveProvider = Provider.of<HiveProvider>(context);
    final recProvider = Provider.of<RecommendationProvider>(context);
    final hive = hiveProvider.getHiveById(widget.hiveId);

    if (hive == null) {
      return Scaffold(
        appBar: AppBar(
          title: const Text('Hive Not Found'),
        ),
        body: const Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(Icons.error_outline, size: 64, color: Colors.grey),
              SizedBox(height: 16),
              Text(
                'Hive not found',
                style: TextStyle(fontSize: 18, color: Colors.grey),
              ),
            ],
          ),
        ),
      );
    }

    final hiveRecommendations = recProvider.getRecommendationsForHive(widget.hiveId);

    return Scaffold(
      body: CustomScrollView(
        slivers: [
          // App Bar with Hive Info
          SliverAppBar(
            expandedHeight: 200,
            pinned: true,
            flexibleSpace: FlexibleSpaceBar(
              background: Container(
                decoration: const BoxDecoration(
                  gradient: LinearGradient(
                    begin: Alignment.topCenter,
                    end: Alignment.bottomCenter,
                    colors: [
                      Color(0xFFF59E0B),
                      Color(0xFFFB923C),
                    ],
                  ),
                ),
                child: SafeArea(
                  child: Padding(
                    padding: const EdgeInsets.all(16),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      mainAxisAlignment: MainAxisAlignment.end,
                      children: [
                        Row(
                          children: [
                            Container(
                              width: 16,
                              height: 16,
                              decoration: BoxDecoration(
                                color: hive.getStatusColor(),
                                shape: BoxShape.circle,
                                boxShadow: [
                                  BoxShadow(
                                    color: hive.getStatusColor().withOpacity(0.5),
                                    blurRadius: 8,
                                    spreadRadius: 2,
                                  ),
                                ],
                              ),
                            ),
                            const SizedBox(width: 12),
                            Expanded(
                              child: Text(
                                hive.name,
                                style: const TextStyle(
                                  fontSize: 28,
                                  fontWeight: FontWeight.bold,
                                  color: Colors.white,
                                ),
                              ),
                            ),
                            if (hive.alerts > 0)
                              Container(
                                padding: const EdgeInsets.symmetric(
                                  horizontal: 12,
                                  vertical: 6,
                                ),
                                decoration: BoxDecoration(
                                  color: Colors.red,
                                  borderRadius: BorderRadius.circular(12),
                                ),
                                child: Text(
                                  '${hive.alerts} ${hive.alerts == 1 ? 'Alert' : 'Alerts'}',
                                  style: const TextStyle(
                                    color: Colors.white,
                                    fontWeight: FontWeight.bold,
                                  ),
                                ),
                              ),
                          ],
                        ),
                        const SizedBox(height: 8),
                        Row(
                          children: [
                            const Icon(Icons.location_on, color: Colors.white70, size: 16),
                            const SizedBox(width: 4),
                            Text(
                              hive.location,
                              style: const TextStyle(
                                color: Colors.white70,
                                fontSize: 14,
                              ),
                            ),
                          ],
                        ),
                      ],
                    ),
                  ),
                ),
              ),
            ),
            actions: [
              IconButton(
                icon: const Icon(Icons.edit),
                onPressed: () {
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(content: Text('Edit functionality coming soon')),
                  );
                },
              ),
              IconButton(
                icon: const Icon(Icons.share),
                onPressed: () {
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(content: Text('Share functionality coming soon')),
                  );
                },
              ),
            ],
          ),

          // Content
          SliverToBoxAdapter(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // Quick Metrics
                  _QuickMetrics(hive: hive),
                  const SizedBox(height: 24),

                  // Time Range Selector
                  _TimeRangeSelector(
                    selected: _selectedTimeRange,
                    onChanged: (range) {
                      setState(() => _selectedTimeRange = range);
                    },
                  ),
                  const SizedBox(height: 16),

                  // Temperature Chart
                  _ChartCard(
                    title: 'Temperature Trend',
                    subtitle: _getTimeRangeLabel(_selectedTimeRange),
                    icon: Icons.thermostat_outlined,
                    iconColor: Colors.orange,
                    child: _TemperatureChart(
                      currentTemp: hive.temperature,
                      timeRange: _selectedTimeRange,
                    ),
                  ),
                  const SizedBox(height: 16),

                  // Humidity Chart
                  _ChartCard(
                    title: 'Humidity Levels',
                    subtitle: _getTimeRangeLabel(_selectedTimeRange),
                    icon: Icons.water_drop_outlined,
                    iconColor: Colors.blue,
                    child: _HumidityChart(
                      currentHumidity: hive.humidity,
                      timeRange: _selectedTimeRange,
                    ),
                  ),
                  const SizedBox(height: 16),

                  // Weight Chart
                  _ChartCard(
                    title: 'Weight Tracking',
                    subtitle: _getTimeRangeLabel(_selectedTimeRange),
                    icon: Icons.scale_outlined,
                    iconColor: Colors.green,
                    child: _WeightChart(
                      currentWeight: hive.weight,
                      timeRange: _selectedTimeRange,
                    ),
                  ),
                  const SizedBox(height: 16),

                  // Health Score
                  _HealthScoreCard(hive: hive),
                  const SizedBox(height: 16),

                  // Recommendations for this hive
                  if (hiveRecommendations.isNotEmpty) ...[
                    _RecommendationsSection(
                      recommendations: hiveRecommendations,
                      hive: hive,
                    ),
                    const SizedBox(height: 16),
                  ],

                  // Location Map Preview
                  _LocationPreview(hive: hive),
                  const SizedBox(height: 16),

                  // Action Buttons
                  _ActionButtons(hive: hive),
                  const SizedBox(height: 80), // Space for FAB
                ],
              ),
            ),
          ),
        ],
      ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: () {
          _showAddInspectionDialog(context, hive);
        },
        backgroundColor: const Color(0xFFF59E0B),
        icon: const Icon(Icons.add),
        label: const Text('Add Inspection'),
      ),
    );
  }

  String _getTimeRangeLabel(String range) {
    switch (range) {
      case '7D':
        return 'Last 7 days';
      case '30D':
        return 'Last 30 days';
      case '3M':
        return 'Last 3 months';
      case '1Y':
        return 'Last year';
      default:
        return 'Last 7 days';
    }
  }

  void _showAddInspectionDialog(BuildContext context, HiveModel hive) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Add Inspection'),
        content: const Text(
          'Inspection feature coming soon!\n\nYou will be able to:\n• Record observations\n• Add photos\n• Track queen presence\n• Note brood pattern\n• Record pests/diseases',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('OK'),
          ),
        ],
      ),
    );
  }
}

// Quick Metrics Widget
class _QuickMetrics extends StatelessWidget {
  final HiveModel hive;

  const _QuickMetrics({required this.hive});

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        Expanded(
          child: _MetricCard(
            icon: Icons.thermostat_outlined,
            label: 'Temperature',
            value: '${hive.temperature}°C',
            color: Colors.orange,
            status: _getTemperatureStatus(hive.temperature),
          ),
        ),
        const SizedBox(width: 12),
        Expanded(
          child: _MetricCard(
            icon: Icons.water_drop_outlined,
            label: 'Humidity',
            value: '${hive.humidity}%',
            color: Colors.blue,
            status: _getHumidityStatus(hive.humidity),
          ),
        ),
        const SizedBox(width: 12),
        Expanded(
          child: _MetricCard(
            icon: Icons.scale_outlined,
            label: 'Weight',
            value: '${hive.weight}kg',
            color: Colors.green,
            status: _getWeightStatus(hive.weight),
          ),
        ),
      ],
    );
  }

  String _getTemperatureStatus(double temp) {
    if (temp < 32) return 'Low';
    if (temp > 36) return 'High';
    return 'Optimal';
  }

  String _getHumidityStatus(double humidity) {
    if (humidity < 50) return 'Low';
    if (humidity > 70) return 'High';
    return 'Good';
  }

  String _getWeightStatus(double weight) {
    if (weight < 40) return 'Light';
    if (weight > 50) return 'Heavy';
    return 'Normal';
  }
}

// Metric Card Widget
class _MetricCard extends StatelessWidget {
  final IconData icon;
  final String label;
  final String value;
  final Color color;
  final String status;

  const _MetricCard({
    required this.icon,
    required this.label,
    required this.value,
    required this.color,
    required this.status,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(
          color: color.withOpacity(0.3),
          width: 2,
        ),
      ),
      child: Column(
        children: [
          Icon(icon, size: 32, color: color),
          const SizedBox(height: 8),
          Text(
            value,
            style: TextStyle(
              fontSize: 22,
              fontWeight: FontWeight.bold,
              color: color,
            ),
          ),
          const SizedBox(height: 4),
          Text(
            label,
            style: TextStyle(
              fontSize: 11,
              color: Colors.grey.shade600,
            ),
          ),
          const SizedBox(height: 4),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
            decoration: BoxDecoration(
              color: color.withOpacity(0.2),
              borderRadius: BorderRadius.circular(8),
            ),
            child: Text(
              status,
              style: TextStyle(
                fontSize: 10,
                fontWeight: FontWeight.bold,
                color: color,
              ),
            ),
          ),
        ],
      ),
    );
  }
}

// Time Range Selector
class _TimeRangeSelector extends StatelessWidget {
  final String selected;
  final Function(String) onChanged;

  const _TimeRangeSelector({
    required this.selected,
    required this.onChanged,
  });

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        _TimeRangeChip('7D', '7 Days', selected == '7D', () => onChanged('7D')),
        const SizedBox(width: 8),
        _TimeRangeChip('30D', '30 Days', selected == '30D', () => onChanged('30D')),
        const SizedBox(width: 8),
        _TimeRangeChip('3M', '3 Months', selected == '3M', () => onChanged('3M')),
        const SizedBox(width: 8),
        _TimeRangeChip('1Y', '1 Year', selected == '1Y', () => onChanged('1Y')),
      ],
    );
  }
}

class _TimeRangeChip extends StatelessWidget {
  final String value;
  final String label;
  final bool isSelected;
  final VoidCallback onTap;

  const _TimeRangeChip(this.value, this.label, this.isSelected, this.onTap);

  @override
  Widget build(BuildContext context) {
    return Expanded(
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(8),
        child: Container(
          padding: const EdgeInsets.symmetric(vertical: 8),
          decoration: BoxDecoration(
            color: isSelected ? const Color(0xFFF59E0B) : Colors.grey.shade200,
            borderRadius: BorderRadius.circular(8),
          ),
          child: Text(
            value,
            textAlign: TextAlign.center,
            style: TextStyle(
              fontSize: 12,
              fontWeight: FontWeight.bold,
              color: isSelected ? Colors.white : Colors.grey.shade600,
            ),
          ),
        ),
      ),
    );
  }
}

// Chart Card Wrapper
class _ChartCard extends StatelessWidget {
  final String title;
  final String subtitle;
  final IconData icon;
  final Color iconColor;
  final Widget child;

  const _ChartCard({
    required this.title,
    required this.subtitle,
    required this.icon,
    required this.iconColor,
    required this.child,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      elevation: 0,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(16),
        side: BorderSide(color: Colors.grey.shade200),
      ),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Container(
                  padding: const EdgeInsets.all(8),
                  decoration: BoxDecoration(
                    color: iconColor.withOpacity(0.1),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Icon(icon, color: iconColor, size: 20),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        title,
                        style: const TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.bold,
                          color: Color(0xFF1F2937),
                        ),
                      ),
                      Text(
                        subtitle,
                        style: TextStyle(
                          fontSize: 12,
                          color: Colors.grey.shade600,
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            child,
          ],
        ),
      ),
    );
  }
}

// Temperature Chart
class _TemperatureChart extends StatelessWidget {
  final double currentTemp;
  final String timeRange;

  const _TemperatureChart({
    required this.currentTemp,
    required this.timeRange,
  });

  @override
  Widget build(BuildContext context) {
    // Mock historical data - in real app, this would come from API
    final data = _generateMockData(currentTemp, 7);

    return SizedBox(
      height: 200,
      child: LineChart(
        LineChartData(
          gridData: FlGridData(
            show: true,
            drawVerticalLine: false,
            horizontalInterval: 2,
            getDrawingHorizontalLine: (value) {
              return FlLine(
                color: Colors.grey.shade200,
                strokeWidth: 1,
              );
            },
          ),
          titlesData: FlTitlesData(
            rightTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
            topTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
            bottomTitles: AxisTitles(
              sideTitles: SideTitles(
                showTitles: true,
                reservedSize: 30,
                getTitlesWidget: (value, meta) {
                  const days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
                  if (value.toInt() >= 0 && value.toInt() < days.length) {
                    return Text(
                      days[value.toInt()],
                      style: const TextStyle(fontSize: 10, color: Colors.grey),
                    );
                  }
                  return const Text('');
                },
              ),
            ),
            leftTitles: AxisTitles(
              sideTitles: SideTitles(
                showTitles: true,
                reservedSize: 40,
                getTitlesWidget: (value, meta) {
                  return Text(
                    '${value.toInt()}°C',
                    style: const TextStyle(fontSize: 10, color: Colors.grey),
                  );
                },
              ),
            ),
          ),
          borderData: FlBorderData(show: false),
          minX: 0,
          maxX: 6,
          minY: 28,
          maxY: 40,
          lineBarsData: <LineChartBarData>[
          LineChartBarData(
          spots: data,
          isCurved: true,
          color: Colors.orange,
          barWidth: 3,
          isStrokeCapRound: true,
          dotData: FlDotData(
            show: true,
            getDotPainter: (spot, percent, barData, index) {
              return FlDotCirclePainter(
                radius: 4,
                color: Colors.white,
                strokeWidth: 2,
                strokeColor: Colors.orange,
              );
            },
          ),
          belowBarData: BarAreaData(
            show: true,
            color: Colors.orange.withOpacity(0.1),
          ),
        ),
      ]),
    ),
    );
  }

  List<FlSpot> _generateMockData(double current, int days) {
    return List.generate(days, (index) {
      final variance = (index - days / 2) * 0.5;
      return FlSpot(index.toDouble(), current + variance);
    });
  }
}

// Humidity Chart
class _HumidityChart extends StatelessWidget {
  final double currentHumidity;
  final String timeRange;

  const _HumidityChart({
    required this.currentHumidity,
    required this.timeRange,
  });

  @override
  Widget build(BuildContext context) {
    final data = _generateMockData(currentHumidity, 7);

    return SizedBox(
      height: 200,
      child: LineChart(
        LineChartData(
          gridData: FlGridData(
            show: true,
            drawVerticalLine: false,
            horizontalInterval: 10,
            getDrawingHorizontalLine: (value) {
              return FlLine(color: Colors.grey.shade200, strokeWidth: 1);
            },
          ),
          titlesData: FlTitlesData(
            rightTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
            topTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
            bottomTitles: AxisTitles(
              sideTitles: SideTitles(
                showTitles: true,
                reservedSize: 30,
                getTitlesWidget: (value, meta) {
                  const days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
                  if (value.toInt() >= 0 && value.toInt() < days.length) {
                    return Text(
                      days[value.toInt()],
                      style: const TextStyle(fontSize: 10, color: Colors.grey),
                    );
                  }
                  return const Text('');
                },
              ),
            ),
            leftTitles: AxisTitles(
              sideTitles: SideTitles(
                showTitles: true,
                reservedSize: 40,
                getTitlesWidget: (value, meta) {
                  return Text(
                    '${value.toInt()}%',
                    style: const TextStyle(fontSize: 10, color: Colors.grey),
                  );
                },
              ),
            ),
          ),
          borderData: FlBorderData(show: false),
          minX: 0,
          maxX: 6,
          minY: 40,
          maxY: 80,
          lineBarsData: [
            LineChartBarData(
              spots: data,
              isCurved: true,
              color: Colors.blue,
              barWidth: 3,
              isStrokeCapRound: true,
              dotData: FlDotData(
                show: true,
                getDotPainter: (spot, percent, barData, index) {
                  return FlDotCirclePainter(
                    radius: 4,
                    color: Colors.white,
                    strokeWidth: 2,
                    strokeColor: Colors.blue,
                  );
                },
              ),
              belowBarData: BarAreaData(
                show: true,
                color: Colors.blue.withOpacity(0.1),
              ),
            ),
          ],
          lineTouchData: LineTouchData(
            touchTooltipData: LineTouchTooltipData(
              tooltipBgColor: Colors.blue,
              getTooltipItems: (touchedSpots) {
                return touchedSpots.map((spot) {
                  return LineTooltipItem(
                    '${spot.y.toStringAsFixed(1)}%',
                    const TextStyle(color: Colors.white, fontWeight: FontWeight.bold),
                  );
                }).toList();
              },
            ),
          ),
        ),
      ),
    );
  }

  List<FlSpot> _generateMockData(double current, int days) {
    return List.generate(days, (index) {
      final variance = (index - days / 2) * 1.5;
      return FlSpot(index.toDouble(), current + variance);
    });
  }
}

// Weight Chart
class _WeightChart extends StatelessWidget {
  final double currentWeight;
  final String timeRange;

  const _WeightChart({
    required this.currentWeight,
    required this.timeRange,
  });

  @override
  Widget build(BuildContext context) {
    final data = _generateMockData(currentWeight, 7);

    return SizedBox(
      height: 200,
      child: LineChart(
        LineChartData(
          gridData: FlGridData(
            show: true,
            drawVerticalLine: false,
            horizontalInterval: 5,
            getDrawingHorizontalLine: (value) {
              return FlLine(color: Colors.grey.shade200, strokeWidth: 1);
            },
          ),
          titlesData: FlTitlesData(
            rightTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
            topTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
            bottomTitles: AxisTitles(
              sideTitles: SideTitles(
                showTitles: true,
                reservedSize: 30,
                getTitlesWidget: (value, meta) {
                  const days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
                  if (value.toInt() >= 0 && value.toInt() < days.length) {
                    return Text(
                      days[value.toInt()],
                      style: const TextStyle(fontSize: 10, color: Colors.grey),
                    );
                  }
                  return const Text('');
                },
              ),
            ),
            leftTitles: AxisTitles(
              sideTitles: SideTitles(
                showTitles: true,
                reservedSize: 40,
                getTitlesWidget: (value, meta) {
                  return Text(
                    '${value.toInt()}kg',
                    style: const TextStyle(fontSize: 10, color: Colors.grey),
                  );
                },
              ),
            ),
          ),
          borderData: FlBorderData(show: false),
          minX: 0,
          maxX: 6,
          minY: 35,
          maxY: 55,
          lineBarsData: [
            LineChartBarData(
              spots: data,
              isCurved: true,
              color: Colors.green,
              barWidth: 3,
              isStrokeCapRound: true,
              dotData: FlDotData(
                show: true,
                getDotPainter: (spot, percent, barData, index) {
                  return FlDotCirclePainter(
                    radius: 4,
                    color: Colors.white,
                    strokeWidth: 2,
                    strokeColor: Colors.green,
                  );
                },
              ),
              belowBarData: BarAreaData(
                show: true,
                color: Colors.green.withOpacity(0.1),
              ),
            ),
          ],
          lineTouchData: LineTouchData(
            touchTooltipData: LineTouchTooltipData(
              tooltipBgColor: Colors.green,
              getTooltipItems: (touchedSpots) {
                return touchedSpots.map((spot) {
                  return LineTooltipItem(
                    '${spot.y.toStringAsFixed(1)}kg',
                    const TextStyle(color: Colors.white, fontWeight: FontWeight.bold),
                  );
                }).toList();
              },
            ),
          ),
        ),
      ),
    );
  }

  List<FlSpot> _generateMockData(double current, int days) {
    return List.generate(days, (index) {
      final variance = (index - days / 2) * 0.8;
      return FlSpot(index.toDouble(), current + variance);
    });
  }
}

// Health Score Card
class _HealthScoreCard extends StatelessWidget {
  final HiveModel hive;

  const _HealthScoreCard({required this.hive});

  @override
  Widget build(BuildContext context) {
    final score = _calculateHealthScore(hive);
    final color = _getScoreColor(score);

    return Card(
      elevation: 0,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(16),
        side: BorderSide(color: Colors.grey.shade200),
      ),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            Row(
              children: [
                Container(
                  padding: const EdgeInsets.all(8),
                  decoration: BoxDecoration(
                    color: color.withOpacity(0.1),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Icon(Icons.favorite, color: color, size: 20),
                ),
                const SizedBox(width: 12),
                const Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'Health Score',
                        style: TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.bold,
                          color: Color(0xFF1F2937),
                        ),
                      ),
                      Text(
                        'Overall hive health assessment',
                        style: TextStyle(
                          fontSize: 12,
                          color: Colors.grey,
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
            const SizedBox(height: 20),
            SizedBox(
              height: 120,
              child: Stack(
                alignment: Alignment.center,
                children: [
                  SizedBox(
                    width: 120,
                    height: 120,
                    child: CircularProgressIndicator(
                      value: score / 100,
                      strokeWidth: 12,
                      backgroundColor: Colors.grey.shade200,
                      valueColor: AlwaysStoppedAnimation<Color>(color),
                    ),
                  ),
                  Column(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Text(
                        '${score.toInt()}',
                        style: TextStyle(
                          fontSize: 36,
                          fontWeight: FontWeight.bold,
                          color: color,
                        ),
                      ),
                      Text(
                        _getScoreLabel(score),
                        style: TextStyle(
                          fontSize: 14,
                          color: color,
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ),
            const SizedBox(height: 16),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceAround,
              children: [
                _ScoreIndicator(
                  label: 'Temperature',
                  value: _getTempScore(hive.temperature),
                  color: Colors.orange,
                ),
                _ScoreIndicator(
                  label: 'Humidity',
                  value: _getHumidityScore(hive.humidity),
                  color: Colors.blue,
                ),
                _ScoreIndicator(
                  label: 'Weight',
                  value: _getWeightScore(hive.weight),
                  color: Colors.green,
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  double _calculateHealthScore(HiveModel hive) {
    final tempScore = _getTempScore(hive.temperature);
    final humidityScore = _getHumidityScore(hive.humidity);
    final weightScore = _getWeightScore(hive.weight);
    final alertPenalty = hive.alerts * 10;

    return ((tempScore + humidityScore + weightScore) / 3 - alertPenalty).clamp(0, 100);
  }

  double _getTempScore(double temp) {
    if (temp >= 32 && temp <= 36) return 100;
    if (temp >= 30 && temp <= 38) return 80;
    if (temp >= 28 && temp <= 40) return 60;
    return 40;
  }

  double _getHumidityScore(double humidity) {
    if (humidity >= 50 && humidity <= 70) return 100;
    if (humidity >= 45 && humidity <= 75) return 80;
    if (humidity >= 40 && humidity <= 80) return 60;
    return 40;
  }

  double _getWeightScore(double weight) {
    if (weight >= 42 && weight <= 48) return 100;
    if (weight >= 38 && weight <= 52) return 80;
    if (weight >= 35 && weight <= 55) return 60;
    return 40;
  }

  Color _getScoreColor(double score) {
    if (score >= 80) return Colors.green;
    if (score >= 60) return Colors.orange;
    return Colors.red;
  }

  String _getScoreLabel(double score) {
    if (score >= 80) return 'Excellent';
    if (score >= 60) return 'Good';
    if (score >= 40) return 'Fair';
    return 'Poor';
  }
}

class _ScoreIndicator extends StatelessWidget {
  final String label;
  final double value;
  final Color color;

  const _ScoreIndicator({
    required this.label,
    required this.value,
    required this.color,
  });

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Text(
          '${value.toInt()}%',
          style: TextStyle(
            fontSize: 16,
            fontWeight: FontWeight.bold,
            color: color,
          ),
        ),
        const SizedBox(height: 4),
        Text(
          label,
          style: const TextStyle(
            fontSize: 11,
            color: Colors.grey,
          ),
        ),
      ],
    );
  }
}

// Recommendations Section
class _RecommendationsSection extends StatelessWidget {
  final List recommendations;
  final HiveModel hive;

  const _RecommendationsSection({
    required this.recommendations,
    required this.hive,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      elevation: 0,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(16),
        side: BorderSide(color: Colors.grey.shade200),
      ),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Container(
                  padding: const EdgeInsets.all(8),
                  decoration: BoxDecoration(
                    color: Colors.orange.withOpacity(0.1),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: const Icon(
                    Icons.warning_amber_rounded,
                    color: Colors.orange,
                    size: 20,
                  ),
                ),
                const SizedBox(width: 12),
                const Expanded(
                  child: Text(
                    'Active Recommendations',
                    style: TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.bold,
                      color: Color(0xFF1F2937),
                    ),
                  ),
                ),
                TextButton(
                  onPressed: () => context.push('/recommendations'),
                  child: const Text('View All'),
                ),
              ],
            ),
            const SizedBox(height: 12),
            ...recommendations.take(3).map((rec) => Padding(
              padding: const EdgeInsets.only(bottom: 8),
              child: Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: rec.getPriorityBackgroundColor(),
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(
                    color: rec.getPriorityColor().withOpacity(0.3),
                  ),
                ),
                child: Row(
                  children: [
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            rec.action,
                            style: TextStyle(
                              fontWeight: FontWeight.w600,
                              color: rec.getPriorityColor(),
                            ),
                          ),
                          const SizedBox(height: 4),
                          Text(
                            rec.reason,
                            style: TextStyle(
                              fontSize: 12,
                              color: rec.getPriorityColor().withOpacity(0.8),
                            ),
                          ),
                        ],
                      ),
                    ),
                    Container(
                      padding: const EdgeInsets.symmetric(
                        horizontal: 8,
                        vertical: 4,
                      ),
                      decoration: BoxDecoration(
                        color: rec.getPriorityColor(),
                        borderRadius: BorderRadius.circular(8),
                      ),
                      child: Text(
                        rec.priority.toUpperCase(),
                        style: const TextStyle(
                          color: Colors.white,
                          fontSize: 10,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            )),
          ],
        ),
      ),
    );
  }
}

// Location Preview
class _LocationPreview extends StatelessWidget {
  final HiveModel hive;

  const _LocationPreview({required this.hive});

  @override
  Widget build(BuildContext context) {
    return Card(
      elevation: 0,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(16),
        side: BorderSide(color: Colors.grey.shade200),
      ),
      child: InkWell(
        onTap: () => context.push('/map'),
        borderRadius: BorderRadius.circular(16),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Container(
                    padding: const EdgeInsets.all(8),
                    decoration: BoxDecoration(
                      color: Colors.red.withOpacity(0.1),
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: const Icon(Icons.location_on, color: Colors.red, size: 20),
                  ),
                  const SizedBox(width: 12),
                  const Expanded(
                    child: Text(
                      'Location',
                      style: TextStyle(
                        fontSize: 16,
                        fontWeight: FontWeight.bold,
                        color: Color(0xFF1F2937),
                      ),
                    ),
                  ),
                  const Icon(Icons.chevron_right, color: Colors.grey),
                ],
              ),
              const SizedBox(height: 12),
              Row(
                children: [
                  const Icon(Icons.place, size: 16, color: Colors.grey),
                  const SizedBox(width: 8),
                  Text(
                    hive.location,
                    style: const TextStyle(fontSize: 14),
                  ),
                ],
              ),
              const SizedBox(height: 4),
              Row(
                children: [
                  const Icon(Icons.gps_fixed, size: 16, color: Colors.grey),
                  const SizedBox(width: 8),
                  Text(
                    '${hive.latitude.toStringAsFixed(4)}, ${hive.longitude.toStringAsFixed(4)}',
                    style: TextStyle(
                      fontSize: 12,
                      color: Colors.grey.shade600,
                    ),
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }
}

// Action Buttons
class _ActionButtons extends StatelessWidget {
  final HiveModel hive;

  const _ActionButtons({required this.hive});

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        Expanded(
          child: OutlinedButton.icon(
            onPressed: () {
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(content: Text('Edit functionality coming soon')),
              );
            },
            icon: const Icon(Icons.edit),
            label: const Text('Edit Hive'),
            style: OutlinedButton.styleFrom(
              padding: const EdgeInsets.symmetric(vertical: 12),
              side: BorderSide(color: Colors.grey.shade300),
            ),
          ),
        ),
        const SizedBox(width: 12),
        Expanded(
          child: ElevatedButton.icon(
            onPressed: () => context.push('/map'),
            icon: const Icon(Icons.map),
            label: const Text('View on Map'),
            style: ElevatedButton.styleFrom(
              backgroundColor: const Color(0xFFF59E0B),
              foregroundColor: Colors.white,
              padding: const EdgeInsets.symmetric(vertical: 12),
              elevation: 0,
            ),
          ),
        ),
      ],
    );
  }
}