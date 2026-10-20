import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:google_fonts/google_fonts.dart';
import '../../../app/theme.dart';
import '../providers/dashboard_provider.dart';

class SimulatorSummaryCard extends ConsumerWidget {
  const SimulatorSummaryCard({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final state = ref.watch(dashboardProvider);
    final simState = state.simulatorState;
    final activeCount = simState?.appliances.where((a) => a.isOn).length ?? 4;
    final totalCount = simState?.appliances.length ?? 4;
    final aggW = simState?.aggregatePowerW ?? state.telemetry?.activePowerW ?? 284.0;
    final unattW = simState?.unattributedPowerW ?? 12.0;

    return Container(
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
              Container(
                padding: const EdgeInsets.all(6),
                decoration: const BoxDecoration(
                  color: EnergyMirrorColors.softSky,
                  shape: BoxShape.circle,
                ),
                child: const Icon(
                  Icons.tune_rounded,
                  size: 16,
                  color: EnergyMirrorColors.primaryBlue,
                ),
              ),
              const SizedBox(width: 8),
              Expanded(
                child: Text(
                  'SIMULATOR LAB',
                  style: GoogleFonts.inter(
                    color: EnergyMirrorColors.textPrimary,
                    fontSize: 12,
                    fontWeight: FontWeight.w800,
                    letterSpacing: 0.6,
                  ),
                  overflow: TextOverflow.ellipsis,
                ),
              ),
              const SizedBox(width: 6),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                decoration: BoxDecoration(
                  color: EnergyMirrorColors.softSky,
                  borderRadius: BorderRadius.circular(4),
                ),
                child: Text(
                  'SIMULATED TELEMETRY',
                  style: GoogleFonts.inter(
                    color: EnergyMirrorColors.primaryBlue,
                    fontSize: 8.5,
                    fontWeight: FontWeight.w700,
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 6),
          Row(
            children: [
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                decoration: BoxDecoration(
                  color: EnergyMirrorColors.softAmber,
                  borderRadius: BorderRadius.circular(4),
                ),
                child: Text(
                  'RULE-BASED ESTIMATE',
                  style: GoogleFonts.inter(
                    color: EnergyMirrorColors.amberAccent,
                    fontSize: 8.5,
                    fontWeight: FontWeight.w700,
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 10),
          Row(
            children: [
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      '$activeCount of $totalCount Virtual Appliances Active',
                      style: GoogleFonts.inter(
                        color: EnergyMirrorColors.textPrimary,
                        fontSize: 13,
                        fontWeight: FontWeight.w700,
                      ),
                    ),
                    const SizedBox(height: 2),
                    Text(
                      '${aggW.toInt()} W Simulated Load (${unattW.toInt()} W Baseline Residual)',
                      style: GoogleFonts.inter(
                        color: EnergyMirrorColors.textSecondary,
                        fontSize: 11,
                      ),
                    ),
                  ],
                ),
              ),
              ElevatedButton.icon(
                onPressed: () => context.go('/simulator'),
                icon: const Icon(Icons.arrow_forward_rounded, size: 14),
                label: const Text('Open Lab'),
                style: ElevatedButton.styleFrom(
                  backgroundColor: EnergyMirrorColors.primaryBlue,
                  foregroundColor: Colors.white,
                  elevation: 0,
                  padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
                  textStyle: GoogleFonts.inter(fontSize: 11.5, fontWeight: FontWeight.w700),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }
}
