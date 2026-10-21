import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:google_fonts/google_fonts.dart';
import '../../../app/theme.dart';
import '../../../core/models/simulator_model.dart';
import '../../../core/widgets/appliance_image.dart';
import '../providers/dashboard_provider.dart';

class SimulatorLabPanel extends ConsumerWidget {
  const SimulatorLabPanel({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final state = ref.watch(dashboardProvider);
    final notifier = ref.read(dashboardProvider.notifier);
    final simState = state.simulatorState;

    // Fallback default virtual appliances if simulator state not yet loaded
    final appliances = simState?.appliances ?? [
      SimulatorAppliance(
        applianceId: 'heater_01',
        name: 'Water Heater',
        category: 'Heating',
        isOn: true,
        nominalPowerW: 140.0,
        currentPowerW: 140.0,
        status: 'RUNNING',
      ),
      SimulatorAppliance(
        applianceId: 'pump_01',
        name: 'Water Pump',
        category: 'Motor',
        isOn: true,
        nominalPowerW: 75.0,
        currentPowerW: 75.0,
        status: 'RUNNING',
      ),
      SimulatorAppliance(
        applianceId: 'fan_01',
        name: 'Ceiling Fan',
        category: 'Motor',
        isOn: true,
        nominalPowerW: 45.0,
        currentPowerW: 45.0,
        status: 'RUNNING',
      ),
      SimulatorAppliance(
        applianceId: 'bulb_01',
        name: 'LED Bulb',
        category: 'Lighting',
        isOn: true,
        nominalPowerW: 12.0,
        currentPowerW: 12.0,
        status: 'RUNNING',
      ),
    ];

    final aggregateW = simState?.aggregatePowerW ?? state.telemetry?.activePowerW ?? 284.0;
    final attributedW = simState?.attributedPowerW ?? 272.0;
    final unattributedW = simState?.unattributedPowerW ?? 12.0;
    final events = simState?.recentEvents ?? [];

    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: EnergyMirrorColors.surfaceElevated,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: EnergyMirrorColors.surfaceBorder, width: 1.2),
        boxShadow: const [
          BoxShadow(
            color: Color(0x080F1728),
            blurRadius: 10,
            offset: Offset(0, 3),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // 1. Header with Badges and Reset Button
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
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                ),
              ),
              const SizedBox(width: 4),
              // Explicit simulated badge
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 5, vertical: 2.5),
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
                    letterSpacing: 0.3,
                  ),
                ),
              ),
              const SizedBox(width: 6),
              // Reset baseline button
              IconButton(
                icon: state.isTogglingAppliance
                    ? const SizedBox(
                        width: 14,
                        height: 14,
                        child: CircularProgressIndicator(
                          strokeWidth: 2,
                          color: EnergyMirrorColors.amberAccent,
                        ),
                      )
                    : const Icon(Icons.restart_alt_rounded, size: 20, color: EnergyMirrorColors.amberAccent),
                tooltip: 'Reset to baseline (All ON, 284 W)',
                visualDensity: VisualDensity.compact,
                padding: EdgeInsets.zero,
                constraints: const BoxConstraints(minWidth: 32, minHeight: 32),
                onPressed: state.isTogglingAppliance ? null : () => notifier.resetSimulator(),
              ),
            ],
          ),
          const SizedBox(height: 12),

          // 2. Power Accounting Bar
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 10),
            decoration: BoxDecoration(
              color: EnergyMirrorColors.canvas,
              borderRadius: BorderRadius.circular(10),
              border: Border.all(color: EnergyMirrorColors.surfaceBorder),
            ),
            child: Row(
              children: [
                _buildAccountingItem(
                  label: 'AGGREGATE',
                  value: '${aggregateW.toInt()} W',
                  color: EnergyMirrorColors.primaryBlue,
                ),
                Container(width: 1, height: 24, color: EnergyMirrorColors.surfaceBorder),
                _buildAccountingItem(
                  label: 'ATTRIBUTED',
                  value: '${attributedW.toInt()} W',
                  color: EnergyMirrorColors.mintAccent,
                ),
                Container(width: 1, height: 24, color: EnergyMirrorColors.surfaceBorder),
                _buildAccountingItem(
                  label: 'STANDBY FLOOR',
                  value: '${unattributedW.toInt()} W',
                  color: EnergyMirrorColors.amberAccent,
                ),
              ],
            ),
          ),
          const SizedBox(height: 14),

          // 3. Virtual Appliance Controls with Asset Images
          Text(
            'TOGGLE VIRTUAL APPLIANCE LOADS',
            style: GoogleFonts.inter(
              color: EnergyMirrorColors.textMuted,
              fontSize: 10,
              fontWeight: FontWeight.w700,
              letterSpacing: 0.6,
            ),
          ),
          const SizedBox(height: 8),
          Column(
            children: appliances.map((app) {
              final isAppOn = app.isOn;
              return Container(
                margin: const EdgeInsets.only(bottom: 8),
                padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                decoration: BoxDecoration(
                  color: isAppOn ? Colors.white : EnergyMirrorColors.surfaceSubtle,
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(
                    color: isAppOn
                        ? EnergyMirrorColors.primaryBlue.withValues(alpha: 0.3)
                        : EnergyMirrorColors.surfaceBorder,
                    width: isAppOn ? 1.5 : 1.0,
                  ),
                ),
                child: Row(
                  children: [
                    ApplianceImage(
                      applianceId: app.applianceId,
                      size: 42,
                      isActive: isAppOn,
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            app.name,
                            style: GoogleFonts.inter(
                              color: isAppOn
                                  ? EnergyMirrorColors.textPrimary
                                  : EnergyMirrorColors.textSecondary,
                              fontSize: 13,
                              fontWeight: FontWeight.w700,
                            ),
                          ),
                          Row(
                            children: [
                              Flexible(
                                child: Text(
                                  '${app.category} • Nominal ${app.nominalPowerW.toInt()} W',
                                  style: GoogleFonts.inter(
                                    color: EnergyMirrorColors.textMuted,
                                    fontSize: 10.5,
                                  ),
                                  overflow: TextOverflow.ellipsis,
                                ),
                              ),
                              if (app.detectionCapability == 'UNSUPPORTED') ...[
                                const SizedBox(width: 4),
                                Container(
                                  padding: const EdgeInsets.symmetric(horizontal: 4, vertical: 1),
                                  decoration: BoxDecoration(
                                    color: EnergyMirrorColors.surfaceSubtle,
                                    borderRadius: BorderRadius.circular(3),
                                    border: Border.all(color: EnergyMirrorColors.surfaceBorder),
                                  ),
                                  child: Text(
                                    'UNMATCHED',
                                    style: GoogleFonts.inter(
                                      color: EnergyMirrorColors.textMuted,
                                      fontSize: 8,
                                      fontWeight: FontWeight.w600,
                                    ),
                                  ),
                                ),
                              ],
                            ],
                          ),
                        ],
                      ),
                    ),
                    Column(
                      crossAxisAlignment: CrossAxisAlignment.end,
                      children: [
                        Text(
                          isAppOn ? '${app.nominalPowerW.toInt()} W' : '0 W',
                          style: GoogleFonts.inter(
                            color: isAppOn ? EnergyMirrorColors.primaryBlue : EnergyMirrorColors.textMuted,
                            fontSize: 13,
                            fontWeight: FontWeight.w800,
                          ),
                        ),
                        Container(
                          padding: const EdgeInsets.symmetric(horizontal: 4, vertical: 1),
                          decoration: BoxDecoration(
                            color: isAppOn ? EnergyMirrorColors.softMint : EnergyMirrorColors.surfaceSubtle,
                            borderRadius: BorderRadius.circular(4),
                          ),
                          child: Text(
                            isAppOn ? 'ON' : 'OFF',
                            style: GoogleFonts.inter(
                              color: isAppOn ? EnergyMirrorColors.mintAccent : EnergyMirrorColors.textMuted,
                              fontSize: 9,
                              fontWeight: FontWeight.w700,
                            ),
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(width: 8),
                    Switch(
                      value: isAppOn,
                      activeThumbColor: Colors.white,
                      activeTrackColor: EnergyMirrorColors.primaryBlue,
                      inactiveThumbColor: EnergyMirrorColors.textMuted,
                      inactiveTrackColor: EnergyMirrorColors.surfaceBorder,
                      materialTapTargetSize: MaterialTapTargetSize.shrinkWrap,
                      onChanged: state.isTogglingAppliance
                          ? null
                          : (newVal) {
                              notifier.toggleAppliance(
                                app.applianceId,
                                targetState: newVal ? 'ON' : 'OFF',
                              );
                            },
                    ),
                  ],
                ),
              );
            }).toList(),
          ),
          const SizedBox(height: 10),

          // Prominent Reset Baseline Control
          SizedBox(
            width: double.infinity,
            child: OutlinedButton.icon(
              onPressed: state.isTogglingAppliance ? null : () => notifier.resetSimulator(),
              icon: const Icon(Icons.restore_rounded, size: 16),
              label: const Text('Reset All Loads to Baseline (284 W)'),
              style: OutlinedButton.styleFrom(
                foregroundColor: EnergyMirrorColors.amberAccent,
                side: BorderSide(color: EnergyMirrorColors.amberAccent.withValues(alpha: 0.4)),
                padding: const EdgeInsets.symmetric(vertical: 10),
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                textStyle: GoogleFonts.inter(fontSize: 12, fontWeight: FontWeight.w700),
              ),
            ),
          ),
          const SizedBox(height: 14),

          // 4. Rule-Based Edge Detector Events
          Row(
            children: [
              Expanded(
                child: Text(
                  'RECENT DETECTOR TRANSITIONS',
                  style: GoogleFonts.inter(
                    color: EnergyMirrorColors.textPrimary,
                    fontSize: 11,
                    fontWeight: FontWeight.w700,
                    letterSpacing: 0.5,
                  ),
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                ),
              ),
              const SizedBox(width: 6),
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
          const SizedBox(height: 8),
          if (events.isEmpty)
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: EnergyMirrorColors.surfaceSubtle,
                borderRadius: BorderRadius.circular(8),
                border: Border.all(color: EnergyMirrorColors.surfaceBorder),
              ),
              child: Center(
                child: Text(
                  'No transition events recorded in this session. Toggle an appliance above to observe detector output.',
                  style: GoogleFonts.inter(color: EnergyMirrorColors.textMuted, fontSize: 11),
                  textAlign: TextAlign.center,
                ),
              ),
            )
          else
            Column(
              children: events.take(3).map((ev) {
                final isMatched = ev.status == 'MATCHED';
                final isAmbiguous = ev.status == 'AMBIGUOUS';
                final badgeColor = isMatched
                    ? EnergyMirrorColors.mintAccent
                    : (isAmbiguous ? EnergyMirrorColors.amberAccent : EnergyMirrorColors.textMuted);
                final badgeBg = isMatched
                    ? EnergyMirrorColors.softMint
                    : (isAmbiguous ? EnergyMirrorColors.softAmber : EnergyMirrorColors.surfaceSubtle);

                return Container(
                  margin: const EdgeInsets.only(bottom: 6),
                  padding: const EdgeInsets.all(10),
                  decoration: BoxDecoration(
                    color: EnergyMirrorColors.surfaceSubtle,
                    borderRadius: BorderRadius.circular(8),
                    border: Border.all(color: EnergyMirrorColors.surfaceBorder),
                  ),
                  child: Row(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                        decoration: BoxDecoration(
                          color: badgeBg,
                          borderRadius: BorderRadius.circular(4),
                        ),
                        child: Text(
                          ev.status,
                          style: GoogleFonts.inter(
                            color: badgeColor,
                            fontSize: 9.5,
                            fontWeight: FontWeight.w700,
                          ),
                        ),
                      ),
                      const SizedBox(width: 8),
                      Expanded(
                        child: Text(
                          ev.ruleDescription,
                          style: GoogleFonts.inter(
                            color: EnergyMirrorColors.textSecondary,
                            fontSize: 11,
                            height: 1.3,
                          ),
                        ),
                      ),
                      const SizedBox(width: 8),
                      Text(
                        '${ev.deltaPowerW > 0 ? "+" : ""}${ev.deltaPowerW.toInt()} W',
                        style: GoogleFonts.inter(
                          color: ev.deltaPowerW > 0
                              ? EnergyMirrorColors.primaryBlue
                              : EnergyMirrorColors.alertCoral,
                          fontSize: 12,
                          fontWeight: FontWeight.w700,
                        ),
                      ),
                    ],
                  ),
                );
              }).toList(),
            ),
        ],
      ),
    );
  }

  Widget _buildAccountingItem({
    required String label,
    required String value,
    required Color color,
  }) {
    return Expanded(
      child: Column(
        children: [
          Text(
            label,
            style: GoogleFonts.inter(
              color: EnergyMirrorColors.textMuted,
              fontSize: 9,
              fontWeight: FontWeight.w600,
              letterSpacing: 0.3,
            ),
            textAlign: TextAlign.center,
            maxLines: 1,
            overflow: TextOverflow.ellipsis,
          ),
          const SizedBox(height: 2),
          Text(
            value,
            style: GoogleFonts.inter(
              color: color,
              fontSize: 14,
              fontWeight: FontWeight.w800,
            ),
          ),
        ],
      ),
    );
  }
}
