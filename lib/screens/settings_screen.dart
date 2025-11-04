// screens/settings_screen.dart
import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

/// Settings screen for app configuration
class SettingsScreen extends StatefulWidget {
  const SettingsScreen({super.key});

  @override
  State<SettingsScreen> createState() => _SettingsScreenState();
}

class _SettingsScreenState extends State<SettingsScreen> {
  bool _temperatureAlerts = true;
  bool _weightMonitoring = true;
  bool _soundAnalysis = true;
  bool _pushNotifications = true;
  bool _emailAlerts = false;
  bool _dataBackup = true;

  String _monitoringFrequency = 'Every 15 minutes';
  String _alertThreshold = 'Medium and High priority';

  @override
  Widget build(BuildContext context) {
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
                child: Row(
                  children: [
                    IconButton(
                      icon: const Icon(Icons.arrow_back, color: Colors.white),
                      onPressed: () => context.pop(),
                    ),
                    const Text(
                      'Settings',
                      style: TextStyle(
                        color: Colors.white,
                        fontSize: 20,
                        fontWeight: FontWeight.bold,
                      ),
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
                  child: ListView(
                    padding: const EdgeInsets.all(16),
                    children: [
                      // Hive Monitoring Settings
                      Card(
                        child: Padding(
                          padding: const EdgeInsets.all(16),
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              const Text(
                                'Hive Monitoring Settings',
                                style: TextStyle(
                                  fontSize: 18,
                                  fontWeight: FontWeight.bold,
                                  color: Color(0xFF1F2937),
                                ),
                              ),
                              const SizedBox(height: 16),
                              _SettingSwitch(
                                title: 'Temperature Alerts',
                                subtitle: 'Get notified when temperature goes outside optimal range',
                                value: _temperatureAlerts,
                                onChanged: (val) => setState(() => _temperatureAlerts = val),
                              ),
                              const Divider(),
                              _SettingSwitch(
                                title: 'Weight Monitoring',
                                subtitle: 'Track sudden weight changes',
                                value: _weightMonitoring,
                                onChanged: (val) => setState(() => _weightMonitoring = val),
                              ),
                              const Divider(),
                              _SettingSwitch(
                                title: 'Sound Analysis',
                                subtitle: 'Monitor bee activity through sound patterns',
                                value: _soundAnalysis,
                                onChanged: (val) => setState(() => _soundAnalysis = val),
                              ),
                              const Divider(),
                              _SettingDropdown(
                                title: 'Monitoring Frequency',
                                value: _monitoringFrequency,
                                items: const [
                                  'Every 5 minutes',
                                  'Every 15 minutes',
                                  'Every 30 minutes',
                                  'Every hour',
                                ],
                                onChanged: (val) => setState(() => _monitoringFrequency = val!),
                              ),
                            ],
                          ),
                        ),
                      ),
                      const SizedBox(height: 16),

                      // Notification Settings
                      Card(
                        child: Padding(
                          padding: const EdgeInsets.all(16),
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              const Text(
                                'Notification Settings',
                                style: TextStyle(
                                  fontSize: 18,
                                  fontWeight: FontWeight.bold,
                                  color: Color(0xFF1F2937),
                                ),
                              ),
                              const SizedBox(height: 16),
                              _SettingSwitch(
                                title: 'Push Notifications',
                                subtitle: 'Receive instant alerts on your device',
                                value: _pushNotifications,
                                onChanged: (val) => setState(() => _pushNotifications = val),
                              ),
                              const Divider(),
                              _SettingSwitch(
                                title: 'Email Alerts',
                                subtitle: 'Get detailed reports via email',
                                value: _emailAlerts,
                                onChanged: (val) => setState(() => _emailAlerts = val),
                              ),
                              const Divider(),
                              _SettingDropdown(
                                title: 'Alert Priority Threshold',
                                value: _alertThreshold,
                                items: const [
                                  'All alerts',
                                  'Medium and High priority',
                                  'High priority only',
                                ],
                                onChanged: (val) => setState(() => _alertThreshold = val!),
                              ),
                            ],
                          ),
                        ),
                      ),
                      const SizedBox(height: 16),

                      // Data & Privacy
                      Card(
                        child: Padding(
                          padding: const EdgeInsets.all(16),
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              const Text(
                                'Data & Privacy',
                                style: TextStyle(
                                  fontSize: 18,
                                  fontWeight: FontWeight.bold,
                                  color: Color(0xFF1F2937),
                                ),
                              ),
                              const SizedBox(height: 16),
                              _SettingSwitch(
                                title: 'Data Backup',
                                subtitle: 'Automatically backup hive data to cloud',
                                value: _dataBackup,
                                onChanged: (val) => setState(() => _dataBackup = val),
                              ),
                              const Divider(),
                              ListTile(
                                contentPadding: EdgeInsets.zero,
                                leading: const Icon(Icons.download, color: Color(0xFF3B82F6)),
                                title: const Text('Export Data'),
                                trailing: const Icon(Icons.chevron_right),
                                onTap: () {
                                  ScaffoldMessenger.of(context).showSnackBar(
                                    const SnackBar(content: Text('Export feature coming soon')),
                                  );
                                },
                              ),
                              const Divider(),
                              ListTile(
                                contentPadding: EdgeInsets.zero,
                                leading: const Icon(Icons.refresh, color: Color(0xFFEF4444)),
                                title: const Text(
                                  'Reset All Settings',
                                  style: TextStyle(color: Color(0xFFEF4444)),
                                ),
                                trailing: const Icon(Icons.chevron_right),
                                onTap: () async {
                                  final confirm = await showDialog<bool>(
                                    context: context,
                                    builder: (context) => AlertDialog(
                                      title: const Text('Reset Settings'),
                                      content: const Text(
                                        'Are you sure you want to reset all settings to default?',
                                      ),
                                      actions: [
                                        TextButton(
                                          onPressed: () => Navigator.pop(context, false),
                                          child: const Text('Cancel'),
                                        ),
                                        ElevatedButton(
                                          onPressed: () => Navigator.pop(context, true),
                                          style: ElevatedButton.styleFrom(
                                            backgroundColor: Colors.red,
                                          ),
                                          child: const Text('Reset'),
                                        ),
                                      ],
                                    ),
                                  );

                                  if (confirm == true && mounted) {
                                    setState(() {
                                      _temperatureAlerts = true;
                                      _weightMonitoring = true;
                                      _soundAnalysis = true;
                                      _pushNotifications = true;
                                      _emailAlerts = false;
                                      _dataBackup = true;
                                      _monitoringFrequency = 'Every 15 minutes';
                                      _alertThreshold = 'Medium and High priority';
                                    });
                                    ScaffoldMessenger.of(context).showSnackBar(
                                      const SnackBar(
                                        content: Text('Settings reset to default'),
                                      ),
                                    );
                                  }
                                },
                              ),
                            ],
                          ),
                        ),
                      ),
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
}

class _SettingSwitch extends StatelessWidget {
  final String title;
  final String subtitle;
  final bool value;
  final ValueChanged<bool> onChanged;

  const _SettingSwitch({
    required this.title,
    required this.subtitle,
    required this.value,
    required this.onChanged,
  });

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                title,
                style: const TextStyle(
                  fontWeight: FontWeight.w600,
                  color: Color(0xFF1F2937),
                ),
              ),
              const SizedBox(height: 4),
              Text(
                subtitle,
                style: const TextStyle(
                  fontSize: 12,
                  color: Color(0xFF6B7280),
                ),
              ),
            ],
          ),
        ),
        Switch(
          value: value,
          onChanged: onChanged,
          activeColor: const Color(0xFFF59E0B),
        ),
      ],
    );
  }
}

class _SettingDropdown extends StatelessWidget {
  final String title;
  final String value;
  final List<String> items;
  final ValueChanged<String?> onChanged;

  const _SettingDropdown({
    required this.title,
    required this.value,
    required this.items,
    required this.onChanged,
  });

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          title,
          style: const TextStyle(
            fontWeight: FontWeight.w600,
            color: Color(0xFF1F2937),
          ),
        ),
        const SizedBox(height: 8),
        DropdownButtonFormField<String>(
          value: value,
          decoration: InputDecoration(
            border: OutlineInputBorder(
              borderRadius: BorderRadius.circular(12),
            ),
            filled: true,
            fillColor: Colors.white,
            contentPadding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
          ),
          items: items.map((item) {
            return DropdownMenuItem(
              value: item,
              child: Text(item),
            );
          }).toList(),
          onChanged: onChanged,
        ),
      ],
    );
  }
}