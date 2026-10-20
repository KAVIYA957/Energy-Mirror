import 'dart:async';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/models/telemetry_model.dart';
import '../../../core/models/simulator_model.dart';
import '../../../core/services/api_service.dart';

final apiServiceProvider = Provider<ApiService>((ref) {
  return ApiService();
});

class DashboardState {
  final bool isLoading;
  final bool isOffline;
  final bool isStale;
  final bool isPollingPaused;
  final bool isTogglingAppliance;
  final int pollCount;
  final String? errorMessage;
  final TelemetryRecord? telemetry;
  final DisaggregationData? disaggregation;
  final SimulatorState? simulatorState;
  final List<HistoryPoint> history;
  final ApplianceEstimate? selectedAppliance;
  final DateTime? lastUpdated;

  DashboardState({
    this.isLoading = true,
    this.isOffline = false,
    this.isStale = false,
    this.isPollingPaused = false,
    this.isTogglingAppliance = false,
    this.pollCount = 0,
    this.errorMessage,
    this.telemetry,
    this.disaggregation,
    this.simulatorState,
    this.history = const [],
    this.selectedAppliance,
    this.lastUpdated,
  });

  DashboardState copyWith({
    bool? isLoading,
    bool? isOffline,
    bool? isStale,
    bool? isPollingPaused,
    bool? isTogglingAppliance,
    int? pollCount,
    String? errorMessage,
    TelemetryRecord? telemetry,
    DisaggregationData? disaggregation,
    SimulatorState? simulatorState,
    List<HistoryPoint>? history,
    ApplianceEstimate? selectedAppliance,
    DateTime? lastUpdated,
  }) {
    return DashboardState(
      isLoading: isLoading ?? this.isLoading,
      isOffline: isOffline ?? this.isOffline,
      isStale: isStale ?? this.isStale,
      isPollingPaused: isPollingPaused ?? this.isPollingPaused,
      isTogglingAppliance: isTogglingAppliance ?? this.isTogglingAppliance,
      pollCount: pollCount ?? this.pollCount,
      errorMessage: errorMessage,
      telemetry: telemetry ?? this.telemetry,
      disaggregation: disaggregation ?? this.disaggregation,
      simulatorState: simulatorState ?? this.simulatorState,
      history: history ?? this.history,
      selectedAppliance: selectedAppliance ?? this.selectedAppliance,
      lastUpdated: lastUpdated ?? this.lastUpdated,
    );
  }
}

class DashboardNotifier extends StateNotifier<DashboardState> {
  final ApiService _apiService;
  final Duration refreshInterval;
  Timer? _timer;
  bool _isFetching = false;

  DashboardNotifier(
    this._apiService, {
    this.refreshInterval = const Duration(seconds: 4),
    bool autoStartPolling = true,
  }) : super(DashboardState()) {
    if (autoStartPolling) {
      refresh();
      startPolling();
    }
  }

  void startPolling() {
    _timer?.cancel();
    _timer = Timer.periodic(refreshInterval, (_) {
      if (mounted && !state.isPollingPaused) {
        refresh(isAutoPoll: true);
      }
    });
    if (mounted && state.isPollingPaused) {
      state = state.copyWith(isPollingPaused: false);
    }
  }

  void pausePolling() {
    _timer?.cancel();
    _timer = null;
    if (mounted) {
      state = state.copyWith(isPollingPaused: true);
    }
  }

  void resumePolling() {
    startPolling();
  }

  Future<void> refresh({bool isAutoPoll = false}) async {
    // Guard: Prevent overlapping network requests
    if (_isFetching || !mounted) return;
    _isFetching = true;

    // Reset polling timer on manual refresh so it doesn't immediately fire another poll
    if (!isAutoPoll && _timer != null && mounted && !state.isPollingPaused) {
      startPolling();
    }

    // Only set full-screen isLoading if no data has been loaded yet and not auto-polling
    if (state.telemetry == null && !isAutoPoll && mounted) {
      state = state.copyWith(isLoading: true, errorMessage: null);
    }

    try {
      final telemetry = await _apiService.fetchLiveTelemetry();
      final disaggregation = await _apiService.fetchLiveDisaggregation();
      final history = await _apiService.fetchHistory(minutes: 60);
      SimulatorState? simulatorState;
      try {
        simulatorState = await _apiService.fetchSimulatorState();
      } catch (_) {}

      if (!mounted) return;

      state = state.copyWith(
        isLoading: false,
        isOffline: false,
        isStale: false,
        pollCount: state.pollCount + 1,
        telemetry: telemetry,
        disaggregation: disaggregation,
        simulatorState: simulatorState ?? state.simulatorState,
        history: history,
        lastUpdated: DateTime.now(),
        errorMessage: null,
      );
    } catch (e) {
      if (!mounted) return;

      // If we already have cached data, preserve it and mark as STALE
      if (state.telemetry != null) {
        state = state.copyWith(
          isLoading: false,
          isStale: true,
          isOffline: true,
          pollCount: state.pollCount + 1,
          errorMessage: 'Backend unreachable. Displaying cached data (Stale).',
        );
      } else {
        // Offline / Error state with fallback
        state = state.copyWith(
          isLoading: false,
          isOffline: true,
          pollCount: state.pollCount + 1,
          errorMessage: 'Cannot connect to backend (http://127.0.0.1:8000).',
        );
      }
    } finally {
      _isFetching = false;
    }
  }

  Future<void> toggleAppliance(String applianceId, {String? targetState}) async {
    if (state.isTogglingAppliance || !mounted) return;
    state = state.copyWith(isTogglingAppliance: true);
    try {
      final updatedState = await _apiService.toggleSimulatorAppliance(
        applianceId,
        targetState: targetState,
      );
      if (mounted) {
        state = state.copyWith(
          simulatorState: updatedState,
          isTogglingAppliance: false,
        );
      }
      // Immediate resync of live telemetry, disaggregation & history
      await refresh();
    } catch (e) {
      if (mounted) {
        state = state.copyWith(
          isTogglingAppliance: false,
          errorMessage: 'Failed to toggle appliance: $e',
        );
      }
    }
  }

  Future<void> resetSimulator() async {
    if (state.isTogglingAppliance || !mounted) return;
    state = state.copyWith(isTogglingAppliance: true);
    try {
      final resetState = await _apiService.resetSimulator();
      if (mounted) {
        state = state.copyWith(
          simulatorState: resetState,
          isTogglingAppliance: false,
        );
      }
      await refresh();
    } catch (e) {
      if (mounted) {
        state = state.copyWith(
          isTogglingAppliance: false,
          errorMessage: 'Failed to reset simulator: $e',
        );
      }
    }
  }

  void selectAppliance(ApplianceEstimate? appliance) {
    if (mounted) {
      state = state.copyWith(selectedAppliance: appliance);
    }
  }

  @override
  void dispose() {
    _timer?.cancel();
    _timer = null;
    super.dispose();
  }
}

final dashboardProvider = StateNotifierProvider<DashboardNotifier, DashboardState>((ref) {
  final api = ref.watch(apiServiceProvider);
  return DashboardNotifier(api);
});
