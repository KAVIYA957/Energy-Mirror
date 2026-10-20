import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:mobile/core/models/telemetry_model.dart';
import 'package:mobile/core/models/simulator_model.dart';
import 'package:mobile/core/services/api_service.dart';
import 'package:mobile/features/dashboard/providers/dashboard_provider.dart';
import 'package:mobile/features/dashboard/screens/dashboard_screen.dart';
import 'package:mobile/app/theme.dart';

class MockApiService extends ApiService {
  @override
  Future<TelemetryRecord> fetchLiveTelemetry() async {
    return TelemetryRecord(
      deviceId: 'esp32-sim-01',
      timestamp: DateTime.now(),
      dataSource: 'SIMULATED',
      voltageV: 230.2,
      currentA: 1.23,
      activePowerW: 284.0,
      apparentPowerVa: 302.1,
      powerFactor: 0.94,
      energyKwh: 18.42,
      isSimulated: true,
      unattributedPowerW: 12.0,
      storyHeadline: 'Pump cycle detected at 11:18 AM (+75 W)',
    );
  }

  @override
  Future<DisaggregationData> fetchLiveDisaggregation() async {
    return DisaggregationData(
      timestamp: DateTime.now(),
      aggregatePowerW: 284.0,
      dataSource: 'SIMULATED',
      isSimulated: true,
      unattributedPowerW: 12.0,
      unattributedPercentage: 4.2,
      appliances: [
        ApplianceEstimate(
          applianceId: 'heater_01',
          name: 'Water Heater',
          category: 'Heating',
          status: 'RUNNING',
          estimatedPowerW: 140.0,
          dataSource: 'NILM_ESTIMATED',
          confidenceScore: 0.94,
          evidenceNotes: 'Sharp resistive step',
          timestamp: DateTime.now(),
        ),
        ApplianceEstimate(
          applianceId: 'pump_01',
          name: 'Water Pump',
          category: 'Motor',
          status: 'RUNNING',
          estimatedPowerW: 75.0,
          dataSource: 'NILM_ESTIMATED',
          confidenceScore: 0.88,
          evidenceNotes: 'Inductive motor inrush',
          timestamp: DateTime.now(),
        ),
        ApplianceEstimate(
          applianceId: 'fan_01',
          name: 'Ceiling Fan',
          category: 'Motor',
          status: 'RUNNING',
          estimatedPowerW: 45.0,
          dataSource: 'NILM_ESTIMATED',
          confidenceScore: 0.91,
          evidenceNotes: 'Steady rotary load',
          timestamp: DateTime.now(),
        ),
        ApplianceEstimate(
          applianceId: 'bulb_01',
          name: 'LED Bulb',
          category: 'Lighting',
          status: 'RUNNING',
          estimatedPowerW: 12.0,
          dataSource: 'NILM_ESTIMATED',
          confidenceScore: 0.85,
          evidenceNotes: 'Low wattage baseline step',
          timestamp: DateTime.now(),
        ),
      ],
      storyHeadline: 'Pump cycle detected at 11:18 AM (+75 W)',
      storyDetail: 'Matches typical overhead tank refill pattern based on duration and inductive current signature.',
    );
  }

  @override
  Future<List<HistoryPoint>> fetchHistory({int minutes = 60}) async {
    return [
      HistoryPoint(timestamp: DateTime.now().subtract(const Duration(minutes: 60)), activePowerW: 69.0, dataSource: 'SIMULATED'),
      HistoryPoint(timestamp: DateTime.now().subtract(const Duration(minutes: 30)), activePowerW: 209.0, dataSource: 'SIMULATED'),
      HistoryPoint(timestamp: DateTime.now(), activePowerW: 284.0, dataSource: 'SIMULATED'),
    ];
  }

  @override
  Future<SimulatorState> fetchSimulatorState() async {
    return SimulatorState(
      timestamp: DateTime.now(),
      aggregatePowerW: 284.0,
      attributedPowerW: 272.0,
      unattributedPowerW: 12.0,
      unattributedPercentage: 4.2,
      appliances: [
        SimulatorAppliance(
          applianceId: 'heater_01',
          name: 'Water Heater',
          category: 'Heating',
          isOn: true,
          nominalPowerW: 140.0,
          currentPowerW: 140.0,
          status: 'RUNNING',
        ),
        SimulatorAppliance(
          applianceId: 'pump_01',
          name: 'Water Pump',
          category: 'Motor',
          isOn: true,
          nominalPowerW: 75.0,
          currentPowerW: 75.0,
          status: 'RUNNING',
        ),
        SimulatorAppliance(
          applianceId: 'fan_01',
          name: 'Ceiling Fan',
          category: 'Motor',
          isOn: true,
          nominalPowerW: 45.0,
          currentPowerW: 45.0,
          status: 'RUNNING',
        ),
        SimulatorAppliance(
          applianceId: 'bulb_01',
          name: 'LED Bulb',
          category: 'Lighting',
          isOn: true,
          nominalPowerW: 12.0,
          currentPowerW: 12.0,
          status: 'RUNNING',
        ),
      ],
      recentEvents: [],
      dataSource: 'SIMULATED',
      detectorMode: 'RULE_BASED_ESTIMATE',
    );
  }

  @override
  Future<SimulatorState> toggleSimulatorAppliance(
    String applianceId, {
    String? targetState,
  }) async {
    return fetchSimulatorState();
  }

  @override
  Future<SimulatorState> resetSimulator() async {
    return fetchSimulatorState();
  }
}

void main() {
  testWidgets('Energy Mirror Living Current dashboard renders all components correctly', (WidgetTester tester) async {
    // Set standard mobile viewport (393 x 852 logical)
    tester.view.physicalSize = const Size(1179, 2556);
    tester.view.devicePixelRatio = 3.0;
    addTearDown(() => tester.view.resetPhysicalSize());

    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          apiServiceProvider.overrideWithValue(MockApiService()),
        ],
        child: MaterialApp(
          theme: EnergyMirrorTheme.darkTheme,
          home: const DashboardScreen(),
        ),
      ),
    );

    // Initial load
    await tester.pump();
    await tester.pump(const Duration(milliseconds: 100));

    // 1. Verify Header and Truth-in-Reporting Elements
    expect(find.text('ENERGY MIRROR'), findsOneWidget);
    expect(find.text('SIMULATED DATA'), findsOneWidget);
    expect(find.text('SIMULATED AGGREGATE'), findsOneWidget);
    expect(find.text('NILM ESTIMATED'), findsOneWidget);

    // 2. Verify Energy Pulse Readout
    expect(find.text('284'), findsOneWidget);
    expect(find.text('W'), findsOneWidget);
    expect(find.text('Aggregate Load'), findsOneWidget);

    // 3. Verify Appliance Constellation Nodes
    expect(find.text('Water Heater'), findsWidgets);
    expect(find.text('Water Pump'), findsWidgets);
    expect(find.text('Ceiling Fan'), findsWidgets);
    expect(find.text('LED Bulb'), findsWidgets);

    // 4. Verify Load Reconciliation & Unattributed Residual
    expect(find.text('LOAD RECONCILIATION'), findsOneWidget);
    expect(find.text('Unattributed Residual'), findsOneWidget);

    // 5. Verify Simulator Lab Panel & Rule-Based Estimations
    expect(find.text('SIMULATOR LAB'), findsOneWidget);
    expect(find.text('SIMULATED TELEMETRY'), findsWidgets);
    expect(find.text('RULE-BASED ESTIMATE'), findsWidgets);

    // 6. Verify Editorial Insight Story
    expect(find.text('EDITORIAL INSIGHT'), findsOneWidget);
    expect(find.text('Pump cycle detected at 11:18 AM (+75 W)'), findsOneWidget);

    // 7. Test Interactive Detail Modal Sheet
    await tester.tap(find.text('Water Pump').first);
    await tester.pump(const Duration(milliseconds: 300));
    await tester.pump(const Duration(milliseconds: 300));

    expect(find.text('OPERATING STATE'), findsOneWidget);
    expect(find.text('RUNNING'), findsOneWidget);
    expect(find.text('INFERENCE EVIDENCE & REASONING'), findsOneWidget);
    expect(find.text('Inductive motor inrush'), findsOneWidget);

    // Close modal
    await tester.tap(find.text('Close'));
    await tester.pump(const Duration(milliseconds: 300));
    await tester.pump(const Duration(milliseconds: 300));
  });
}
