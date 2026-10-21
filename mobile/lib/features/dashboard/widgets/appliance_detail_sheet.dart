import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:google_fonts/google_fonts.dart';
import '../../../app/theme.dart';
import '../../../core/models/telemetry_model.dart';
import '../../../core/widgets/appliance_image.dart';

class ApplianceDetailSheet extends StatelessWidget {
  final ApplianceEstimate appliance;

  const ApplianceDetailSheet({super.key, required this.appliance});

  @override
  Widget build(BuildContext context) {
    final isOff = appliance.status == 'OFF' || appliance.estimatedPowerW <= 0;

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 16),
      decoration: const BoxDecoration(
        color: EnergyMirrorColors.surfaceElevated,
        borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
        border: Border(
          top: BorderSide(color: EnergyMirrorColors.surfaceBorder, width: 1.5),
        ),
      ),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Drag handle
          Center(
            child: Container(
              width: 40,
              height: 4,
              decoration: BoxDecoration(
                color: EnergyMirrorColors.surfaceBorder,
                borderRadius: BorderRadius.circular(2),
              ),
            ),
          ),
          const SizedBox(height: 16),
          // Header with Asset Image and Title
          Row(
            children: [
              ApplianceImage(
                applianceId: appliance.applianceId,
                size: 64,
                isActive: !isOff,
              ),
              const SizedBox(width: 14),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      appliance.name,
                      style: GoogleFonts.inter(
                        color: EnergyMirrorColors.textPrimary,
                        fontSize: 18,
                        fontWeight: FontWeight.w800,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Wrap(
                      spacing: 6,
                      runSpacing: 4,
                      children: [
                        Container(
                          padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                          decoration: BoxDecoration(
                            color: isOff ? EnergyMirrorColors.surfaceSubtle : EnergyMirrorColors.softMint,
                            borderRadius: BorderRadius.circular(4),
                          ),
                          child: Text(
                            isOff ? 'OFF / STANDBY' : 'ACTIVE',
                            style: GoogleFonts.inter(
                              color: isOff ? EnergyMirrorColors.textMuted : EnergyMirrorColors.mintAccent,
                              fontSize: 10,
                              fontWeight: FontWeight.w700,
                            ),
                          ),
                        ),
                        Container(
                          padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                          decoration: BoxDecoration(
                            color: appliance.detectionCapability == 'UNSUPPORTED'
                                ? EnergyMirrorColors.surfaceSubtle
                                : EnergyMirrorColors.softSky,
                            borderRadius: BorderRadius.circular(4),
                          ),
                          child: Text(
                            appliance.detectionCapability == 'UNSUPPORTED'
                                ? 'SIMULATED ONLY'
                                : 'RULE-BASED ESTIMATE',
                            style: GoogleFonts.inter(
                              color: appliance.detectionCapability == 'UNSUPPORTED'
                                  ? EnergyMirrorColors.textMuted
                                  : EnergyMirrorColors.primaryBlue,
                              fontSize: 9.5,
                              fontWeight: FontWeight.w700,
                            ),
                          ),
                        ),
                      ],
                    ),
                  ],
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          // Estimated Power Readout Card
          Container(
            padding: const EdgeInsets.all(14),
            decoration: BoxDecoration(
              color: EnergyMirrorColors.surfaceSubtle,
              borderRadius: BorderRadius.circular(12),
              border: Border.all(color: EnergyMirrorColors.surfaceBorder),
            ),
            child: Row(
              children: [
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'ESTIMATED REAL-TIME POWER',
                        style: GoogleFonts.inter(
                          color: EnergyMirrorColors.textMuted,
                          fontSize: 10,
                          fontWeight: FontWeight.w700,
                          letterSpacing: 0.5,
                        ),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        '${appliance.estimatedPowerW.toInt()} W',
                        style: GoogleFonts.inter(
                          color: isOff ? EnergyMirrorColors.textMuted : EnergyMirrorColors.primaryBlue,
                          fontSize: 24,
                          fontWeight: FontWeight.w800,
                        ),
                      ),
                    ],
                  ),
                ),
                Container(width: 1, height: 36, color: EnergyMirrorColors.surfaceBorder),
                const SizedBox(width: 16),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'OPERATING STATE',
                        style: GoogleFonts.inter(
                          color: EnergyMirrorColors.textMuted,
                          fontSize: 10,
                          fontWeight: FontWeight.w700,
                          letterSpacing: 0.5,
                        ),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        appliance.status,
                        style: GoogleFonts.inter(
                          color: EnergyMirrorColors.textPrimary,
                          fontSize: 16,
                          fontWeight: FontWeight.w700,
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 14),
          // Inference Evidence and Reasoning Details
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(12),
              border: Border.all(color: EnergyMirrorColors.surfaceBorder),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'INFERENCE EVIDENCE & REASONING',
                  style: GoogleFonts.inter(
                    color: EnergyMirrorColors.textMuted,
                    fontSize: 10,
                    fontWeight: FontWeight.w700,
                    letterSpacing: 0.5,
                  ),
                ),
                const SizedBox(height: 8),
                if (appliance.evidenceNotes != null && appliance.evidenceNotes!.isNotEmpty) ...[
                  Text(
                    appliance.evidenceNotes!,
                    style: GoogleFonts.inter(
                      color: EnergyMirrorColors.textPrimary,
                      fontSize: 12.5,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                  const SizedBox(height: 8),
                ],
                _buildRow('Appliance Identifier', appliance.applianceId),
                const SizedBox(height: 6),
                _buildRow('Category', appliance.category),
                const SizedBox(height: 6),
                _buildRow('Nominal Rating', appliance.nominalPowerW != null ? '${appliance.nominalPowerW!.toInt()} W' : 'Unrated'),
                const SizedBox(height: 6),
                _buildRow(
                  'Detection Capability',
                  appliance.detectionCapability == 'PRODUCTION_RULE_MATCHED'
                      ? 'PRODUCTION_RULE_MATCHED (Calibrated)'
                      : (appliance.detectionCapability == 'UNSUPPORTED'
                          ? 'UNSUPPORTED (Simulated Only)'
                          : 'EXPERIMENTAL_ONLY'),
                ),
                const SizedBox(height: 6),
                _buildRow(
                  'Detection Method',
                  appliance.detectionCapability == 'UNSUPPORTED'
                      ? 'Simulated Only (No Calibrated NILM Envelope)'
                      : 'Rule-Based Step Classifier',
                ),
                const SizedBox(height: 6),
                _buildRow('Telemetry Source', 'Simulated Virtual Environment'),
                const SizedBox(height: 6),
                _buildRow('Sub-Meter Hardware', 'None (Calculated from Aggregate)'),
              ],
            ),
          ),
          const SizedBox(height: 16),
          // Action button to Simulator and Close button
          Row(
            children: [
              Expanded(
                child: ElevatedButton.icon(
                  onPressed: () {
                    Navigator.of(context).pop();
                    context.go('/simulator');
                  },
                  icon: const Icon(Icons.tune_rounded, size: 16),
                  label: const Text('Simulator Lab'),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: EnergyMirrorColors.primaryBlue,
                    foregroundColor: Colors.white,
                    padding: const EdgeInsets.symmetric(vertical: 12),
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                    textStyle: GoogleFonts.inter(fontSize: 13, fontWeight: FontWeight.w700),
                  ),
                ),
              ),
              const SizedBox(width: 8),
              TextButton(
                onPressed: () => Navigator.of(context).pop(),
                style: TextButton.styleFrom(
                  foregroundColor: EnergyMirrorColors.textSecondary,
                  padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
                ),
                child: const Text('Close'),
              ),
            ],
          ),
          const SizedBox(height: 12),
        ],
      ),
    );
  }

  Widget _buildRow(String label, String value) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Expanded(
          flex: 2,
          child: Text(
            label,
            style: GoogleFonts.inter(color: EnergyMirrorColors.textSecondary, fontSize: 11.5),
            overflow: TextOverflow.ellipsis,
          ),
        ),
        const SizedBox(width: 8),
        Expanded(
          flex: 3,
          child: Text(
            value,
            textAlign: TextAlign.end,
            style: GoogleFonts.inter(
              color: EnergyMirrorColors.textPrimary,
              fontSize: 11.5,
              fontWeight: FontWeight.w600,
            ),
            overflow: TextOverflow.ellipsis,
          ),
        ),
      ],
    );
  }
}
