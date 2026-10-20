import 'package:flutter_test/flutter_test.dart';
import 'package:mobile/core/models/telemetry_model.dart';

void main() {
  group('Telemetry Models JSON Deserialization', () {
    test('TelemetryRecord parses valid JSON correctly', () {
      final json = {
        'device_id': 'esp32-sim-01',
        'timestamp': '2026-10-20T12:00:00Z',
        'data_source': 'SIMULATED',
        'voltage_v': 230.2,
        'current_a': 1.23,
        'active_power_w': 284.0,
        'apparent_power_va': 302.1,
        'power_factor': 0.94,
        'frequency_hz': 50.01,
        'energy_kwh': 18.42,
        'is_simulated': true,
        'unattributed_power_w': 12.0,
        'story_headline': 'Pump cycle detected at 11:18 AM (+75 W)',
      };

      final record = TelemetryRecord.fromJson(json);
      expect(record.deviceId, 'esp32-sim-01');
      expect(record.dataSource, 'SIMULATED');
      expect(record.activePowerW, 284.0);
      expect(record.voltageV, 230.2);
      expect(record.isSimulated, true);
      expect(record.unattributedPowerW, 12.0);
    });

    test('DisaggregationData parses appliances and arithmetic invariants', () {
      final json = {
        'timestamp': '2026-10-20T12:00:00Z',
        'aggregate_power_w': 284.0,
        'data_source': 'SIMULATED',
        'is_simulated': true,
        'unattributed_power_w': 12.0,
        'unattributed_percentage': 4.2,
        'appliances': [
          {
            'appliance_id': 'heater_01',
            'name': 'Water Heater',
            'category': 'Heating',
            'status': 'RUNNING',
            'estimated_power_w': 140.0,
            'data_source': 'NILM_ESTIMATED',
            'confidence_score': 0.94,
            'evidence_notes': 'Resistive step',
            'timestamp': '2026-10-20T12:00:00Z',
          },
          {
            'appliance_id': 'pump_01',
            'name': 'Water Pump',
            'category': 'Motor',
            'status': 'RUNNING',
            'estimated_power_w': 75.0,
            'data_source': 'NILM_ESTIMATED',
            'confidence_score': 0.88,
            'evidence_notes': 'Inductive signature',
            'timestamp': '2026-10-20T12:00:00Z',
          },
        ],
        'story_headline': 'Pump cycle detected',
        'story_detail': 'Matches typical overhead tank refill pattern',
      };

      final disagg = DisaggregationData.fromJson(json);
      expect(disagg.aggregatePowerW, 284.0);
      expect(disagg.appliances.length, 2);
      expect(disagg.appliances[0].name, 'Water Heater');
      expect(disagg.appliances[0].estimatedPowerW, 140.0);
      expect(disagg.appliances[0].dataSource, 'NILM_ESTIMATED');
      expect(disagg.appliances[1].name, 'Water Pump');
      expect(disagg.unattributedPowerW, 12.0);
    });
  });
}
