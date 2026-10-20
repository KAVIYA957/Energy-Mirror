import 'dart:io' show Platform;
import 'package:flutter/foundation.dart';
import 'package:dio/dio.dart';
import '../models/telemetry_model.dart';
import '../models/simulator_model.dart';
import '../models/diagnostics_model.dart';

class ApiService {
  final Dio _dio;
  final String baseUrl;

  static String getDefaultBaseUrl() {
    const envUrl = String.fromEnvironment('API_URL');
    if (envUrl.isNotEmpty) {
      return envUrl;
    }
    if (kIsWeb) {
      final host = Uri.base.host.isNotEmpty ? Uri.base.host : '127.0.0.1';
      return 'http://$host:8000/api/v1';
    }
    try {
      if (Platform.isAndroid) {
        return 'http://10.0.2.2:8000/api/v1';
      }
    } catch (_) {}
    return 'http://127.0.0.1:8000/api/v1';
  }

  ApiService({String? baseUrl, Dio? dio})
      : baseUrl = baseUrl ?? getDefaultBaseUrl(),
        _dio = dio ??
            Dio(
              BaseOptions(
                baseUrl: baseUrl ?? getDefaultBaseUrl(),
                connectTimeout: const Duration(seconds: 4),
                receiveTimeout: const Duration(seconds: 4),
                headers: {
                  'Content-Type': 'application/json',
                  'Accept': 'application/json',
                },
              ),
            );

  Future<bool> checkHealth() async {
    try {
      final res = await _dio.get('/health');
      return res.statusCode == 200 && res.data['status'] == 'healthy';
    } catch (_) {
      return false;
    }
  }

  Future<TelemetryRecord> fetchLiveTelemetry() async {
    final response = await _dio.get('/telemetry/live');
    if (response.statusCode == 200) {
      return TelemetryRecord.fromJson(response.data as Map<String, dynamic>);
    }
    throw Exception('Failed to load live telemetry (status: ${response.statusCode})');
  }

  Future<DisaggregationData> fetchLiveDisaggregation() async {
    final response = await _dio.get('/nilm/live-disaggregation');
    if (response.statusCode == 200) {
      return DisaggregationData.fromJson(response.data as Map<String, dynamic>);
    }
    throw Exception('Failed to load disaggregation data (status: ${response.statusCode})');
  }

  Future<List<HistoryPoint>> fetchHistory({int minutes = 60}) async {
    final response = await _dio.get('/telemetry/history', queryParameters: {'minutes': minutes});
    if (response.statusCode == 200) {
      final data = response.data as Map<String, dynamic>;
      final rawList = data['points'] as List<dynamic>? ?? [];
      return rawList.map((pt) => HistoryPoint.fromJson(pt as Map<String, dynamic>)).toList();
    }
    throw Exception('Failed to load history (status: ${response.statusCode})');
  }

  Future<HistoryResponseData> fetchHistoryWithMetadata({int minutes = 60}) async {
    final response = await _dio.get('/telemetry/history', queryParameters: {'minutes': minutes});
    if (response.statusCode == 200) {
      return HistoryResponseData.fromJson(response.data as Map<String, dynamic>);
    }
    throw Exception('Failed to load history (status: ${response.statusCode})');
  }

  Future<List<PersistedEvent>> fetchPersistedEvents({int minutes = 60}) async {
    final response = await _dio.get('/telemetry/events', queryParameters: {'minutes': minutes});
    if (response.statusCode == 200) {
      final rawList = response.data as List<dynamic>? ?? [];
      return rawList.map((e) => PersistedEvent.fromJson(e as Map<String, dynamic>)).toList();
    }
    throw Exception('Failed to load persisted events (status: ${response.statusCode})');
  }


  Future<SimulatorState> fetchSimulatorState() async {
    final response = await _dio.get('/simulator/state');
    if (response.statusCode == 200) {
      return SimulatorState.fromJson(response.data as Map<String, dynamic>);
    }
    throw Exception('Failed to load simulator state (status: ${response.statusCode})');
  }

  Future<SimulatorState> toggleSimulatorAppliance(
    String applianceId, {
    String? targetState,
  }) async {
    final payload = <String, dynamic>{
      'appliance_id': applianceId,
    };
    if (targetState != null) {
      payload['target_state'] = targetState;
    }
    final response = await _dio.post('/simulator/toggle-appliance', data: payload);
    if (response.statusCode == 200) {
      final data = response.data as Map<String, dynamic>;
      final stateData = data['simulator_state'] as Map<String, dynamic>;
      return SimulatorState.fromJson(stateData);
    }
    throw Exception('Failed to toggle appliance $applianceId (status: ${response.statusCode})');
  }

  Future<SimulatorState> resetSimulator() async {
    final response = await _dio.post('/simulator/reset');
    if (response.statusCode == 200) {
      return SimulatorState.fromJson(response.data as Map<String, dynamic>);
    }
    throw Exception('Failed to reset simulator (status: ${response.statusCode})');
  }

  Future<SystemDiagnosticsData> fetchSystemDiagnostics() async {
    final response = await _dio.get('/diagnostics/system');
    if (response.statusCode == 200) {
      return SystemDiagnosticsData.fromJson(response.data as Map<String, dynamic>);
    }
    throw Exception('Failed to load system diagnostics (status: ${response.statusCode})');
  }
}
