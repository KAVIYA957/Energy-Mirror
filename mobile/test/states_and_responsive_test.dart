import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:mobile/core/models/telemetry_model.dart';
import 'package:mobile/core/models/simulator_model.dart';
import 'package:mobile/core/services/api_service.dart';
import 'package:mobile/features/dashboard/providers/dashboard_provider.dart';
import 'package:mobile/features/dashboard/screens/dashboard_screen.dart';
import 'package:mobile/app/theme.dart';

class FailingApiService extends ApiService {
  @override
  Future<TelemetryRecord> fetchLiveTelemetry() async {
    throw Exception('Connection refused');
  }

  @override
  Future<DisaggregationData> fetchLiveDisaggregation() async {
    throw Exception('Connection refused');
  }

  @override
  Future<List<HistoryPoint>> fetchHistory({int minutes = 60}) async {
    throw Exception('Connection refused');
  }

  @override
  Future<SimulatorState> fetchSimulatorState() async {
    throw Exception('Connection refused');
  }
}

void main() {
  group('Dashboard States & Responsive Viewports', () {
    testWidgets('Dashboard displays offline error banner when backend is unreachable', (WidgetTester tester) async {
      await tester.pumpWidget(
        ProviderScope(
          overrides: [
            apiServiceProvider.overrideWithValue(FailingApiService()),
          ],
          child: MaterialApp(
            theme: EnergyMirrorTheme.darkTheme,
            home: const DashboardScreen(),
          ),
        ),
      );

      await tester.pump();
      await tester.pump(const Duration(milliseconds: 100));

      // Offline badge and error banner
      expect(find.text('OFFLINE'), findsOneWidget);
      expect(find.textContaining('Cannot connect to backend'), findsOneWidget);
      expect(find.text('Retry'), findsOneWidget);
    });

    testWidgets('Dashboard renders on Tablet viewport (768 x 1024) without overflow', (WidgetTester tester) async {
      tester.view.physicalSize = const Size(768 * 2, 1024 * 2);
      tester.view.devicePixelRatio = 2.0;
      addTearDown(() => tester.view.resetPhysicalSize());

      await tester.pumpWidget(
        ProviderScope(
          overrides: [
            apiServiceProvider.overrideWithValue(FailingApiService()),
          ],
          child: MaterialApp(
            theme: EnergyMirrorTheme.darkTheme,
            home: const DashboardScreen(),
          ),
        ),
      );

      await tester.pump();
      expect(find.text('ENERGY MIRROR'), findsOneWidget);
    });

    testWidgets('Dashboard renders on Desktop viewport (1440 x 900) without overflow', (WidgetTester tester) async {
      tester.view.physicalSize = const Size(1440 * 1, 900 * 1);
      tester.view.devicePixelRatio = 1.0;
      addTearDown(() => tester.view.resetPhysicalSize());

      await tester.pumpWidget(
        ProviderScope(
          overrides: [
            apiServiceProvider.overrideWithValue(FailingApiService()),
          ],
          child: MaterialApp(
            theme: EnergyMirrorTheme.darkTheme,
            home: const DashboardScreen(),
          ),
        ),
      );

      await tester.pump();
      expect(find.text('ENERGY MIRROR'), findsOneWidget);
    });
  });
}
