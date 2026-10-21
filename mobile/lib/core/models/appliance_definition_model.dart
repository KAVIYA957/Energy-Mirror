import 'telemetry_model.dart';

class ApplianceDefinition {
  final int id;
  final String applianceId;
  final String name;
  final String category;
  final double nominalPowerW;
  final double? expectedPf;
  final double? toleranceW;
  final double? pfTolerance;
  final bool isEnabled;
  final bool isSimulatorSupported;
  final String detectionCapability;
  final double? confidenceScore;
  final String? evidenceNotes;
  final DateTime createdAt;
  final DateTime updatedAt;

  ApplianceDefinition({
    this.id = 0,
    required this.applianceId,
    required this.name,
    required this.category,
    required this.nominalPowerW,
    this.expectedPf,
    this.toleranceW,
    this.pfTolerance,
    this.isEnabled = true,
    this.isSimulatorSupported = true,
    this.detectionCapability = 'UNSUPPORTED',
    this.confidenceScore,
    this.evidenceNotes,
    DateTime? createdAt,
    DateTime? updatedAt,
  })  : createdAt = createdAt ?? DateTime.fromMillisecondsSinceEpoch(0, isUtc: true),
        updatedAt = updatedAt ?? DateTime.fromMillisecondsSinceEpoch(0, isUtc: true);

  String? get description => evidenceNotes;

  bool get isProtected => const {'heater_01', 'pump_01', 'fan_01', 'bulb_01'}.contains(applianceId);

  factory ApplianceDefinition.fromJson(Map<String, dynamic> json) {
    return ApplianceDefinition(
      id: (json['id'] as num?)?.toInt() ?? 0,
      applianceId: json['appliance_id'] as String? ?? '',
      name: json['name'] as String? ?? 'Unnamed Appliance',
      category: json['category'] as String? ?? 'General',
      nominalPowerW: (json['nominal_power_w'] as num?)?.toDouble() ?? 0.0,
      expectedPf: (json['expected_pf'] as num?)?.toDouble(),
      toleranceW: (json['tolerance_w'] as num?)?.toDouble(),
      pfTolerance: (json['pf_tolerance'] as num?)?.toDouble(),
      isEnabled: json['is_enabled'] as bool? ?? true,
      isSimulatorSupported: json['is_simulator_supported'] as bool? ?? true,
      detectionCapability: json['detection_capability'] as String? ?? 'UNSUPPORTED',
      confidenceScore: (json['confidence_score'] as num?)?.toDouble(),
      evidenceNotes: json['evidence_notes'] as String?,
      createdAt: parseDateTimeUtc(json['created_at']),
      updatedAt: parseDateTimeUtc(json['updated_at']),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'appliance_id': applianceId,
      'name': name,
      'category': category,
      'nominal_power_w': nominalPowerW,
      'expected_pf': expectedPf,
      'tolerance_w': toleranceW,
      'pf_tolerance': pfTolerance,
      'is_enabled': isEnabled,
      'is_simulator_supported': isSimulatorSupported,
      'detection_capability': detectionCapability,
      'confidence_score': confidenceScore,
      'evidence_notes': evidenceNotes,
      'created_at': createdAt.toIso8601String(),
      'updated_at': updatedAt.toIso8601String(),
    };
  }
}
