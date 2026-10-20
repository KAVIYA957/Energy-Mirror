import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import '../../../app/theme.dart';

class EnergyStoryPanel extends StatelessWidget {
  final String? headline;
  final String? detail;

  const EnergyStoryPanel({
    super.key,
    this.headline,
    this.detail,
  });

  @override
  Widget build(BuildContext context) {
    if (headline == null && detail == null) {
      return const SizedBox.shrink();
    }

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
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            padding: const EdgeInsets.all(8),
            decoration: const BoxDecoration(
              color: EnergyMirrorColors.softSky,
              shape: BoxShape.circle,
            ),
            child: const Icon(
              Icons.auto_awesome,
              size: 18,
              color: EnergyMirrorColors.primaryBlue,
            ),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'EDITORIAL INSIGHT',
                  style: GoogleFonts.inter(
                    color: EnergyMirrorColors.primaryBlue,
                    fontSize: 10,
                    fontWeight: FontWeight.w800,
                    letterSpacing: 0.8,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  headline ?? 'Active Energy Telemetry',
                  style: GoogleFonts.inter(
                    color: EnergyMirrorColors.textPrimary,
                    fontSize: 13.5,
                    fontWeight: FontWeight.w700,
                  ),
                ),
                if (detail != null) ...[
                  const SizedBox(height: 4),
                  Text(
                    detail!,
                    style: GoogleFonts.inter(
                      color: EnergyMirrorColors.textSecondary,
                      fontSize: 12,
                      height: 1.4,
                    ),
                  ),
                ],
              ],
            ),
          ),
        ],
      ),
    );
  }
}
