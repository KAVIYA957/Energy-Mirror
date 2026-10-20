import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/models/diagnostics_model.dart';
import '../../../core/services/api_service.dart';
import '../../dashboard/providers/dashboard_provider.dart';

class DiagnosticsState {
  final bool isLoading;
  final SystemDiagnosticsData? data;
  final String? errorMessage;
  final DateTime? lastChecked;
  final int? latencyMs;

  DiagnosticsState({
    this.isLoading = true,
    this.data,
    this.errorMessage,
    this.lastChecked,
    this.latencyMs,
  });

  DiagnosticsState copyWith({
    bool? isLoading,
    SystemDiagnosticsData? data,
    String? errorMessage,
    DateTime? lastChecked,
    int? latencyMs,
  }) {
    return DiagnosticsState(
      isLoading: isLoading ?? this.isLoading,
      data: data ?? this.data,
      errorMessage: errorMessage,
      lastChecked: lastChecked ?? this.lastChecked,
      latencyMs: latencyMs ?? this.latencyMs,
    );
  }
}

class DiagnosticsNotifier extends StateNotifier<DiagnosticsState> {
  final ApiService _apiService;

  DiagnosticsNotifier(this._apiService) : super(DiagnosticsState()) {
    checkDiagnostics();
  }

  Future<void> checkDiagnostics() async {
    state = state.copyWith(isLoading: true, errorMessage: null);
    final stopwatch = Stopwatch()..start();
    try {
      final res = await _apiService.fetchSystemDiagnostics();
      stopwatch.stop();
      if (mounted) {
        state = state.copyWith(
          isLoading: false,
          data: res,
          lastChecked: DateTime.now(),
          latencyMs: stopwatch.elapsedMilliseconds,
          errorMessage: null,
        );
      }
    } catch (e) {
      stopwatch.stop();
      if (mounted) {
        state = state.copyWith(
          isLoading: false,
          latencyMs: stopwatch.elapsedMilliseconds,
          errorMessage: 'Diagnostics check failed: Unable to connect to backend.',
        );
      }
    }
  }
}

final diagnosticsProvider = StateNotifierProvider<DiagnosticsNotifier, DiagnosticsState>((ref) {
  final api = ref.watch(apiServiceProvider);
  return DiagnosticsNotifier(api);
});
