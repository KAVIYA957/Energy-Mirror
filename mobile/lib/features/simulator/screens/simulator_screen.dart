import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:google_fonts/google_fonts.dart';
import '../../../app/theme.dart';
import '../../dashboard/providers/dashboard_provider.dart';
import '../../dashboard/widgets/simulator_lab_panel.dart';

class SimulatorScreen extends ConsumerWidget {
  const SimulatorScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final notifier = ref.read(dashboardProvider.notifier);

    return Scaffold(
      backgroundColor: EnergyMirrorColors.canvas,
      body: SafeArea(
        child: RefreshIndicator(
          onRefresh: notifier.refresh,
          color: EnergyMirrorColors.primaryBlue,
          backgroundColor: EnergyMirrorColors.surface,
          child: SingleChildScrollView(
            physics: const AlwaysScrollableScrollPhysics(),
            padding: const EdgeInsets.symmetric(vertical: 12),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                // Screen Title
                Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 16.0),
                  child: Row(
                    children: [
                      Container(
                        padding: const EdgeInsets.all(6),
                        decoration: const BoxDecoration(
                          color: EnergyMirrorColors.softSky,
                          shape: BoxShape.circle,
                        ),
                        child: const Icon(Icons.tune_rounded, size: 18, color: EnergyMirrorColors.primaryBlue),
                      ),
                      const SizedBox(width: 10),
                      Expanded(
                        child: Text(
                          'APPLIANCE SIMULATOR',
                          style: GoogleFonts.inter(
                            color: EnergyMirrorColors.textPrimary,
                            fontSize: 14,
                            fontWeight: FontWeight.w800,
                            letterSpacing: 0.8,
                          ),
                          maxLines: 1,
                          overflow: TextOverflow.ellipsis,
                        ),
                      ),
                      const SizedBox(width: 8),
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                        decoration: BoxDecoration(
                          color: EnergyMirrorColors.softSky,
                          borderRadius: BorderRadius.circular(6),
                        ),
                        child: Text(
                          'SIMULATION MODE',
                          style: GoogleFonts.inter(
                            color: EnergyMirrorColors.primaryBlue,
                            fontSize: 9.5,
                            fontWeight: FontWeight.w700,
                            letterSpacing: 0.4,
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 12),

                // Main Interactive Simulator Lab Panel
                const SimulatorLabPanel(),

                // Methodological Truth-in-Reporting Guidance Card
                Container(
                  margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
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
                          const Icon(Icons.verified_user_outlined, size: 18, color: EnergyMirrorColors.amberAccent),
                          const SizedBox(width: 8),
                          Expanded(
                            child: Text(
                              'METHODOLOGICAL ARCHITECTURE',
                              overflow: TextOverflow.ellipsis,
                              style: GoogleFonts.inter(
                                color: EnergyMirrorColors.textPrimary,
                                fontSize: 12,
                                fontWeight: FontWeight.w800,
                                letterSpacing: 0.6,
                              ),
                            ),
                          ),
                          const SizedBox(width: 8),
                          Container(
                            padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                            decoration: BoxDecoration(
                              color: EnergyMirrorColors.softAmber,
                              borderRadius: BorderRadius.circular(4),
                            ),
                            child: Text(
                              'RULE-BASED NILM',
                              style: GoogleFonts.inter(
                                color: EnergyMirrorColors.amberAccent,
                                fontSize: 9,
                                fontWeight: FontWeight.w700,
                              ),
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 12),
                      _buildBulletPoint(
                        'Controllable Telemetry: Generates deterministic appliance states (Water Heater 140W, Water Pump 75W, Ceiling Fan 45W, LED Bulb 12W) with a fixed 12W standby floor.',
                      ),
                      const SizedBox(height: 8),
                      _buildBulletPoint(
                        'Zero ML Fabrication: The event detector evaluates observed telemetry step transitions (Delta P). It has no access to internal simulator commands and uses validated threshold boundaries.',
                      ),
                      const SizedBox(height: 8),
                      _buildBulletPoint(
                        'Accounting Invariant: When all 4 appliances are OFF, aggregate power remains exactly 12 W (standby floor). Total power reconciles across all 16 ON/OFF combinations.',
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 24),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildBulletPoint(String text) {
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Container(
          margin: const EdgeInsets.only(top: 6),
          width: 5,
          height: 5,
          decoration: const BoxDecoration(
            color: EnergyMirrorColors.primaryBlue,
            shape: BoxShape.circle,
          ),
        ),
        const SizedBox(width: 8),
        Expanded(
          child: Text(
            text,
            style: GoogleFonts.inter(
              color: EnergyMirrorColors.textSecondary,
              fontSize: 11.5,
              height: 1.4,
            ),
          ),
        ),
      ],
    );
  }
}
