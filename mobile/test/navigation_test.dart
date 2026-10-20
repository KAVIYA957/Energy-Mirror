import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:mobile/core/models/telemetry_model.dart';
import 'package:mobile/core/models/simulator_model.dart';
import 'package:mobile/core/models/diagnostics_model.dart';
import 'package:mobile/core/services/api_service.dart';
import 'package:mobile/features/dashboard/providers/dashboard_provider.dart';
import 'package:mobile/app/routes.dart';
import 'package:mobile/app/theme.dart';

class NavMockApiService extends ApiService {
  @override
  Future<TelemetryRecord> fetchLiveTelemetry() async {
    return TelemetryRecord(
      deviceId: 'esp32-sim-01',
      timestamp: DateTime.now(),
      dataSource: 'SIMULATED',
      voltageV: 230.0,
      currentA: 1.23,
      activePowerW: 284.0,
      apparentPowerVa: 302.0,
      powerFactor: 0.94,
      energyKwh: 18.42,
      isSimulated: true,
      unattributedPowerW: 12.0,
      storyHeadline: 'Nav test live record',
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
          applianceId: 'bulb_01',
          name: 'LED Bulb',
          category: 'Lighting',
          status: 'RUNNING',
          estimatedPowerW: 12.0,
          dataSource: 'NILM_ESTIMATED',
          confidenceScore: 0.85,
          evidenceNotes: 'Baseline active',
          timestamp: DateTime.now(),
        ),
      ],
    );
  }

  @override
  Future<List<HistoryPoint>> fetchHistory({int minutes = 60}) async {
    return [
      HistoryPoint(timestamp: DateTime.now(), activePowerW: 284.0, dataSource: 'SIMULATED'),
    ];
  }

  @override
  Future<HistoryResponseData> fetchHistoryWithMetadata({int minutes = 60}) async {
    return HistoryResponseData(
      intervalMinutes: minutes,
      count: 1,
      points: [
        HistoryPoint(timestamp: DateTime.now(), activePowerW: 284.0, dataSource: 'SIMULATED'),
      ],
      availableRangeMinutes: 60,
      dataSource: 'SIMULATED',
      isSimulated: true,
    );
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
      message: 'Running',
    );
  }

  @override
  Future<SystemDiagnosticsData> fetchSystemDiagnostics() async {
    return SystemDiagnosticsData(
      status: 'healthy',
      appName: 'Energy Mirror Backend',
      appVersion: '1.0.0',
      serverTimestamp: DateTime.now(),
      activeTelemetrySource: 'SIMULATED',
      hardwareIngestionEnabled: false,
      hardwareMode: 'STAGED_INACTIVE',
      databaseConnected: true,
      databaseType: 'SQLite',
      databaseRecordCount: 64,
      simulatorActive: true,
      simulatorAppliancesCount: 4,
      simulatorAggregateW: 284.0,
      unattributedBaselineW: 12.0,
      recentEventsCount: 1,
      nilmDetectorMode: 'RULE_BASED_DERIVATIVE_ESTIMATOR',
      nilmMethodology: 'Derivative threshold matching (|Delta P| step detection)',
      dataClassification: 'SIMULATED_AND_RULE_BASED_ESTIMATES',
    );
  }
}

void main() {
  group('Multi-Screen Navigation & Responsive Layout Tests', () {
    testWidgets('Compact screen renders NavigationBar with 4 destinations', (WidgetTester tester) async {
      tester.view.physicalSize = const Size(393 * 3, 852 * 3);
      tester.view.devicePixelRatio = 3.0;
      addTearDown(() => tester.view.resetPhysicalSize());

      final router = createRouter(initialLocation: '/');

      await tester.pumpWidget(
        ProviderScope(
          overrides: [
            apiServiceProvider.overrideWithValue(NavMockApiService()),
          ],
          child: MaterialApp.router(
            theme: EnergyMirrorTheme.darkTheme,
            routerConfig: router,
          ),
        ),
      );

      await tester.pump();
      await tester.pump(const Duration(milliseconds: 100));

      // Verify compact view renders NavigationBar (not NavigationRail)
      expect(find.byType(NavigationBar), findsOneWidget);
      expect(find.byType(NavigationRail), findsNothing);

      // Verify 4 destinations exist
      expect(find.text('Dashboard'), findsOneWidget);
      expect(find.text('History'), findsOneWidget);
      expect(find.text('Simulator'), findsOneWidget);
      expect(find.text('Diagnostics'), findsOneWidget);
    });

    testWidgets('Wide screen (>= 720px) renders NavigationRail with 4 destinations', (WidgetTester tester) async {
      // 1440 x 900 desktop viewport
      tester.view.physicalSize = const Size(1440 * 1, 900 * 1);
      tester.view.devicePixelRatio = 1.0;
      addTearDown(() => tester.view.resetPhysicalSize());

      final router = createRouter(initialLocation: '/');

      await tester.pumpWidget(
        ProviderScope(
          overrides: [
            apiServiceProvider.overrideWithValue(NavMockApiService()),
          ],
          child: MaterialApp.router(
            theme: EnergyMirrorTheme.darkTheme,
            routerConfig: router,
          ),
        ),
      );

      await tester.pump();
      await tester.pump(const Duration(milliseconds: 100));

      // Verify wide view renders NavigationRail (not NavigationBar)
      expect(find.byType(NavigationRail), findsOneWidget);
      expect(find.byType(NavigationBar), findsNothing);

      // Verify sidebar branding
      expect(find.text('MIRROR'), findsOneWidget);

      // Verify 4 destinations on rail
      expect(find.text('Dashboard'), findsOneWidget);
      expect(find.text('History'), findsOneWidget);
      expect(find.text('Simulator'), findsOneWidget);
      expect(find.text('Diagnostics'), findsOneWidget);
    });

    testWidgets('Navigating among all four screens via GoRouter routes', (WidgetTester tester) async {
      tester.view.physicalSize = const Size(1179, 2556);
      tester.view.devicePixelRatio = 3.0;
      addTearDown(() => tester.view.resetPhysicalSize());

      final router = createRouter(initialLocation: '/');

      await tester.pumpWidget(
        ProviderScope(
          overrides: [
            apiServiceProvider.overrideWithValue(NavMockApiService()),
          ],
          child: MaterialApp.router(
            theme: EnergyMirrorTheme.darkTheme,
            routerConfig: router,
          ),
        ),
      );

      await tester.pump();
      await tester.pump(const Duration(milliseconds: 100));

      // 1. Dashboard: /
      expect(find.text('ENERGY MIRROR'), findsOneWidget);

      // 2. Navigate to History: /history
      router.go('/history');
      await tester.pump();
      await tester.pump(const Duration(milliseconds: 350));
      expect(find.text('ANALYTICS & HISTORY'), findsOneWidget);

      // 3. Navigate to Simulator: /simulator
      router.go('/simulator');
      await tester.pump();
      await tester.pump(const Duration(milliseconds: 350));
      expect(find.text('METHODOLOGICAL ARCHITECTURE'), findsOneWidget);

      // 4. Navigate to Diagnostics: /diagnostics
      router.go('/diagnostics');
      await tester.pump();
      await tester.pump(const Duration(milliseconds: 350));
      expect(find.text('SYSTEM DIAGNOSTICS'), findsOneWidget);
      expect(find.text('BACKEND CONNECTIVITY'), findsOneWidget);
    });

    testWidgets('Tapping NavigationBar items navigates to matching screens', (WidgetTester tester) async {
      tester.view.physicalSize = const Size(1179, 2556);
      tester.view.devicePixelRatio = 3.0;
      addTearDown(() => tester.view.resetPhysicalSize());

      final router = createRouter(initialLocation: '/');

      await tester.pumpWidget(
        ProviderScope(
          overrides: [
            apiServiceProvider.overrideWithValue(NavMockApiService()),
          ],
          child: MaterialApp.router(
            theme: EnergyMirrorTheme.darkTheme,
            routerConfig: router,
          ),
        ),
      );

      await tester.pump();
      await tester.pump(const Duration(milliseconds: 350));

      // Tap History in bottom nav
      await tester.tap(find.text('History'));
      await tester.pump();
      await tester.pump(const Duration(milliseconds: 350));
      expect(find.text('ANALYTICS & HISTORY'), findsOneWidget);

      // Tap Simulator in bottom nav
      await tester.tap(find.text('Simulator'));
      await tester.pump();
      await tester.pump(const Duration(milliseconds: 350));
      expect(find.text('METHODOLOGICAL ARCHITECTURE'), findsOneWidget);

      // Tap Diagnostics in bottom nav
      await tester.tap(find.text('Diagnostics'));
      await tester.pump();
      await tester.pump(const Duration(milliseconds: 350));
      expect(find.text('SYSTEM DIAGNOSTICS'), findsOneWidget);

      // Tap Dashboard in bottom nav
      await tester.tap(find.text('Dashboard'));
      await tester.pump();
      await tester.pump(const Duration(milliseconds: 350));
      expect(find.text('ENERGY MIRROR'), findsOneWidget);
    });
  });
}
