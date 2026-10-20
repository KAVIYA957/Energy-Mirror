import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import '../../../app/theme.dart';

class UnattributedLoadBar extends StatelessWidget {
  final double aggregatePowerW;
  final double unattributedPowerW;
  final double unattributedPercentage;

  const UnattributedLoadBar({
    super.key,
    required this.aggregatePowerW,
    required this.unattributedPowerW,
    required this.unattributedPercentage,
  });

  @override
  Widget build(BuildContext context) {
    final residualPct = unattributedPercentage.clamp(0.0, 100.0);
    final applianceTotalW = (aggregatePowerW - unattributedPowerW).clamp(0.0, aggregatePowerW);
    final appliancePct = (100.0 - residualPct).clamp(0.0, 100.0);

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
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Expanded(
                child: Text(
                  'LOAD RECONCILIATION',
                  style: GoogleFonts.inter(
                    color: EnergyMirrorColors.textPrimary,
                    fontSize: 12,
                    fontWeight: FontWeight.w800,
                    letterSpacing: 0.6,
                  ),
                  overflow: TextOverflow.ellipsis,
                ),
              ),
              const SizedBox(width: 8),
              Text(
                'Total: ${aggregatePowerW.toInt()} W',
                style: GoogleFonts.inter(
                  color: EnergyMirrorColors.primaryBlue,
                  fontSize: 12,
                  fontWeight: FontWeight.w700,
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          // Dual Segmented Telemetry Bar
          ClipRRect(
            borderRadius: BorderRadius.circular(6),
            child: SizedBox(
              height: 10,
              child: Row(
                children: [
                  Expanded(
                    flex: (appliancePct * 10).toInt().clamp(1, 1000),
                    child: Container(
                      color: EnergyMirrorColors.mintAccent,
                    ),
                  ),
                  const SizedBox(width: 2),
                  Expanded(
                    flex: (residualPct * 10).toInt().clamp(1, 1000),
                    child: Container(
                      color: EnergyMirrorColors.amberAccent,
                    ),
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 12),
          // Two column metrics: Appliance estimates vs Residual with overflow protection
          Row(
            children: [
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Container(
                          width: 8,
                          height: 8,
                          decoration: const BoxDecoration(
                            color: EnergyMirrorColors.mintAccent,
                            shape: BoxShape.circle,
                          ),
                        ),
                        const SizedBox(width: 6),
                        Expanded(
                          child: Text(
                            'Attributed Load',
                            style: GoogleFonts.inter(
                              color: EnergyMirrorColors.textSecondary,
                              fontSize: 11,
                              fontWeight: FontWeight.w600,
                            ),
                            overflow: TextOverflow.ellipsis,
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 2),
                    Text(
                      '${applianceTotalW.toInt()} W (${appliancePct.toStringAsFixed(1)}%)',
                      style: GoogleFonts.inter(
                        color: EnergyMirrorColors.textPrimary,
                        fontSize: 14,
                        fontWeight: FontWeight.w800,
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(width: 8),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.end,
                  children: [
                    Row(
                      mainAxisAlignment: MainAxisAlignment.end,
                      children: [
                        Container(
                          width: 8,
                          height: 8,
                          decoration: const BoxDecoration(
                            color: EnergyMirrorColors.amberAccent,
                            shape: BoxShape.circle,
                          ),
                        ),
                        const SizedBox(width: 6),
                        Expanded(
                          child: Text(
                            'Unattributed Residual',
                            style: GoogleFonts.inter(
                              color: EnergyMirrorColors.textSecondary,
                              fontSize: 11,
                              fontWeight: FontWeight.w600,
                            ),
                            textAlign: TextAlign.end,
                            overflow: TextOverflow.ellipsis,
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 2),
                    Text(
                      '${unattributedPowerW.toInt()} W (${residualPct.toStringAsFixed(1)}%)',
                      style: GoogleFonts.inter(
                        color: EnergyMirrorColors.amberAccent,
                        fontSize: 14,
                        fontWeight: FontWeight.w800,
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
          const SizedBox(height: 10),
          const Divider(height: 1),
          const SizedBox(height: 8),
          Text(
            'Some of the total power is not assigned to the appliances shown. The simulation includes a fixed 12 W background baseline assumption.',
            style: GoogleFonts.inter(
              color: EnergyMirrorColors.textMuted,
              fontSize: 10.5,
              height: 1.4,
            ),
          ),
        ],
      ),
    );
  }
}
