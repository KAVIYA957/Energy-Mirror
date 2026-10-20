import 'telemetry_model.dart';

class SystemDiagnosticsData {
  final String status;
  final String appName;
  final String appVersion;
  final DateTime serverTimestamp;
  final String activeTelemetrySource;
  final bool hardwareIngestionEnabled;
  final String hardwareMode;
  final bool databaseConnected;
  final String databaseType;
  final int databaseRecordCount;
  final bool simulatorActive;
  final int simulatorAppliancesCount;
  final double simulatorAggregateW;
  final double unattributedBaselineW;
  final int recentEventsCount;
  final String nilmDetectorMode;
  final String nilmMethodology;
  final String dataClassification;

  SystemDiagnosticsData({
    required this.status,
    required this.appName,
    required this.appVersion,
    required this.serverTimestamp,
    required this.activeTelemetrySource,
    required this.hardwareIngestionEnabled,
    required this.hardwareMode,
    required this.databaseConnected,
    required this.databaseType,
    required this.databaseRecordCount,
    required this.simulatorActive,
    required this.simulatorAppliancesCount,
    required this.simulatorAggregateW,
    required this.unattributedBaselineW,
    required this.recentEventsCount,
    required this.nilmDetectorMode,
    required this.nilmMethodology,
    required this.dataClassification,
  });

  factory SystemDiagnosticsData.fromJson(Map<String, dynamic> json) {
    return SystemDiagnosticsData(
      status: json['status'] as String? ?? 'unknown',
      appName: json['app_name'] as String? ?? 'Energy Mirror',
      appVersion: json['app_version'] as String? ?? '1.0.0',
      serverTimestamp: parseDateTimeUtc(json['server_timestamp']),
      activeTelemetrySource: json['active_telemetry_source'] as String? ?? 'SIMULATED',
      hardwareIngestionEnabled: json['hardware_ingestion_enabled'] as bool? ?? false,
      hardwareMode: json['hardware_mode'] as String? ?? 'STAGED_INACTIVE',
      databaseConnected: json['database_connected'] as bool? ?? false,
      databaseType: json['database_type'] as String? ?? 'SQLite',
      databaseRecordCount: (json['database_record_count'] as num?)?.toInt() ?? 0,
      simulatorActive: json['simulator_active'] as bool? ?? true,
      simulatorAppliancesCount: (json['simulator_appliances_count'] as num?)?.toInt() ?? 4,
      simulatorAggregateW: (json['simulator_aggregate_w'] as num?)?.toDouble() ?? 284.0,
      unattributedBaselineW: (json['unattributed_baseline_w'] as num?)?.toDouble() ?? 12.0,
      recentEventsCount: (json['recent_events_count'] as num?)?.toInt() ?? 0,
      nilmDetectorMode: json['nilm_detector_mode'] as String? ?? 'RULE_BASED_ESTIMATE',
      nilmMethodology: json['nilm_methodology'] as String? ?? 'Derivative Step Detection',
      dataClassification: json['data_classification'] as String? ?? 'SIMULATED_SYSTEM_DIAGNOSTICS',
    );
  }
}
