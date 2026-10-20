import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:google_fonts/google_fonts.dart';
import '../../../app/theme.dart';
import '../providers/dashboard_provider.dart';
import '../widgets/energy_mirror_header.dart';
import '../widgets/energy_pulse_widget.dart';
import '../widgets/appliance_constellation.dart';
import '../widgets/unattributed_load_bar.dart';
import '../widgets/energy_story_panel.dart';
import '../widgets/power_timeline_chart.dart';
import '../widgets/simulator_summary_card.dart';

class DashboardScreen extends ConsumerStatefulWidget {
  const DashboardScreen({super.key});

  @override
  ConsumerState<DashboardScreen> createState() => _DashboardScreenState();
}

class _DashboardScreenState extends ConsumerState<DashboardScreen> with WidgetsBindingObserver {
  bool _showOnboardingBanner = true;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addObserver(this);
  }

  @override
  void dispose() {
    WidgetsBinding.instance.removeObserver(this);
    super.dispose();
  }

  @override
  void didChangeAppLifecycleState(AppLifecycleState lifecycleState) {
    final notifier = ref.read(dashboardProvider.notifier);
    if (lifecycleState == AppLifecycleState.resumed) {
      notifier.resumePolling();
    } else if (lifecycleState == AppLifecycleState.paused ||
               lifecycleState == AppLifecycleState.inactive ||
               lifecycleState == AppLifecycleState.hidden) {
      notifier.pausePolling();
    }
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(dashboardProvider);
    final notifier = ref.read(dashboardProvider.notifier);

    // Determine status badge color and text
    String statusText = 'SIMULATED DATA';
    Color statusColor = EnergyMirrorColors.amberAccent;

    if (state.isOffline && state.telemetry == null) {
      statusText = 'OFFLINE';
      statusColor = EnergyMirrorColors.alertCoral;
    } else if (state.isStale) {
      statusText = 'STALE DATA';
      statusColor = EnergyMirrorColors.amberAccent;
    } else if (state.telemetry != null && !state.telemetry!.isSimulated) {
      statusText = 'LIVE HARDWARE';
      statusColor = EnergyMirrorColors.mintAccent;
    }

    if (state.isLoading && state.telemetry == null) {
      return Scaffold(
        backgroundColor: EnergyMirrorColors.canvas,
        body: Center(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              const CircularProgressIndicator(
                color: EnergyMirrorColors.primaryBlue,
                strokeWidth: 2.5,
              ),
              const SizedBox(height: 16),
              Text(
                'Connecting to Energy Mirror...',
                style: GoogleFonts.inter(
                  color: EnergyMirrorColors.textSecondary,
                  fontSize: 13,
                  fontWeight: FontWeight.w500,
                ),
              ),
            ],
          ),
        ),
      );
    }

    final activePower = state.telemetry?.activePowerW ?? 284.0;
    final appliances = state.disaggregation?.appliances ?? [];
    final unattributedPower = state.disaggregation?.unattributedPowerW ?? 12.0;
    final unattributedPct = state.disaggregation?.unattributedPercentage ?? 4.2;
    final headline = state.disaggregation?.storyHeadline ?? state.telemetry?.storyHeadline;
    final detail = state.disaggregation?.storyDetail;

    return Scaffold(
      backgroundColor: EnergyMirrorColors.canvas,
      body: SafeArea(
        child: RefreshIndicator(
          onRefresh: notifier.refresh,
          color: EnergyMirrorColors.primaryBlue,
          backgroundColor: EnergyMirrorColors.surface,
          child: SingleChildScrollView(
            physics: const AlwaysScrollableScrollPhysics(),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                // 1. Top Header with Status Pill and Micro-Legend
                EnergyMirrorHeader(
                  statusText: statusText,
                  statusColor: statusColor,
                  onRefresh: notifier.refresh,
                ),

                // Error / Stale / Offline Notification Banner
                if (state.errorMessage != null)
                  Container(
                    margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                    padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
                    decoration: BoxDecoration(
                      color: EnergyMirrorColors.softCoral,
                      border: Border.all(color: EnergyMirrorColors.alertCoral.withValues(alpha: 0.3)),
                      borderRadius: BorderRadius.circular(10),
                    ),
                    child: Row(
                      children: [
                        const Icon(Icons.info_outline, size: 16, color: EnergyMirrorColors.alertCoral),
                        const SizedBox(width: 8),
                        Expanded(
                          child: Text(
                            state.errorMessage!,
                            style: GoogleFonts.inter(
                              color: EnergyMirrorColors.alertCoral,
                              fontSize: 11,
                              fontWeight: FontWeight.w500,
                            ),
                          ),
                        ),
                        TextButton(
                          onPressed: notifier.refresh,
                          style: TextButton.styleFrom(
                            padding: EdgeInsets.zero,
                            minimumSize: const Size(40, 24),
                          ),
                          child: Text(
                            'Retry',
                            style: GoogleFonts.inter(color: EnergyMirrorColors.textPrimary, fontSize: 11, fontWeight: FontWeight.w700),
                          ),
                        ),
                      ],
                    ),
                  ),

                // Lightweight First-Use Onboarding Card
                if (_showOnboardingBanner)
                  Container(
                    margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                    padding: const EdgeInsets.all(14),
                    decoration: BoxDecoration(
                      color: EnergyMirrorColors.softSky,
                      borderRadius: BorderRadius.circular(12),
                      border: Border.all(color: EnergyMirrorColors.primaryBlue.withValues(alpha: 0.2)),
                    ),
                    child: Row(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Container(
                          padding: const EdgeInsets.all(6),
                          decoration: const BoxDecoration(
                            color: Colors.white,
                            shape: BoxShape.circle,
                          ),
                          child: const Icon(
                            Icons.lightbulb_outline,
                            size: 16,
                            color: EnergyMirrorColors.primaryBlue,
                          ),
                        ),
                        const SizedBox(width: 10),
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                'How Energy Mirror Works',
                                style: GoogleFonts.inter(
                                  color: EnergyMirrorColors.primaryBlue,
                                  fontSize: 12,
                                  fontWeight: FontWeight.w700,
                                ),
                              ),
                              const SizedBox(height: 2),
                              Text(
                                'Energy Mirror estimates appliance activity from whole-home power without individual smart plugs. Test what-if load toggles in Simulator Lab.',
                                style: GoogleFonts.inter(
                                  color: EnergyMirrorColors.textSecondary,
                                  fontSize: 11,
                                  height: 1.35,
                                ),
                              ),
                            ],
                          ),
                        ),
                        IconButton(
                          icon: const Icon(Icons.close, size: 16, color: EnergyMirrorColors.textMuted),
                          onPressed: () => setState(() => _showOnboardingBanner = false),
                          padding: EdgeInsets.zero,
                          constraints: const BoxConstraints(),
                          tooltip: 'Dismiss guide',
                        ),
                      ],
                    ),
                  ),

                const SizedBox(height: 8),

                // 2. Hero: The Luminous Energy Pulse Field
                Center(
                  child: EnergyPulseWidget(
                    activePowerW: activePower,
                    isSimulated: state.telemetry?.isSimulated ?? true,
                    isStale: state.isStale,
                    size: MediaQuery.of(context).size.width < 420 ? 195.0 : 235.0,
                  ),
                ),

                const SizedBox(height: 8),

                // 3. Secondary: Appliance Breakdown with Asset Visuals
                ApplianceConstellation(
                  appliances: appliances,
                  aggregatePowerW: activePower,
                ),

                // 4. Unattributed Load Reconciler
                UnattributedLoadBar(
                  aggregatePowerW: activePower,
                  unattributedPowerW: unattributedPower,
                  unattributedPercentage: unattributedPct,
                ),

                // 5. Compact Simulator Lab Shortcut
                const SimulatorSummaryCard(),

                // 6. Recent Power Change Timeline (FL Chart)
                PowerTimelineChart(
                  points: state.history,
                  isSimulated: state.telemetry?.isSimulated ?? true,
                ),

                // 7. Traceable Energy Story Insight Panel
                EnergyStoryPanel(
                  headline: headline,
                  detail: detail,
                ),

                const SizedBox(height: 32),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
