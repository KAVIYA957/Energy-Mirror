import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:mobile/core/models/diagnostics_model.dart';
import 'package:mobile/core/services/api_service.dart';
import 'package:mobile/features/dashboard/providers/dashboard_provider.dart';
import 'package:mobile/features/diagnostics/screens/diagnostics_screen.dart';
import 'package:mobile/app/theme.dart';

class DiagnosticsMockApiService extends ApiService {
  bool simulateError = false;
  int fetchCount = 0;

  @override
  Future<SystemDiagnosticsData> fetchSystemDiagnostics() async {
    fetchCount++;
    if (simulateError) {
      throw Exception('Connection refused: Backend daemon unreachable on 127.0.0.1:8000');
    }

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
  group('System Diagnostics & Privacy Audit UI Tests', () {
    testWidgets('Diagnostics renders healthy status, simulated metrology, staged hardware, and SQLite records', (WidgetTester tester) async {
      tester.view.physicalSize = const Size(1179, 2556);
      tester.view.devicePixelRatio = 3.0;
      addTearDown(() => tester.view.resetPhysicalSize());

      final mockApi = DiagnosticsMockApiService();

      await tester.pumpWidget(
        ProviderScope(
          overrides: [
            apiServiceProvider.overrideWithValue(mockApi),
          ],
          child: MaterialApp(
            theme: EnergyMirrorTheme.darkTheme,
            home: const DiagnosticsScreen(),
          ),
        ),
      );

      await tester.pump();
      await tester.pump(const Duration(milliseconds: 100));

      // 1. Header & Backend Connectivity
      expect(find.text('SYSTEM DIAGNOSTICS'), findsOneWidget);
      expect(find.text('BACKEND CONNECTIVITY'), findsOneWidget);
      expect(find.text('HEALTHY'), findsOneWidget);
      expect(find.text('1.0.0'), findsOneWidget);

      // 2. Metrology & Telemetry Source
      expect(find.text('METROLOGY & TELEMETRY SOURCE'), findsOneWidget);
      expect(find.text('SIMULATED'), findsOneWidget);
      expect(find.text('esp32-sim-01'), findsOneWidget);

      // 3. Hardware Ingestion Status
      expect(find.text('HARDWARE INGESTION STATUS'), findsOneWidget);
      expect(find.text('NONE (Simulation Mode)'), findsOneWidget);
      expect(find.text('STAGED_INACTIVE'), findsOneWidget);
      expect(find.text('ENABLE_HARDWARE_INGEST = false'), findsOneWidget);

      // 4. Simulator & NILM Subsystem
      expect(find.text('SIMULATOR & NILM SUBSYSTEM'), findsOneWidget);
      expect(find.text('ACTIVE (Deterministic)'), findsOneWidget);
      expect(find.text('4 Active Loads'), findsOneWidget);
      expect(find.text('12 W (Assumed Residual)'), findsOneWidget);

      // 5. Local Database Persistence
      expect(find.text('LOCAL DATABASE PERSISTENCE'), findsOneWidget);
      expect(find.text('SQLite'), findsOneWidget);
      expect(find.text('CONNECTED'), findsOneWidget);
      expect(find.text('64 rows'), findsOneWidget);
    });

    testWidgets('Security & Privacy Audit: zero secrets, tokens, or private paths exposed', (WidgetTester tester) async {
      tester.view.physicalSize = const Size(1179, 2556);
      tester.view.devicePixelRatio = 3.0;
      addTearDown(() => tester.view.resetPhysicalSize());

      final mockApi = DiagnosticsMockApiService();

      await tester.pumpWidget(
        ProviderScope(
          overrides: [
            apiServiceProvider.overrideWithValue(mockApi),
          ],
          child: MaterialApp(
            theme: EnergyMirrorTheme.darkTheme,
            home: const DiagnosticsScreen(),
          ),
        ),
      );

      await tester.pump();
      await tester.pump(const Duration(milliseconds: 100));

      // Assert that NO sensitive tokens, secrets, or internal paths are displayed anywhere
      expect(find.textContaining('bearer', findRichText: true), findsNothing);
      expect(find.textContaining('token', findRichText: true), findsNothing);
      expect(find.textContaining('secret', findRichText: true), findsNothing);
      expect(find.textContaining('password', findRichText: true), findsNothing);
      expect(find.textContaining('C:\\', findRichText: true), findsNothing);
      expect(find.textContaining('/Users/', findRichText: true), findsNothing);
    });

    testWidgets('Offline / Connection error displays warning and retry button', (WidgetTester tester) async {
      tester.view.physicalSize = const Size(1179, 2556);
      tester.view.devicePixelRatio = 3.0;
      addTearDown(() => tester.view.resetPhysicalSize());

      final mockApi = DiagnosticsMockApiService();
      mockApi.simulateError = true;

      await tester.pumpWidget(
        ProviderScope(
          overrides: [
            apiServiceProvider.overrideWithValue(mockApi),
          ],
          child: MaterialApp(
            theme: EnergyMirrorTheme.darkTheme,
            home: const DiagnosticsScreen(),
          ),
        ),
      );

      await tester.pump();
      await tester.pump(const Duration(milliseconds: 100));

      // Verify offline state
      expect(find.text('OFFLINE'), findsOneWidget);
      expect(find.text('Diagnostics check failed: Unable to connect to backend.'), findsOneWidget);

      // Tap refresh icon button to retry
      mockApi.simulateError = false;
      final refreshBtn = find.byIcon(Icons.refresh);
      expect(refreshBtn, findsOneWidget);

      await tester.tap(refreshBtn);
      await tester.pump();
      await tester.pump(const Duration(milliseconds: 100));

      // Successfully recovers
      expect(find.text('HEALTHY'), findsOneWidget);
    });
  });
}
