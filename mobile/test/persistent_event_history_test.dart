import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:mobile/core/models/telemetry_model.dart';
import 'package:mobile/core/services/api_service.dart';
import 'package:mobile/features/dashboard/providers/dashboard_provider.dart';
import 'package:mobile/features/history/screens/history_screen.dart';
import 'package:mobile/app/theme.dart';

class PersistentEventMockApiService extends ApiService {
  bool simulateError = false;
  bool returnEmptyEvents = false;

  @override
  Future<HistoryResponseData> fetchHistoryWithMetadata({int minutes = 60}) async {
    if (simulateError) {
      throw Exception('Database connection failed');
    }

    final now = DateTime.now();

    final List<PersistedEvent> events = returnEmptyEvents
        ? []
        : [
            PersistedEvent(
              id: 1,
              timestamp: now.subtract(const Duration(minutes: 10)),
              status: 'MATCHED',
              applianceId: 'heater_01',
              applianceName: 'Water Heater',
              transitionType: 'OFF',
              deltaPowerW: -140.0,
              deltaPf: -0.09,
              ruleDescription: 'Rule-based match: Water Heater OFF (|Delta P| = 140.0 W)',
              dataClassification: 'RULE_BASED_ESTIMATE',
            ),
            PersistedEvent(
              id: 2,
              timestamp: now.subtract(const Duration(minutes: 5)),
              status: 'AMBIGUOUS',
              applianceId: null,
              applianceName: 'Ambiguous Overlap',
              transitionType: 'ON',
              deltaPowerW: 215.0,
              deltaPf: 0.14,
              ruleDescription: 'Ambiguous step of +215.0 W overlaps multiple signatures.',
              dataClassification: 'RULE_BASED_ESTIMATE',
            ),
          ];

    return HistoryResponseData(
      intervalMinutes: minutes,
      count: 2,
      points: [
        HistoryPoint(
          timestamp: now.subtract(const Duration(minutes: 10)),
          activePowerW: 144.0,
          dataSource: 'SIMULATED',
          applianceEvent: 'Water Heater OFF (-140 W)',
        ),
        HistoryPoint(
          timestamp: now,
          activePowerW: 359.0,
          dataSource: 'SIMULATED',
          applianceEvent: null,
        ),
      ],
      availableRangeMinutes: minutes,
      dataSource: 'SIMULATED',
      isSimulated: true,
      events: events,
    );
  }
}

void main() {
  group('Persistent Event History UI & Architecture Tests', () {
    testWidgets('Renders durable SQLite archive header, distinct disclaimer, and event items', (WidgetTester tester) async {
      tester.view.physicalSize = const Size(1179, 2556);
      tester.view.devicePixelRatio = 3.0;
      addTearDown(() => tester.view.resetPhysicalSize());

      final mockApi = PersistentEventMockApiService();

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

      // 1. Verify Archive Header and Distinct Notice
      expect(find.text('DURABLE EVENT ARCHIVE (SQLITE)'), findsOneWidget);
      expect(find.text('2 events'), findsOneWidget);
      expect(
        find.textContaining('survives server restarts (distinct from the transient simulator feed'),
        findsOneWidget,
      );

      // 2. Verify Matched Event Details
      expect(find.text('MATCHED'), findsOneWidget);
      expect(find.text('Water Heater'), findsOneWidget);
      expect(find.text('-140.0 W'), findsOneWidget);
      expect(find.text('OFF'), findsOneWidget);
      expect(find.text('ΔPF: -0.09'), findsOneWidget);
      expect(find.textContaining('Water Heater OFF (|Delta P| = 140.0 W)'), findsOneWidget);

      // 3. Verify Ambiguous Event Details
      expect(find.text('AMBIGUOUS'), findsOneWidget);
      expect(find.text('Ambiguous Overlap'), findsOneWidget);
      expect(find.text('+215.0 W'), findsOneWidget);
      expect(find.text('ON'), findsOneWidget);
      expect(find.text('ΔPF: +0.14'), findsOneWidget);
      expect(find.textContaining('Ambiguous step of +215.0 W'), findsOneWidget);
    });

    testWidgets('Renders empty state when no events exist in the selected window', (WidgetTester tester) async {
      tester.view.physicalSize = const Size(1179, 2556);
      tester.view.devicePixelRatio = 3.0;
      addTearDown(() => tester.view.resetPhysicalSize());

      final mockApi = PersistentEventMockApiService()..returnEmptyEvents = true;

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

      expect(find.text('DURABLE EVENT ARCHIVE (SQLITE)'), findsOneWidget);
      expect(find.text('0 events'), findsOneWidget);
      expect(find.text('No durable events recorded in this time window.'), findsOneWidget);
      expect(
        find.text('Toggle virtual appliances in Simulator Lab to record durable event transitions in SQLite.'),
        findsOneWidget,
      );
    });
  });
}
