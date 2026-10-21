import 'telemetry_model.dart';

class SimulatorAppliance {
  final String applianceId;
  final String name;
  final String category;
  final bool isOn;
  final double nominalPowerW;
  final double currentPowerW;
  final String status;
  final String? detectionCapability;
  final DateTime? lastToggledAt;

  SimulatorAppliance({
    required this.applianceId,
    required this.name,
    required this.category,
    required this.isOn,
    required this.nominalPowerW,
    required this.currentPowerW,
    required this.status,
    this.detectionCapability,
    this.lastToggledAt,
  });

  factory SimulatorAppliance.fromJson(Map<String, dynamic> json) {
    return SimulatorAppliance(
      applianceId: json['appliance_id'] as String? ?? '',
      name: json['name'] as String? ?? 'Appliance',
      category: json['category'] as String? ?? 'general',
      isOn: json['is_on'] as bool? ?? false,
      nominalPowerW: (json['nominal_power_w'] as num?)?.toDouble() ?? 0.0,
      currentPowerW: (json['current_power_w'] as num?)?.toDouble() ?? 0.0,
      status: json['status'] as String? ?? 'OFF',
      detectionCapability: json['detection_capability'] as String?,
      lastToggledAt: json['last_toggled_at'] != null
          ? parseDateTimeUtc(json['last_toggled_at'])
          : null,
    );
  }
}

class DetectedEvent {
  final String status;
  final String? applianceId;
  final String? applianceName;
  final String? transitionType;
  final double deltaPowerW;
  final String ruleDescription;
  final DateTime timestamp;
  final String dataClassification;

  DetectedEvent({
    required this.status,
    this.applianceId,
    this.applianceName,
    this.transitionType,
    required this.deltaPowerW,
    required this.ruleDescription,
    required this.timestamp,
    required this.dataClassification,
  });

  factory DetectedEvent.fromJson(Map<String, dynamic> json) {
    return DetectedEvent(
      status: json['status'] as String? ?? 'UNKNOWN',
      applianceId: json['appliance_id'] as String?,
      applianceName: json['appliance_name'] as String?,
      transitionType: json['transition_type'] as String?,
      deltaPowerW: (json['delta_power_w'] as num?)?.toDouble() ?? 0.0,
      ruleDescription: json['rule_description'] as String? ?? '',
      timestamp: parseDateTimeUtc(json['timestamp']),
      dataClassification: json['data_classification'] as String? ?? 'RULE_BASED_ESTIMATE',
    );
  }
}

class SimulatorState {
  final DateTime timestamp;
  final double aggregatePowerW;
  final double attributedPowerW;
  final double unattributedPowerW;
  final double unattributedPercentage;
  final List<SimulatorAppliance> appliances;
  final List<DetectedEvent> recentEvents;
  final String dataSource;
  final String detectorMode;
  final String? message;

  SimulatorState({
    required this.timestamp,
    required this.aggregatePowerW,
    required this.attributedPowerW,
    required this.unattributedPowerW,
    required this.unattributedPercentage,
    required this.appliances,
    required this.recentEvents,
    required this.dataSource,
    required this.detectorMode,
    this.message,
  });

  factory SimulatorState.fromJson(Map<String, dynamic> json) {
    final rawApps = json['appliances'] as List<dynamic>? ?? [];
    final rawEvents = json['recent_events'] as List<dynamic>? ?? [];
    return SimulatorState(
      timestamp: parseDateTimeUtc(json['timestamp']),
      aggregatePowerW: (json['aggregate_power_w'] as num?)?.toDouble() ?? 0.0,
      attributedPowerW: (json['attributed_power_w'] as num?)?.toDouble() ?? 0.0,
      unattributedPowerW: (json['unattributed_power_w'] as num?)?.toDouble() ?? 12.0,
      unattributedPercentage: (json['unattributed_percentage'] as num?)?.toDouble() ?? 0.0,
      appliances: rawApps.map((a) => SimulatorAppliance.fromJson(a as Map<String, dynamic>)).toList(),
      recentEvents: rawEvents.map((e) => DetectedEvent.fromJson(e as Map<String, dynamic>)).toList(),
      dataSource: json['data_source'] as String? ?? 'SIMULATED',
      detectorMode: json['detector_mode'] as String? ?? 'RULE_BASED_ESTIMATE',
      message: json['message'] as String?,
    );
  }
}
