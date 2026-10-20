import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/models/telemetry_model.dart';
import '../../../core/services/api_service.dart';
import '../../dashboard/providers/dashboard_provider.dart';

class HistoryState {
  final int selectedIntervalMinutes;
  final bool isLoading;
  final String? errorMessage;
  final HistoryResponseData? historyData;
  final DateTime? lastFetched;

  HistoryState({
    this.selectedIntervalMinutes = 60,
    this.isLoading = true,
    this.errorMessage,
    this.historyData,
    this.lastFetched,
  });

  HistoryState copyWith({
    int? selectedIntervalMinutes,
    bool? isLoading,
    String? errorMessage,
    HistoryResponseData? historyData,
    DateTime? lastFetched,
  }) {
    return HistoryState(
      selectedIntervalMinutes: selectedIntervalMinutes ?? this.selectedIntervalMinutes,
      isLoading: isLoading ?? this.isLoading,
      errorMessage: errorMessage,
      historyData: historyData ?? this.historyData,
      lastFetched: lastFetched ?? this.lastFetched,
    );
  }
}

class HistoryNotifier extends StateNotifier<HistoryState> {
  final ApiService _apiService;

  HistoryNotifier(this._apiService) : super(HistoryState()) {
    fetchHistory();
  }

  Future<void> selectInterval(int minutes) async {
    if (state.selectedIntervalMinutes == minutes && !state.isLoading) return;
    state = state.copyWith(selectedIntervalMinutes: minutes, isLoading: true, errorMessage: null);
    await fetchHistory();
  }

  Future<void> fetchHistory() async {
    state = state.copyWith(isLoading: true, errorMessage: null);
    try {
      final res = await _apiService.fetchHistoryWithMetadata(minutes: state.selectedIntervalMinutes);
      if (mounted) {
        state = state.copyWith(
          isLoading: false,
          historyData: res,
          lastFetched: DateTime.now(),
          errorMessage: null,
        );
      }
    } catch (e) {
      if (mounted) {
        state = state.copyWith(
          isLoading: false,
          errorMessage: 'Failed to retrieve telemetry history: $e',
        );
      }
    }
  }
}

final historyProvider = StateNotifierProvider<HistoryNotifier, HistoryState>((ref) {
  final api = ref.watch(apiServiceProvider);
  final notifier = HistoryNotifier(api);

  // Automatically refresh history whenever dashboard pollCount increments or an appliance is toggled
  ref.listen<DashboardState>(dashboardProvider, (prev, next) {
    if (prev?.pollCount != next.pollCount ||
        prev?.simulatorState?.aggregatePowerW != next.simulatorState?.aggregatePowerW) {
      notifier.fetchHistory();
    }
  });

  return notifier;
});
