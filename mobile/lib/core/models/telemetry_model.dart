/// Safely parses an ISO-8601 string into a local DateTime, ensuring naive UTC strings are treated as UTC.
DateTime parseDateTimeUtc(dynamic val) {
  if (val == null) return DateTime.now();
  final str = val.toString().trim();
  if (str.isEmpty) return DateTime.now();
  // If string does not contain 'Z' or timezone offset (+/-), append 'Z' so it is parsed as UTC.
  final normalized = (str.endsWith('Z') || str.contains('+') || (str.length > 10 && str.substring(10).contains('-')))
      ? str
      : '${str}Z';
  return (DateTime.tryParse(normalized) ?? DateTime.now()).toLocal();
}

class ApplianceEstimate {
  final String applianceId;
  final String name;
  final String category;
  final String status;
  final double estimatedPowerW;
  final double? nominalPowerW;
  final String? detectionCapability;
  final String dataSource;
  final double? confidenceScore;
  final String? evidenceNotes;
  final DateTime timestamp;

  ApplianceEstimate({
    required this.applianceId,
    required this.name,
    required this.category,
    required this.status,
    required this.estimatedPowerW,
    this.nominalPowerW,
    this.detectionCapability,
    required this.dataSource,
    this.confidenceScore,
    this.evidenceNotes,
    required this.timestamp,
  });

  factory ApplianceEstimate.fromJson(Map<String, dynamic> json) {
    return ApplianceEstimate(
      applianceId: json['appliance_id'] as String? ?? 'unknown',
      name: json['name'] as String? ?? 'Appliance',
      category: json['category'] as String? ?? 'general',
      status: json['status'] as String? ?? 'RUNNING',
      estimatedPowerW: (json['estimated_power_w'] as num?)?.toDouble() ?? 0.0,
      nominalPowerW: (json['nominal_power_w'] as num?)?.toDouble(),
      detectionCapability: json['detection_capability'] as String?,
      dataSource: json['data_source'] as String? ?? 'NILM_ESTIMATED',
      confidenceScore: (json['confidence_score'] as num?)?.toDouble(),
      evidenceNotes: json['evidence_notes'] as String?,
      timestamp: parseDateTimeUtc(json['timestamp']),
    );
  }
}

class TelemetryRecord {
  final String deviceId;
  final DateTime timestamp;
  final String dataSource;
  final double? voltageV;
  final double? currentA;
  final double activePowerW;
  final double? apparentPowerVa;
  final double? powerFactor;
  final double? frequencyHz;
  final double? energyKwh;
  final bool isSimulated;
  final double unattributedPowerW;
  final String? storyHeadline;

  TelemetryRecord({
    required this.deviceId,
    required this.timestamp,
    required this.dataSource,
    this.voltageV,
    this.currentA,
    required this.activePowerW,
    this.apparentPowerVa,
    this.powerFactor,
    this.frequencyHz,
    this.energyKwh,
    required this.isSimulated,
    required this.unattributedPowerW,
    this.storyHeadline,
  });

  factory TelemetryRecord.fromJson(Map<String, dynamic> json) {
    return TelemetryRecord(
      deviceId: json['device_id'] as String? ?? 'esp32-sim-01',
      timestamp: parseDateTimeUtc(json['timestamp']),
      dataSource: json['data_source'] as String? ?? 'SIMULATED',
      voltageV: (json['voltage_v'] as num?)?.toDouble(),
      currentA: (json['current_a'] as num?)?.toDouble(),
      activePowerW: (json['active_power_w'] as num?)?.toDouble() ?? 0.0,
      apparentPowerVa: (json['apparent_power_va'] as num?)?.toDouble(),
      powerFactor: (json['power_factor'] as num?)?.toDouble(),
      frequencyHz: (json['frequency_hz'] as num?)?.toDouble(),
      energyKwh: (json['energy_kwh'] as num?)?.toDouble(),
      isSimulated: json['is_simulated'] as bool? ?? true,
      unattributedPowerW: (json['unattributed_power_w'] as num?)?.toDouble() ?? 0.0,
      storyHeadline: json['story_headline'] as String?,
    );
  }
}

class DisaggregationData {
  final DateTime timestamp;
  final double aggregatePowerW;
  final String dataSource;
  final bool isSimulated;
  final double unattributedPowerW;
  final double unattributedPercentage;
  final List<ApplianceEstimate> appliances;
  final String? storyHeadline;
  final String? storyDetail;

  DisaggregationData({
    required this.timestamp,
    required this.aggregatePowerW,
    required this.dataSource,
    required this.isSimulated,
    required this.unattributedPowerW,
    required this.unattributedPercentage,
    required this.appliances,
    this.storyHeadline,
    this.storyDetail,
  });

  factory DisaggregationData.fromJson(Map<String, dynamic> json) {
    final rawList = json['appliances'] as List<dynamic>? ?? [];
    final appliances = rawList
        .map((item) => ApplianceEstimate.fromJson(item as Map<String, dynamic>))
        .toList();

    return DisaggregationData(
      timestamp: parseDateTimeUtc(json['timestamp']),
      aggregatePowerW: (json['aggregate_power_w'] as num?)?.toDouble() ?? 0.0,
      dataSource: json['data_source'] as String? ?? 'SIMULATED',
      isSimulated: json['is_simulated'] as bool? ?? true,
      unattributedPowerW: (json['unattributed_power_w'] as num?)?.toDouble() ?? 0.0,
      unattributedPercentage: (json['unattributed_percentage'] as num?)?.toDouble() ?? 0.0,
      appliances: appliances,
      storyHeadline: json['story_headline'] as String?,
      storyDetail: json['story_detail'] as String?,
    );
  }
}

class HistoryPoint {
  final DateTime timestamp;
  final double activePowerW;
  final String dataSource;
  final String? applianceEvent;

  HistoryPoint({
    required this.timestamp,
    required this.activePowerW,
    required this.dataSource,
    this.applianceEvent,
  });

  factory HistoryPoint.fromJson(Map<String, dynamic> json) {
    return HistoryPoint(
      timestamp: parseDateTimeUtc(json['timestamp']),
      activePowerW: (json['active_power_w'] as num?)?.toDouble() ?? 0.0,
      dataSource: json['data_source'] as String? ?? 'SIMULATED',
      applianceEvent: json['appliance_event'] as String?,
    );
  }
}

class PersistedEvent {
  final int? id;
  final DateTime timestamp;
  final String status;
  final String? applianceId;
  final String? applianceName;
  final String? transitionType;
  final double deltaPowerW;
  final double? deltaPf;
  final String ruleDescription;
  final String dataClassification;

  PersistedEvent({
    this.id,
    required this.timestamp,
    required this.status,
    this.applianceId,
    this.applianceName,
    this.transitionType,
    required this.deltaPowerW,
    this.deltaPf,
    required this.ruleDescription,
    this.dataClassification = 'RULE_BASED_ESTIMATE',
  });

  factory PersistedEvent.fromJson(Map<String, dynamic> json) {
    return PersistedEvent(
      id: (json['id'] as num?)?.toInt(),
      timestamp: parseDateTimeUtc(json['timestamp']),
      status: json['status'] as String? ?? 'MATCHED',
      applianceId: json['appliance_id'] as String?,
      applianceName: json['appliance_name'] as String?,
      transitionType: json['transition_type'] as String?,
      deltaPowerW: (json['delta_power_w'] as num?)?.toDouble() ?? 0.0,
      deltaPf: (json['delta_pf'] as num?)?.toDouble(),
      ruleDescription: json['rule_description'] as String? ?? '',
      dataClassification: json['data_classification'] as String? ?? 'RULE_BASED_ESTIMATE',
    );
  }
}

class HistoryResponseData {
  final int intervalMinutes;
  final int count;
  final List<HistoryPoint> points;
  final int? availableRangeMinutes;
  final String dataSource;
  final bool isSimulated;
  final List<PersistedEvent> events;

  HistoryResponseData({
    required this.intervalMinutes,
    required this.count,
    required this.points,
    this.availableRangeMinutes,
    required this.dataSource,
    required this.isSimulated,
    this.events = const [],
  });

  factory HistoryResponseData.fromJson(Map<String, dynamic> json) {
    final rawList = json['points'] as List<dynamic>? ?? [];
    final rawEvents = json['events'] as List<dynamic>? ?? [];
    return HistoryResponseData(
      intervalMinutes: (json['interval_minutes'] as num?)?.toInt() ?? 60,
      count: (json['count'] as num?)?.toInt() ?? 0,
      points: rawList.map((pt) => HistoryPoint.fromJson(pt as Map<String, dynamic>)).toList(),
      availableRangeMinutes: (json['available_range_minutes'] as num?)?.toInt(),
      dataSource: json['data_source'] as String? ?? 'SIMULATED',
      isSimulated: json['is_simulated'] as bool? ?? true,
      events: rawEvents.map((e) => PersistedEvent.fromJson(e as Map<String, dynamic>)).toList(),
    );
  }
}

