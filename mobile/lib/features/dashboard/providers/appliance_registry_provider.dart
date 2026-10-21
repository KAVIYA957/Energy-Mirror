import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/models/appliance_definition_model.dart';
import '../../../core/services/api_service.dart';
import 'dashboard_provider.dart';

class ApplianceRegistryState {
  final bool isLoading;
  final bool isMutating;
  final String? errorMessage;
  final String? successMessage;
  final List<ApplianceDefinition> appliances;

  ApplianceRegistryState({
    this.isLoading = false,
    this.isMutating = false,
    this.errorMessage,
    this.successMessage,
    this.appliances = const [],
  });

  ApplianceRegistryState copyWith({
    bool? isLoading,
    bool? isMutating,
    String? errorMessage,
    String? successMessage,
    List<ApplianceDefinition>? appliances,
  }) {
    return ApplianceRegistryState(
      isLoading: isLoading ?? this.isLoading,
      isMutating: isMutating ?? this.isMutating,
      errorMessage: errorMessage,
      successMessage: successMessage,
      appliances: appliances ?? this.appliances,
    );
  }
}

class ApplianceRegistryNotifier extends StateNotifier<ApplianceRegistryState> {
  final ApiService? apiService;
  final Ref? ref;

  ApplianceRegistryNotifier({
    this.apiService,
    this.ref,
    ApplianceRegistryState? initialState,
    bool autoLoad = true,
  }) : super(initialState ?? ApplianceRegistryState()) {
    if (autoLoad && apiService != null) {
      loadAppliances();
    }
  }

  Future<void> loadAppliances({bool? enabledOnly}) async {
    if (!mounted || apiService == null) return;
    state = state.copyWith(isLoading: true, errorMessage: null);
    try {
      final list = await apiService!.fetchAppliances(enabledOnly: enabledOnly);
      if (mounted) {
        state = state.copyWith(
          isLoading: false,
          appliances: list,
          errorMessage: null,
        );
      }
    } catch (e) {
      if (mounted) {
        state = state.copyWith(
          isLoading: false,
          errorMessage: 'Failed to load appliance registry: $e',
        );
      }
    }
  }

  Future<bool> registerAppliance(Map<String, dynamic> payload, {String? adminKey}) async {
    if (!mounted || apiService == null) return false;
    state = state.copyWith(isMutating: true, errorMessage: null, successMessage: null);
    try {
      final created = await apiService!.createAppliance(payload, adminKey: adminKey);
      if (mounted) {
        final updatedList = List<ApplianceDefinition>.from(state.appliances)..add(created);
        state = state.copyWith(
          isMutating: false,
          appliances: updatedList,
          successMessage: 'Appliance "${created.name}" registered successfully.',
        );
        // Resync dashboard and simulator
        ref?.read(dashboardProvider.notifier).refresh();
      }
      return true;
    } catch (e) {
      if (mounted) {
        state = state.copyWith(
          isMutating: false,
          errorMessage: e.toString().replaceFirst('Exception: ', ''),
        );
      }
      return false;
    }
  }

  Future<bool> updateAppliance(
    String applianceId,
    Map<String, dynamic> payload, {
    String? adminKey,
  }) async {
    if (!mounted || apiService == null) return false;
    state = state.copyWith(isMutating: true, errorMessage: null, successMessage: null);
    try {
      final updated = await apiService!.updateAppliance(applianceId, payload, adminKey: adminKey);
      if (mounted) {
        final updatedList = state.appliances.map((a) => a.applianceId == applianceId ? updated : a).toList();
        state = state.copyWith(
          isMutating: false,
          appliances: updatedList,
          successMessage: 'Appliance "${updated.name}" updated.',
        );
        ref?.read(dashboardProvider.notifier).refresh();
      }
      return true;
    } catch (e) {
      if (mounted) {
        state = state.copyWith(
          isMutating: false,
          errorMessage: e.toString().replaceFirst('Exception: ', ''),
        );
      }
      return false;
    }
  }

  Future<bool> deleteAppliance(String applianceId, {String? adminKey}) async {
    if (!mounted || apiService == null) return false;
    state = state.copyWith(isMutating: true, errorMessage: null, successMessage: null);
    try {
      await apiService!.deleteAppliance(applianceId, adminKey: adminKey);
      if (mounted) {
        final updatedList = state.appliances.where((a) => a.applianceId != applianceId).toList();
        state = state.copyWith(
          isMutating: false,
          appliances: updatedList,
          successMessage: 'Appliance "$applianceId" deleted successfully.',
        );
        ref?.read(dashboardProvider.notifier).refresh();
      }
      return true;
    } catch (e) {
      if (mounted) {
        state = state.copyWith(
          isMutating: false,
          errorMessage: e.toString().replaceFirst('Exception: ', ''),
        );
      }
      return false;
    }
  }

  void clearMessages() {
    if (mounted) {
      state = state.copyWith(errorMessage: null, successMessage: null);
    }
  }
}

final applianceRegistryProvider =
    StateNotifierProvider<ApplianceRegistryNotifier, ApplianceRegistryState>((ref) {
  final api = ref.watch(apiServiceProvider);
  return ApplianceRegistryNotifier(apiService: api, ref: ref);
});
