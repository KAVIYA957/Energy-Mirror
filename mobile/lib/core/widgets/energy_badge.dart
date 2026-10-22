import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import '../../app/theme.dart';

enum EnergyBadgeType {
  simulated,
  liveHardware,
  ruleBased,
  unsupported,
  offline,
  stale,
  sqlite,
  stagedInactive,
}

/// Truth-in-reporting badge widget ensuring transparent, high-contrast,
/// accessible status communication across all Energy Mirror screens.
class EnergyBadge extends StatelessWidget {
  final EnergyBadgeType type;
  final String? customLabel;
  final String? tooltip;
  final double fontSize;
  final EdgeInsetsGeometry padding;

  const EnergyBadge({
    super.key,
    required this.type,
    this.customLabel,
    this.tooltip,
    this.fontSize = 10.0,
    this.padding = const EdgeInsets.symmetric(horizontal: 7.0, vertical: 3.5),
  });

  factory EnergyBadge.simulated({String? tooltip}) => EnergyBadge(
        type: EnergyBadgeType.simulated,
        tooltip: tooltip ?? 'Calibrated mathematical simulation running at 1 Hz',
      );

  factory EnergyBadge.ruleBased({String? tooltip}) => EnergyBadge(
        type: EnergyBadgeType.ruleBased,
        tooltip: tooltip ?? 'Estimated via deterministic active power and power factor step rules',
      );

  factory EnergyBadge.unsupported({String? tooltip}) => EnergyBadge(
        type: EnergyBadgeType.unsupported,
        tooltip: tooltip ?? 'Load profile uncalibrated in active rule dictionary',
      );

  factory EnergyBadge.sqlite({String? tooltip}) => EnergyBadge(
        type: EnergyBadgeType.sqlite,
        tooltip: tooltip ?? 'Durable local SQLite database active (energy_mirror.db)',
      );

  factory EnergyBadge.stagedInactive({String? tooltip}) => EnergyBadge(
        type: EnergyBadgeType.stagedInactive,
        tooltip: tooltip ?? 'Hardware ingestion endpoint staged inactive (ENABLE_HARDWARE_INGEST=false)',
      );

  @override
  Widget build(BuildContext context) {
    Color bg;
    Color fg;
    Color border;
    IconData icon;
    String label;

    switch (type) {
      case EnergyBadgeType.simulated:
        bg = EnergyMirrorColors.softAmber;
        fg = EnergyMirrorColors.amberAccent;
        border = EnergyMirrorColors.amberAccent.withValues(alpha: 0.35);
        icon = Icons.biotech_rounded;
        label = customLabel ?? 'SIMULATED DATA';
        break;
      case EnergyBadgeType.liveHardware:
        bg = EnergyMirrorColors.softMint;
        fg = EnergyMirrorColors.mintAccent;
        border = EnergyMirrorColors.mintAccent.withValues(alpha: 0.35);
        icon = Icons.sensors_rounded;
        label = customLabel ?? 'LIVE HARDWARE';
        break;
      case EnergyBadgeType.ruleBased:
        bg = EnergyMirrorColors.softSky;
        fg = EnergyMirrorColors.primaryBlue;
        border = EnergyMirrorColors.primaryBlue.withValues(alpha: 0.35);
        icon = Icons.rule_rounded;
        label = customLabel ?? 'RULE-BASED';
        break;
      case EnergyBadgeType.unsupported:
        bg = EnergyMirrorColors.surfaceSubtle;
        fg = EnergyMirrorColors.textMuted;
        border = EnergyMirrorColors.surfaceBorder;
        icon = Icons.help_outline_rounded;
        label = customLabel ?? 'UNSUPPORTED';
        break;
      case EnergyBadgeType.offline:
        bg = EnergyMirrorColors.softCoral;
        fg = EnergyMirrorColors.alertCoral;
        border = EnergyMirrorColors.alertCoral.withValues(alpha: 0.35);
        icon = Icons.cloud_off_rounded;
        label = customLabel ?? 'OFFLINE';
        break;
      case EnergyBadgeType.stale:
        bg = EnergyMirrorColors.softAmber;
        fg = EnergyMirrorColors.amberAccent;
        border = EnergyMirrorColors.amberAccent.withValues(alpha: 0.35);
        icon = Icons.history_rounded;
        label = customLabel ?? 'STALE DATA';
        break;
      case EnergyBadgeType.sqlite:
        bg = EnergyMirrorColors.surfaceSubtle;
        fg = EnergyMirrorColors.textPrimary;
        border = EnergyMirrorColors.surfaceBorder;
        icon = Icons.storage_rounded;
        label = customLabel ?? 'SQLite';
        break;
      case EnergyBadgeType.stagedInactive:
        bg = EnergyMirrorColors.surfaceSubtle;
        fg = EnergyMirrorColors.textSecondary;
        border = EnergyMirrorColors.surfaceBorder;
        icon = Icons.toggle_off_rounded;
        label = customLabel ?? 'STAGED_INACTIVE';
        break;
    }

    final badge = Container(
      padding: padding,
      decoration: BoxDecoration(
        color: bg,
        borderRadius: BorderRadius.circular(6.0),
        border: Border.all(color: border, width: 1.0),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, size: fontSize + 2.5, color: fg),
          const SizedBox(width: 4.5),
          Text(
            label,
            style: GoogleFonts.inter(
              color: fg,
              fontSize: fontSize,
              fontWeight: FontWeight.w700,
              letterSpacing: 0.4,
            ),
          ),
        ],
      ),
    );

    if (tooltip != null && tooltip!.isNotEmpty) {
      return Tooltip(
        message: tooltip!,
        child: badge,
      );
    }
    return badge;
  }
}
