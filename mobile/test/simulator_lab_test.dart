import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:mobile/core/models/telemetry_model.dart';
import 'package:mobile/core/models/simulator_model.dart';
import 'package:mobile/core/services/api_service.dart';
import 'package:mobile/features/dashboard/providers/dashboard_provider.dart';
import 'package:mobile/features/simulator/screens/simulator_screen.dart';
import 'package:mobile/app/theme.dart';

class InteractiveSimulatorMockApi extends ApiService {
  bool heaterOn = true;
  bool pumpOn = true;
  bool fanOn = true;
  bool bulbOn = true;
  List<DetectedEvent> events = [];
  int toggleCallCount = 0;
  int resetCallCount = 0;

  double get attributedW {
    double total = 0.0;
    if (heaterOn) total += 140.0;
    if (pumpOn) total += 75.0;
    if (fanOn) total += 45.0;
    if (bulbOn) total += 12.0;
    return total;
  }

  double get aggregateW => attributedW + 12.0;

  @override
  Future<TelemetryRecord> fetchLiveTelemetry() async {
    return TelemetryRecord(
      deviceId: 'esp32-sim-01',
      timestamp: DateTime.now(),
      dataSource: 'SIMULATED',
      voltageV: 230.2,
      currentA: aggregateW / 230.2,
      activePowerW: aggregateW,
      apparentPowerVa: aggregateW / 0.94,
      powerFactor: 0.94,
      energyKwh: 18.42,
      isSimulated: true,
      unattributedPowerW: 12.0,
      storyHeadline: 'Dynamic simulator update',
    );
  }

  @override
  Future<DisaggregationData> fetchLiveDisaggregation() async {
    return DisaggregationData(
      timestamp: DateTime.now(),
      aggregatePowerW: aggregateW,
      dataSource: 'SIMULATED',
      isSimulated: true,
      unattributedPowerW: 12.0,
      unattributedPercentage: (12.0 / aggregateW) * 100.0,
      appliances: [
        ApplianceEstimate(
          applianceId: 'heater_01',
          name: 'Water Heater',
          category: 'Heating',
          status: heaterOn ? 'RUNNING' : 'OFF',
          estimatedPowerW: heaterOn ? 140.0 : 0.0,
          dataSource: 'NILM_ESTIMATED',
          confidenceScore: heaterOn ? 0.94 : null,
          evidenceNotes: heaterOn ? 'Resistive step' : 'Appliance is OFF',
          timestamp: DateTime.now(),
        ),
        ApplianceEstimate(
          applianceId: 'pump_01',
          name: 'Water Pump',
          category: 'Motor',
          status: pumpOn ? 'RUNNING' : 'OFF',
          estimatedPowerW: pumpOn ? 75.0 : 0.0,
          dataSource: 'NILM_ESTIMATED',
          confidenceScore: pumpOn ? 0.88 : null,
          evidenceNotes: pumpOn ? 'Motor inductive' : 'Appliance is OFF',
          timestamp: DateTime.now(),
        ),
      ],
    );
  }

  @override
  Future<List<HistoryPoint>> fetchHistory({int minutes = 60}) async {
    return [
      HistoryPoint(timestamp: DateTime.now(), activePowerW: aggregateW, dataSource: 'SIMULATED'),
    ];
  }

  @override
  Future<SimulatorState> fetchSimulatorState() async {
    return SimulatorState(
      timestamp: DateTime.now(),
      aggregatePowerW: aggregateW,
      attributedPowerW: attributedW,
      unattributedPowerW: 12.0,
      unattributedPercentage: (12.0 / aggregateW) * 100.0,
      appliances: [
        SimulatorAppliance(
          applianceId: 'heater_01',
          name: 'Water Heater',
          category: 'Heating',
          isOn: heaterOn,
          nominalPowerW: 140.0,
          currentPowerW: heaterOn ? 140.0 : 0.0,
          status: heaterOn ? 'RUNNING' : 'OFF',
        ),
        SimulatorAppliance(
          applianceId: 'pump_01',
          name: 'Water Pump',
          category: 'Motor',
          isOn: pumpOn,
          nominalPowerW: 75.0,
          currentPowerW: pumpOn ? 75.0 : 0.0,
          status: pumpOn ? 'RUNNING' : 'OFF',
        ),
        SimulatorAppliance(
          applianceId: 'fan_01',
          name: 'Ceiling Fan',
          category: 'Motor',
          isOn: fanOn,
          nominalPowerW: 45.0,
          currentPowerW: fanOn ? 45.0 : 0.0,
          status: fanOn ? 'RUNNING' : 'OFF',
        ),
        SimulatorAppliance(
          applianceId: 'bulb_01',
          name: 'LED Bulb',
          category: 'Lighting',
          isOn: bulbOn,
          nominalPowerW: 12.0,
          currentPowerW: bulbOn ? 12.0 : 0.0,
          status: bulbOn ? 'RUNNING' : 'OFF',
        ),
      ],
      recentEvents: events,
      dataSource: 'SIMULATED',
      detectorMode: 'RULE_BASED_ESTIMATE',
    );
  }

  @override
  Future<SimulatorState> toggleSimulatorAppliance(
    String applianceId, {
    String? targetState,
  }) async {
    toggleCallCount++;
    if (applianceId == 'heater_01') {
      heaterOn = targetState == 'ON' ? true : (targetState == 'OFF' ? false : !heaterOn);
      events.insert(
        0,
        DetectedEvent(
          status: 'MATCHED',
          applianceId: 'heater_01',
          applianceName: 'Water Heater',
          transitionType: heaterOn ? 'ON' : 'OFF',
          deltaPowerW: heaterOn ? 140.0 : -140.0,
          ruleDescription: 'Rule-based match: Water Heater ${heaterOn ? "ON" : "OFF"}',
          timestamp: DateTime.now(),
          dataClassification: 'RULE_BASED_ESTIMATE',
        ),
      );
    }
    return fetchSimulatorState();
  }

  @override
  Future<SimulatorState> resetSimulator() async {
    resetCallCount++;
    heaterOn = true;
    pumpOn = true;
    fanOn = true;
    bulbOn = true;
    events.clear();
    return fetchSimulatorState();
  }
}

void main() {
  group('Simulator Lab & Rule-Based NILM UI Tests', () {
    testWidgets('Simulator Lab renders switches, accounting bar, and truth-in-reporting badges', (WidgetTester tester) async {
      tester.view.physicalSize = const Size(1179, 2556);
      tester.view.devicePixelRatio = 3.0;
      addTearDown(() => tester.view.resetPhysicalSize());

      final mockApi = InteractiveSimulatorMockApi();

      await tester.pumpWidget(
        ProviderScope(
          overrides: [
            apiServiceProvider.overrideWithValue(mockApi),
          ],
          child: MaterialApp(
            theme: EnergyMirrorTheme.darkTheme,
            home: const SimulatorScreen(),
          ),
        ),
      );

      await tester.pump();
      await tester.pump(const Duration(milliseconds: 100));

      // 1. Verify Simulator Lab panel title and badges
      expect(find.text('SIMULATOR LAB'), findsOneWidget);
      expect(find.text('SIMULATED TELEMETRY'), findsWidgets);
      expect(find.text('RULE-BASED ESTIMATE'), findsWidgets);

      // 2. Verify Accounting Bar
      expect(find.text('AGGREGATE'), findsWidgets);
      expect(find.text('ATTRIBUTED'), findsWidgets);
      expect(find.text('ASSUMED RESIDUAL'), findsOneWidget);
      expect(find.text('284 W'), findsWidgets); // aggregate
      expect(find.text('272 W'), findsOneWidget); // attributed
      expect(find.text('12 W'), findsWidgets); // assumed residual

      // 3. Verify 4 Switches
      expect(find.byType(Switch), findsNWidgets(4));
    });

    testWidgets('Toggling appliance updates simulator state and recalculates aggregate power', (WidgetTester tester) async {
      tester.view.physicalSize = const Size(1179, 2556);
      tester.view.devicePixelRatio = 3.0;
      addTearDown(() => tester.view.resetPhysicalSize());

      final mockApi = InteractiveSimulatorMockApi();

      await tester.pumpWidget(
        ProviderScope(
          overrides: [
            apiServiceProvider.overrideWithValue(mockApi),
          ],
          child: MaterialApp(
            theme: EnergyMirrorTheme.darkTheme,
            home: const SimulatorScreen(),
          ),
        ),
      );

      // Complete initial async load
      await tester.pump();
      await tester.pump(const Duration(milliseconds: 100));

      // Toggle first switch (Water Heater OFF)
      final switches = find.byType(Switch);
      await tester.tap(switches.first);
      await tester.pump();
      await tester.pump(const Duration(milliseconds: 100));

      // Verify mock was called
      expect(mockApi.toggleCallCount, 1);
      expect(mockApi.heaterOn, isFalse);
      expect(mockApi.aggregateW, 144.0); // 284 - 140 = 144 W

      // Verify UI updated aggregate readout
      expect(find.text('144 W'), findsWidgets);
      expect(find.text('132 W'), findsOneWidget); // 272 - 140 = 132 W attributed

      // Verify detected event appeared in the list
      expect(find.text('MATCHED'), findsOneWidget);
      expect(find.text('Rule-based match: Water Heater OFF'), findsOneWidget);
      expect(find.text('-140 W'), findsOneWidget);
    });

    testWidgets('Reset button restores baseline configuration', (WidgetTester tester) async {
      tester.view.physicalSize = const Size(1179, 2556);
      tester.view.devicePixelRatio = 3.0;
      addTearDown(() => tester.view.resetPhysicalSize());

      final mockApi = InteractiveSimulatorMockApi();
      mockApi.heaterOn = false; // Start with heater OFF

      await tester.pumpWidget(
        ProviderScope(
          overrides: [
            apiServiceProvider.overrideWithValue(mockApi),
          ],
          child: MaterialApp(
            theme: EnergyMirrorTheme.darkTheme,
            home: const SimulatorScreen(),
          ),
        ),
      );

      // Complete initial async load
      await tester.pump();
      await tester.pump(const Duration(milliseconds: 100));

      // Find reset icon button
      final resetBtn = find.byIcon(Icons.restart_alt_rounded);
      expect(resetBtn, findsOneWidget);

      await tester.tap(resetBtn);
      await tester.pump();
      await tester.pump(const Duration(milliseconds: 100));

      expect(mockApi.resetCallCount, 1);
      expect(mockApi.heaterOn, isTrue);
      expect(mockApi.aggregateW, 284.0);
    });
  });
}
