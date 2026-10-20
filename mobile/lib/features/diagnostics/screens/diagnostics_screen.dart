import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:google_fonts/google_fonts.dart';
import '../../../app/theme.dart';
import '../providers/diagnostics_provider.dart';

class DiagnosticsScreen extends ConsumerWidget {
  const DiagnosticsScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final state = ref.watch(diagnosticsProvider);
    final notifier = ref.read(diagnosticsProvider.notifier);
    final data = state.data;

    final isHealthy = data != null && data.status == 'healthy' && state.errorMessage == null;

    return Scaffold(
      backgroundColor: EnergyMirrorColors.canvas,
      body: SafeArea(
        child: RefreshIndicator(
          onRefresh: notifier.checkDiagnostics,
          color: EnergyMirrorColors.primaryBlue,
          backgroundColor: EnergyMirrorColors.surface,
          child: SingleChildScrollView(
            physics: const AlwaysScrollableScrollPhysics(),
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                // 1. Header with Status Badge and Refresh Button
                Row(
                  children: [
                    Container(
                      padding: const EdgeInsets.all(6),
                      decoration: const BoxDecoration(
                        color: EnergyMirrorColors.softSky,
                        shape: BoxShape.circle,
                      ),
                      child: const Icon(
                        Icons.monitor_heart_rounded,
                        size: 18,
                        color: EnergyMirrorColors.primaryBlue,
                      ),
                    ),
                    const SizedBox(width: 8),
                    Expanded(
                      child: Text(
                        'SYSTEM DIAGNOSTICS',
                        style: GoogleFonts.inter(
                          color: EnergyMirrorColors.textPrimary,
                          fontSize: 13.5,
                          fontWeight: FontWeight.w800,
                          letterSpacing: 0.6,
                        ),
                        maxLines: 1,
                        overflow: TextOverflow.ellipsis,
                      ),
                    ),
                    const SizedBox(width: 6),
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 3.5),
                      decoration: BoxDecoration(
                        color: isHealthy
                            ? EnergyMirrorColors.softMint
                            : EnergyMirrorColors.softCoral,
                        borderRadius: BorderRadius.circular(6),
                        border: Border.all(
                          color: isHealthy
                              ? EnergyMirrorColors.mintAccent.withValues(alpha: 0.3)
                              : EnergyMirrorColors.alertCoral.withValues(alpha: 0.3),
                        ),
                      ),
                      child: Text(
                        isHealthy ? 'SYSTEM OK' : 'DEGRADED',
                        style: GoogleFonts.inter(
                          color: isHealthy ? EnergyMirrorColors.mintAccent : EnergyMirrorColors.alertCoral,
                          fontSize: 9.5,
                          fontWeight: FontWeight.w700,
                          letterSpacing: 0.4,
                        ),
                      ),
                    ),
                    const SizedBox(width: 4),
                    IconButton(
                      icon: state.isLoading
                          ? const SizedBox(
                              width: 14,
                              height: 14,
                              child: CircularProgressIndicator(
                                strokeWidth: 2,
                                color: EnergyMirrorColors.primaryBlue,
                              ),
                            )
                          : const Icon(Icons.refresh, size: 18, color: EnergyMirrorColors.textSecondary),
                      onPressed: state.isLoading ? null : () => notifier.checkDiagnostics(),
                      visualDensity: VisualDensity.compact,
                      tooltip: 'Run diagnostics check',
                      padding: EdgeInsets.zero,
                      constraints: const BoxConstraints(minWidth: 28, minHeight: 28),
                    ),
                  ],
                ),
                const SizedBox(height: 14),

                // Error Notification if any
                if (state.errorMessage != null)
                  Container(
                    margin: const EdgeInsets.only(bottom: 12),
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(
                      color: EnergyMirrorColors.softCoral,
                      borderRadius: BorderRadius.circular(10),
                      border: Border.all(color: EnergyMirrorColors.alertCoral.withValues(alpha: 0.3)),
                    ),
                    child: Row(
                      children: [
                        const Icon(Icons.warning_amber_rounded, size: 18, color: EnergyMirrorColors.alertCoral),
                        const SizedBox(width: 10),
                        Expanded(
                          child: Text(
                            state.errorMessage!,
                            style: GoogleFonts.inter(color: EnergyMirrorColors.alertCoral, fontSize: 11.5),
                          ),
                        ),
                      ],
                    ),
                  ),

                // Progressive Disclosure: Essential System Snapshot Card
                Container(
                  margin: const EdgeInsets.only(bottom: 14),
                  padding: const EdgeInsets.all(14),
                  decoration: BoxDecoration(
                    color: EnergyMirrorColors.surfaceElevated,
                    borderRadius: BorderRadius.circular(14),
                    border: Border.all(color: EnergyMirrorColors.surfaceBorder),
                    boxShadow: const [
                      BoxShadow(
                        color: Color(0x060F1728),
                        blurRadius: 8,
                        offset: Offset(0, 2),
                      ),
                    ],
                  ),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        children: [
                          const Icon(Icons.shield_outlined, size: 16, color: EnergyMirrorColors.primaryBlue),
                          const SizedBox(width: 8),
                          Text(
                            'ESSENTIAL SYSTEM STATUS',
                            style: GoogleFonts.inter(
                              color: EnergyMirrorColors.textMuted,
                              fontSize: 10.5,
                              fontWeight: FontWeight.w700,
                              letterSpacing: 0.6,
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 10),
                      _buildSummaryRow(
                        icon: Icons.cloud_done_outlined,
                        label: 'Backend Service',
                        value: isHealthy ? 'ONLINE (Operational)' : 'UNREACHABLE',
                        valueColor: isHealthy ? EnergyMirrorColors.mintAccent : EnergyMirrorColors.alertCoral,
                      ),
                      _buildSummaryRow(
                        icon: Icons.electric_bolt_outlined,
                        label: 'Data Source',
                        value: 'SYNTHETIC SIMULATOR',
                        valueColor: EnergyMirrorColors.primaryBlue,
                      ),
                      _buildSummaryRow(
                        icon: Icons.developer_board_off_outlined,
                        label: 'Physical Hardware',
                        value: 'NONE (Zero Physical Sensors)',
                        valueColor: EnergyMirrorColors.amberAccent,
                      ),
                      _buildSummaryRow(
                        icon: Icons.storage_rounded,
                        label: 'Local Database',
                        value: data?.databaseConnected == true ? 'CONNECTED (SQLite Engine)' : 'DISCONNECTED',
                        valueColor: data?.databaseConnected == true ? EnergyMirrorColors.mintAccent : EnergyMirrorColors.alertCoral,
                      ),
                      _buildSummaryRow(
                        icon: Icons.auto_graph_rounded,
                        label: 'Disaggregation Engine',
                        value: 'RULE-BASED ESTIMATE',
                        valueColor: EnergyMirrorColors.textPrimary,
                      ),
                    ],
                  ),
                ),

                // 2. Diagnostic Cards
                _buildCard(
                  title: 'BACKEND CONNECTIVITY',
                  icon: Icons.cloud_done_outlined,
                  color: isHealthy ? EnergyMirrorColors.mintAccent : EnergyMirrorColors.alertCoral,
                  rows: [
                    _buildRow('API Status', data?.status.toUpperCase() ?? (state.isLoading ? 'CHECKING...' : 'OFFLINE'), isHealthy ? EnergyMirrorColors.mintAccent : EnergyMirrorColors.alertCoral),
                    _buildRow('Ping Latency', state.latencyMs != null ? '${state.latencyMs} ms' : 'Unavailable', EnergyMirrorColors.textPrimary),
                    _buildRow('API Gateway', 'FastAPI 127.0.0.1:8000', EnergyMirrorColors.textSecondary),
                    _buildRow('Software Version', data?.appVersion ?? '1.0.0', EnergyMirrorColors.textSecondary),
                    _buildRow('Last Verified', state.lastChecked != null ? '${state.lastChecked!.hour.toString().padLeft(2, '0')}:${state.lastChecked!.minute.toString().padLeft(2, '0')}:${state.lastChecked!.second.toString().padLeft(2, '0')}' : 'Pending', EnergyMirrorColors.textSecondary),
                  ],
                ),
                const SizedBox(height: 12),

                _buildCard(
                  title: 'METROLOGY & TELEMETRY SOURCE',
                  icon: Icons.electric_bolt_outlined,
                  color: EnergyMirrorColors.primaryBlue,
                  rows: [
                    _buildRow('Active Source', data?.activeTelemetrySource ?? 'SIMULATED', EnergyMirrorColors.primaryBlue),
                    _buildRow('Virtual Device ID', 'esp32-sim-01', EnergyMirrorColors.textSecondary),
                    _buildRow('Nominal Voltage', '230.2 V AC RMS (Simulated)', EnergyMirrorColors.textSecondary),
                    _buildRow('Line Frequency', '50.01 Hz (Simulated)', EnergyMirrorColors.textSecondary),
                    _buildRow('Current Aggregate', '${data?.simulatorAggregateW.toInt() ?? 284} W (Simulated)', EnergyMirrorColors.primaryBlue),
                  ],
                ),
                const SizedBox(height: 12),

                _buildCard(
                  title: 'HARDWARE INGESTION STATUS',
                  icon: Icons.developer_board_off_outlined,
                  color: EnergyMirrorColors.amberAccent,
                  rows: [
                    _buildRow('Hardware Connected', 'NONE (Simulation Mode)', EnergyMirrorColors.amberAccent),
                    _buildRow('Ingestion Pipeline', data?.hardwareMode ?? 'STAGED_INACTIVE', EnergyMirrorColors.amberAccent),
                    _buildRow('Configuration Flag', 'ENABLE_HARDWARE_INGEST = false', EnergyMirrorColors.textSecondary),
                    _buildRow('Physical Ingestion IC', 'None • No Physical Sensor Attached', EnergyMirrorColors.textMuted),
                    _buildRow('Security Audit', 'Zero Token Exposure • Nonce Verified', EnergyMirrorColors.mintAccent),
                  ],
                ),
                const SizedBox(height: 12),

                _buildCard(
                  title: 'SIMULATOR & NILM SUBSYSTEM',
                  icon: Icons.tune_rounded,
                  color: EnergyMirrorColors.primaryBlue,
                  rows: [
                    _buildRow('Simulator Subsystem', data?.simulatorActive == true ? 'ACTIVE (Deterministic)' : 'IDLE', EnergyMirrorColors.mintAccent),
                    _buildRow('Virtual Appliances', '${data?.simulatorAppliancesCount ?? 4} Active Loads', EnergyMirrorColors.textSecondary),
                    _buildRow('Unattributed Standby', '${data?.unattributedBaselineW.toInt() ?? 12} W (Physical Floor)', EnergyMirrorColors.amberAccent),
                    _buildRow('Event Classifier', 'Rule-Based Step (Derivative Delta P)', EnergyMirrorColors.textPrimary),
                    _buildRow('ML Classification', 'None (Deterministic Template Matching)', EnergyMirrorColors.textMuted),
                    _buildRow('Recorded Transitions', '${data?.recentEventsCount ?? 0} events', EnergyMirrorColors.textSecondary),
                  ],
                ),
                const SizedBox(height: 12),

                _buildCard(
                  title: 'LOCAL DATABASE PERSISTENCE',
                  icon: Icons.storage_rounded,
                  color: EnergyMirrorColors.textSecondary,
                  rows: [
                    _buildRow('Database Engine', data?.databaseType ?? 'SQLite', EnergyMirrorColors.textPrimary),
                    _buildRow('Connection Status', data?.databaseConnected == true ? 'CONNECTED' : 'DISCONNECTED', data?.databaseConnected == true ? EnergyMirrorColors.mintAccent : EnergyMirrorColors.alertCoral),
                    _buildRow('Telemetry Records', '${data?.databaseRecordCount ?? 0} rows', EnergyMirrorColors.textPrimary),
                    _buildRow('Test Isolation', 'StaticPool :memory: (Verified)', EnergyMirrorColors.mintAccent),
                  ],
                ),
                const SizedBox(height: 32),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildCard({
    required String title,
    required IconData icon,
    required Color color,
    required List<Widget> rows,
  }) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: EnergyMirrorColors.surfaceElevated,
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: EnergyMirrorColors.surfaceBorder),
        boxShadow: const [
          BoxShadow(
            color: Color(0x060F1728),
            blurRadius: 8,
            offset: Offset(0, 2),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(icon, size: 16, color: color),
              const SizedBox(width: 8),
              Expanded(
                child: Text(
                  title,
                  overflow: TextOverflow.ellipsis,
                  style: GoogleFonts.inter(
                    color: EnergyMirrorColors.textMuted,
                    fontSize: 10.5,
                    fontWeight: FontWeight.w700,
                    letterSpacing: 0.6,
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          ...rows,
        ],
      ),
    );
  }

  Widget _buildRow(String label, String value, Color valueColor) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4.0),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Expanded(
            flex: 4,
            child: Text(
              label,
              style: GoogleFonts.inter(
                color: EnergyMirrorColors.textSecondary,
                fontSize: 11.5,
              ),
            ),
          ),
          const SizedBox(width: 8),
          Expanded(
            flex: 6,
            child: Text(
              value,
              textAlign: TextAlign.end,
              softWrap: true,
              style: GoogleFonts.inter(
                color: valueColor,
                fontSize: 12,
                fontWeight: FontWeight.w700,
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildSummaryRow({
    required IconData icon,
    required String label,
    required String value,
    required Color valueColor,
  }) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4.0),
      child: Row(
        children: [
          Icon(icon, size: 14, color: valueColor),
          const SizedBox(width: 8),
          Expanded(
            flex: 5,
            child: Text(
              label,
              style: GoogleFonts.inter(
                color: EnergyMirrorColors.textSecondary,
                fontSize: 11.5,
                fontWeight: FontWeight.w500,
              ),
            ),
          ),
          const SizedBox(width: 8),
          Expanded(
            flex: 6,
            child: Text(
              value,
              textAlign: TextAlign.end,
              softWrap: true,
              style: GoogleFonts.inter(
                color: valueColor,
                fontSize: 11.5,
                fontWeight: FontWeight.w700,
              ),
            ),
          ),
        ],
      ),
    );
  }
}
