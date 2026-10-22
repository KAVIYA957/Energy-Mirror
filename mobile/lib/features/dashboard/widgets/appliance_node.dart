import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import '../../../app/theme.dart';
import '../../../core/models/telemetry_model.dart';
import '../../../core/widgets/appliance_image.dart';

class ApplianceNode extends StatelessWidget {
  final ApplianceEstimate appliance;
  final double aggregatePowerW;
  final VoidCallback onTap;

  const ApplianceNode({
    super.key,
    required this.appliance,
    required this.aggregatePowerW,
    required this.onTap,
  });

  int get _nominalWattage {
    if (appliance.nominalPowerW != null && appliance.nominalPowerW! > 0) {
      return appliance.nominalPowerW!.round();
    }
    switch (appliance.applianceId) {
      case 'heater_01':
        return 140;
      case 'pump_01':
        return 75;
      case 'fan_01':
        return 45;
      case 'bulb_01':
        return 12;
      default:
        return appliance.estimatedPowerW.toInt();
    }
  }

  @override
  Widget build(BuildContext context) {
    final isOff = appliance.status == 'OFF' || appliance.estimatedPowerW <= 0;
    final powerW = appliance.estimatedPowerW.toInt();
    final pctOfTotal = aggregatePowerW > 0
        ? ((appliance.estimatedPowerW / aggregatePowerW) * 100.0).toStringAsFixed(1)
        : '0.0';

    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(14),
      child: Container(
        padding: const EdgeInsets.all(10),
        decoration: BoxDecoration(
          color: EnergyMirrorColors.surfaceElevated,
          borderRadius: BorderRadius.circular(14),
          border: Border.all(
            color: isOff ? EnergyMirrorColors.surfaceBorder : EnergyMirrorColors.primaryBlue.withValues(alpha: 0.3),
            width: isOff ? 1.0 : 1.5,
          ),
          boxShadow: const [
            BoxShadow(
              color: Color(0x080F1728),
              blurRadius: 8,
              offset: Offset(0, 2),
            ),
          ],
        ),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Top row: Appliance Image + Status Pill
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                ApplianceImage(
                  applianceId: appliance.applianceId,
                  size: 40,
                  isActive: !isOff,
                ),
                const SizedBox(width: 6),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 3),
                  decoration: BoxDecoration(
                    color: isOff ? EnergyMirrorColors.surfaceSubtle : EnergyMirrorColors.softMint,
                    borderRadius: BorderRadius.circular(6),
                    border: Border.all(
                      color: isOff ? EnergyMirrorColors.surfaceBorder : EnergyMirrorColors.mintAccent.withValues(alpha: 0.3),
                    ),
                  ),
                  child: Text(
                    isOff ? 'OFF' : 'ACTIVE',
                    style: GoogleFonts.inter(
                      color: isOff ? EnergyMirrorColors.textMuted : EnergyMirrorColors.mintAccent,
                      fontSize: 9,
                      fontWeight: FontWeight.w700,
                      letterSpacing: 0.4,
                    ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 10),
            // Appliance Name
            Text(
              appliance.name,
              style: GoogleFonts.inter(
                color: EnergyMirrorColors.textPrimary,
                fontSize: 13,
                fontWeight: FontWeight.w700,
              ),
              maxLines: 1,
              overflow: TextOverflow.ellipsis,
            ),
            const SizedBox(height: 2),
            // Power Reading & Nominal Rating
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Flexible(
                  child: Text(
                    isOff ? '0 W' : '$powerW W',
                    style: EnergyMirrorColors.tabularFigures(
                      color: isOff ? EnergyMirrorColors.textMuted : EnergyMirrorColors.primaryBlue,
                      fontSize: 14,
                      fontWeight: FontWeight.w800,
                    ),
                    overflow: TextOverflow.ellipsis,
                  ),
                ),
                Text(
                  '${_nominalWattage}W rated',
                  style: GoogleFonts.inter(
                    color: EnergyMirrorColors.textMuted,
                    fontSize: 9,
                    fontWeight: FontWeight.w600,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 6),
            // Indication that it's a rule-based estimate & % share
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 4, vertical: 2),
                  decoration: BoxDecoration(
                    color: appliance.detectionCapability == 'UNSUPPORTED'
                        ? EnergyMirrorColors.surfaceSubtle
                        : EnergyMirrorColors.softSky,
                    borderRadius: BorderRadius.circular(4),
                  ),
                  child: Text(
                    appliance.detectionCapability == 'UNSUPPORTED' ? 'SIMULATED' : 'RULE-BASED',
                    style: GoogleFonts.inter(
                      color: appliance.detectionCapability == 'UNSUPPORTED'
                          ? EnergyMirrorColors.textMuted
                          : EnergyMirrorColors.primaryBlue,
                      fontSize: 8,
                      fontWeight: FontWeight.w700,
                      letterSpacing: 0.3,
                    ),
                  ),
                ),
                if (!isOff)
                  Text(
                    '$pctOfTotal%',
                    style: GoogleFonts.inter(
                      color: EnergyMirrorColors.textSecondary,
                      fontSize: 9.5,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}
