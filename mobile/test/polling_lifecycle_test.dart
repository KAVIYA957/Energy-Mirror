import 'dart:async';
import 'package:flutter_test/flutter_test.dart';
import 'package:mobile/core/models/telemetry_model.dart';
import 'package:mobile/core/models/simulator_model.dart';
import 'package:mobile/core/services/api_service.dart';
import 'package:mobile/features/dashboard/providers/dashboard_provider.dart';

class CountingApiService extends ApiService {
  int fetchLiveCount = 0;
  int fetchDisaggCount = 0;
  int fetchHistoryCount = 0;
  int fetchSimulatorCount = 0;
  bool shouldFail = false;
  Completer<void>? stallCompleter;

  @override
  Future<TelemetryRecord> fetchLiveTelemetry() async {
    fetchLiveCount++;
    if (stallCompleter != null) {
      await stallCompleter!.future;
    }
    if (shouldFail) {
      throw Exception('Simulated network failure');
    }
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
      storyHeadline: 'Headline',
    );
  }

  @override
  Future<DisaggregationData> fetchLiveDisaggregation() async {
    fetchDisaggCount++;
    if (shouldFail) {
      throw Exception('Simulated network failure');
    }
    return DisaggregationData(
      timestamp: DateTime.now(),
      aggregatePowerW: 284.0,
      dataSource: 'SIMULATED',
      isSimulated: true,
      unattributedPowerW: 12.0,
      unattributedPercentage: 4.2,
      appliances: [],
    );
  }

  @override
  Future<List<HistoryPoint>> fetchHistory({int minutes = 60}) async {
    fetchHistoryCount++;
    if (shouldFail) {
      throw Exception('Simulated network failure');
    }
    return [];
  }

  @override
  Future<SimulatorState> fetchSimulatorState() async {
    fetchSimulatorCount++;
    if (shouldFail) {
      throw Exception('Simulated network failure');
    }
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
  group('Dashboard Auto-Refresh & Lifecycle Regression Tests', () {
    test('Automatic refresh runs at configured interval and increments poll count', () async {
      final mockApi = CountingApiService();
      // Configure short 40ms interval for fast deterministic unit testing
      final notifier = DashboardNotifier(
        mockApi,
        refreshInterval: const Duration(milliseconds: 40),
        autoStartPolling: true,
      );

      // Wait for initial load and 2 timer ticks (~120ms total)
      await Future<void>.delayed(const Duration(milliseconds: 120));
      expect(mockApi.fetchLiveCount, greaterThanOrEqualTo(2));
      expect(notifier.state.pollCount, greaterThanOrEqualTo(2));
      expect(notifier.state.isOffline, isFalse);
      expect(notifier.state.isStale, isFalse);

      notifier.dispose();
    });

    test('Polling stops when pausePolling() is called and resumes with resumePolling()', () async {
      final mockApi = CountingApiService();
      final notifier = DashboardNotifier(
        mockApi,
        refreshInterval: const Duration(milliseconds: 40),
        autoStartPolling: true,
      );

      await Future<void>.delayed(const Duration(milliseconds: 20));
      expect(mockApi.fetchLiveCount, 1);

      // Pause polling
      notifier.pausePolling();
      expect(notifier.state.isPollingPaused, isTrue);
      final countAtPause = mockApi.fetchLiveCount;

      // Wait 100ms: call count must NOT increase while paused
      await Future<void>.delayed(const Duration(milliseconds: 100));
      expect(mockApi.fetchLiveCount, countAtPause);

      // Resume polling
      notifier.resumePolling();
      expect(notifier.state.isPollingPaused, isFalse);

      // Wait 60ms: call count should now advance
      await Future<void>.delayed(const Duration(milliseconds: 60));
      expect(mockApi.fetchLiveCount, greaterThan(countAtPause));

      notifier.dispose();
    });

    test('Timer is cleanly cancelled when provider is disposed', () async {
      final mockApi = CountingApiService();
      final notifier = DashboardNotifier(
        mockApi,
        refreshInterval: const Duration(milliseconds: 40),
        autoStartPolling: true,
      );

      await Future<void>.delayed(const Duration(milliseconds: 20));
      expect(mockApi.fetchLiveCount, 1);

      // Dispose notifier
      notifier.dispose();
      final countAtDispose = mockApi.fetchLiveCount;

      // Wait 100ms: timer should not trigger on disposed notifier
      await Future<void>.delayed(const Duration(milliseconds: 100));
      expect(mockApi.fetchLiveCount, countAtDispose);
    });

    test('Overlapping requests are prevented when an API call is in flight', () async {
      final mockApi = CountingApiService();
      final completer = Completer<void>();

      final notifier = DashboardNotifier(
        mockApi,
        refreshInterval: const Duration(milliseconds: 50),
        autoStartPolling: false, // manual control
      );

      // Set stall completer on the mock API
      mockApi.stallCompleter = completer;

      // Start initial fetch (will stall on completer)
      final future1 = notifier.refresh();
      expect(mockApi.fetchLiveCount, 1);

      // Attempt second concurrent refresh while first is in-flight
      final future2 = notifier.refresh();
      // Second refresh should be dropped / prevented from overlapping
      expect(mockApi.fetchLiveCount, 1);

      // Release stall
      completer.complete();
      await future1;
      await future2;

      expect(mockApi.fetchLiveCount, 1);
      notifier.dispose();
    });

    test('Manual refresh resets polling timer and preserves existing data', () async {
      final mockApi = CountingApiService();
      final notifier = DashboardNotifier(
        mockApi,
        refreshInterval: const Duration(milliseconds: 100),
        autoStartPolling: true,
      );

      await Future<void>.delayed(const Duration(milliseconds: 20));
      expect(mockApi.fetchLiveCount, 1);

      // Manual refresh
      await notifier.refresh();
      expect(mockApi.fetchLiveCount, 2);
      expect(notifier.state.telemetry, isNotNull);
      expect(notifier.state.telemetry!.activePowerW, 284.0);

      notifier.dispose();
    });

    test('API failure during polling preserves cached data and sets isStale=true then self-heals', () async {
      final mockApi = CountingApiService();
      final notifier = DashboardNotifier(
        mockApi,
        refreshInterval: const Duration(milliseconds: 40),
        autoStartPolling: false,
      );

      // 1. Initial successful fetch
      await notifier.refresh();
      expect(notifier.state.isOffline, isFalse);
      expect(notifier.state.isStale, isFalse);
      expect(notifier.state.telemetry, isNotNull);

      // 2. Next poll fails (backend unreachable)
      mockApi.shouldFail = true;
      await notifier.refresh();

      // Should mark as STALE and OFFLINE but retain cached telemetry
      expect(notifier.state.isOffline, isTrue);
      expect(notifier.state.isStale, isTrue);
      expect(notifier.state.telemetry, isNotNull);
      expect(notifier.state.errorMessage, contains('Displaying cached data (Stale)'));

      // 3. Backend recovers on next poll
      mockApi.shouldFail = false;
      await notifier.refresh();

      // Self-heals back to healthy state
      expect(notifier.state.isOffline, isFalse);
      expect(notifier.state.isStale, isFalse);
      expect(notifier.state.errorMessage, isNull);

      notifier.dispose();
    });
  });
}
