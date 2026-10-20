import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:mobile/core/models/telemetry_model.dart';
import 'package:mobile/core/services/api_service.dart';
import 'package:mobile/features/dashboard/providers/dashboard_provider.dart';
import 'package:mobile/features/history/screens/history_screen.dart';
import 'package:mobile/app/theme.dart';

class HistoryMockApiService extends ApiService {
  int lastRequestedMinutes = 60;
  List<int> recordedMinutesCalls = [];
  bool simulateError = false;
  bool returnEmpty = false;
  int? mockAvailableRangeMinutes = 60;

  @override
  Future<HistoryResponseData> fetchHistoryWithMetadata({int minutes = 60}) async {
    lastRequestedMinutes = minutes;
    recordedMinutesCalls.add(minutes);

    if (simulateError) {
      throw Exception('Simulated network error');
    }

    if (returnEmpty) {
      return HistoryResponseData(
        intervalMinutes: minutes,
        count: 0,
        points: [],
        availableRangeMinutes: 0,
        dataSource: 'SIMULATED',
        isSimulated: true,
      );
    }

    final now = DateTime.now();
    return HistoryResponseData(
      intervalMinutes: minutes,
      count: 3,
      points: [
        HistoryPoint(
          timestamp: now.subtract(const Duration(minutes: 50)),
          activePowerW: 100.0,
          dataSource: 'SIMULATED',
          applianceEvent: 'Water Pump ON',
        ),
        HistoryPoint(
          timestamp: now.subtract(const Duration(minutes: 25)),
          activePowerW: 300.0,
          dataSource: 'SIMULATED',
          applianceEvent: null,
        ),
        HistoryPoint(
          timestamp: now,
          activePowerW: 200.0,
          dataSource: 'SIMULATED',
          applianceEvent: null,
        ),
      ],
      availableRangeMinutes: mockAvailableRangeMinutes,
      dataSource: 'SIMULATED',
      isSimulated: true,
    );
  }
}

void main() {
  group('Historical Analytics & Truth-in-Reporting Tests', () {
    testWidgets('History screen renders interval pills, metrics, chart, and truth-in-reporting badge', (WidgetTester tester) async {
      tester.view.physicalSize = const Size(1179, 2556);
      tester.view.devicePixelRatio = 3.0;
      addTearDown(() => tester.view.resetPhysicalSize());

      final mockApi = HistoryMockApiService();

      await tester.pumpWidget(
        ProviderScope(
          overrides: [
            apiServiceProvider.overrideWithValue(mockApi),
          ],
          child: MaterialApp(
            theme: EnergyMirrorTheme.darkTheme,
            home: const HistoryScreen(),
          ),
        ),
      );

      await tester.pump();
      await tester.pump(const Duration(milliseconds: 100));

      // 1. Verify Header and SIMULATED DATA badge
      expect(find.text('ANALYTICS & HISTORY'), findsOneWidget);
      expect(find.text('SIMULATED DATA'), findsOneWidget);

      // 2. Verify all 4 interval pills exist
      expect(find.text('15m'), findsOneWidget);
      expect(find.text('1h'), findsOneWidget);
      expect(find.text('6h'), findsOneWidget);
      expect(find.text('24h'), findsOneWidget);

      // 3. Verify Metric Cards: Avg (200 W), Peak (300 W), Min (100 W)
      expect(find.text('200 W'), findsOneWidget); // Avg: (100 + 300 + 200) / 3 = 200
      expect(find.text('300 W'), findsOneWidget); // Peak: 300
      expect(find.text('100 W'), findsWidgets); // Min: 100 (also in transition list)

      // 4. Verify Chart Container and sample count
      expect(find.text('AGGREGATE ACTIVE POWER (W)'), findsOneWidget);
      expect(find.text('3 samples'), findsOneWidget);

      // 5. Verify Detected Transitions in Window
      expect(find.text('DETECTED LOAD TRANSITIONS IN WINDOW'), findsOneWidget);
      expect(find.text('Water Pump ON'), findsOneWidget);
    });

    testWidgets('Selecting intervals requests exact minute parameters from backend', (WidgetTester tester) async {
      tester.view.physicalSize = const Size(1179, 2556);
      tester.view.devicePixelRatio = 3.0;
      addTearDown(() => tester.view.resetPhysicalSize());

      final mockApi = HistoryMockApiService();

      await tester.pumpWidget(
        ProviderScope(
          overrides: [
            apiServiceProvider.overrideWithValue(mockApi),
          ],
          child: MaterialApp(
            theme: EnergyMirrorTheme.darkTheme,
            home: const HistoryScreen(),
          ),
        ),
      );

      await tester.pump();
      await tester.pump(const Duration(milliseconds: 100));

      // Initial default interval should be 60 min (1h)
      expect(mockApi.lastRequestedMinutes, 60);

      // Tap 15m
      await tester.tap(find.text('15m'));
      await tester.pump();
      await tester.pump(const Duration(milliseconds: 100));
      expect(mockApi.lastRequestedMinutes, 15);

      // Tap 6h
      await tester.tap(find.text('6h'));
      await tester.pump();
      await tester.pump(const Duration(milliseconds: 100));
      expect(mockApi.lastRequestedMinutes, 360);

      // Tap 24h
      await tester.tap(find.text('24h'));
      await tester.pump();
      await tester.pump(const Duration(milliseconds: 100));
      expect(mockApi.lastRequestedMinutes, 1440);

      // Verify all 4 interval requests were dispatched
      expect(mockApi.recordedMinutesCalls, containsAll([60, 15, 360, 1440]));
    });

    testWidgets('Honest available range banner displays when database span is less than interval', (WidgetTester tester) async {
      tester.view.physicalSize = const Size(1179, 2556);
      tester.view.devicePixelRatio = 3.0;
      addTearDown(() => tester.view.resetPhysicalSize());

      final mockApi = HistoryMockApiService();
      mockApi.mockAvailableRangeMinutes = 45; // 45m stored vs 60m requested

      await tester.pumpWidget(
        ProviderScope(
          overrides: [
            apiServiceProvider.overrideWithValue(mockApi),
          ],
          child: MaterialApp(
            theme: EnergyMirrorTheme.darkTheme,
            home: const HistoryScreen(),
          ),
        ),
      );

      await tester.pump();
      await tester.pump(const Duration(milliseconds: 100));

      // Verify honest banner text
      expect(find.textContaining('Showing available 45m of requested 1 Hour window (no artificial gap interpolation)'), findsOneWidget);
    });

    testWidgets('Empty history displays honest placeholder message', (WidgetTester tester) async {
      tester.view.physicalSize = const Size(1179, 2556);
      tester.view.devicePixelRatio = 3.0;
      addTearDown(() => tester.view.resetPhysicalSize());

      final mockApi = HistoryMockApiService();
      mockApi.returnEmpty = true;

      await tester.pumpWidget(
        ProviderScope(
          overrides: [
            apiServiceProvider.overrideWithValue(mockApi),
          ],
          child: MaterialApp(
            theme: EnergyMirrorTheme.darkTheme,
            home: const HistoryScreen(),
          ),
        ),
      );

      await tester.pump();
      await tester.pump(const Duration(milliseconds: 100));

      expect(find.text('No telemetry samples recorded in this window.'), findsOneWidget);
    });

    testWidgets('Error state displays error message and retry button', (WidgetTester tester) async {
      tester.view.physicalSize = const Size(1179, 2556);
      tester.view.devicePixelRatio = 3.0;
      addTearDown(() => tester.view.resetPhysicalSize());

      final mockApi = HistoryMockApiService();
      mockApi.simulateError = true;

      await tester.pumpWidget(
        ProviderScope(
          overrides: [
            apiServiceProvider.overrideWithValue(mockApi),
          ],
          child: MaterialApp(
            theme: EnergyMirrorTheme.darkTheme,
            home: const HistoryScreen(),
          ),
        ),
      );

      await tester.pump();
      await tester.pump(const Duration(milliseconds: 100));

      // Verify error banner and retry button
      expect(find.text('History Unavailable'), findsOneWidget);
      expect(find.text('Retry'), findsOneWidget);

      // Now resolve error and tap retry
      mockApi.simulateError = false;
      await tester.tap(find.text('Retry'));
      await tester.pump();
      await tester.pump(const Duration(milliseconds: 100));

      // Successfully loads after retry
      expect(find.text('200 W'), findsOneWidget);
    });
  });
}
