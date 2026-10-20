import 'dart:math' as math;
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:fl_chart/fl_chart.dart';
import '../../../app/theme.dart';
import '../../../core/models/telemetry_model.dart';
import '../providers/history_provider.dart';

class HistoryScreen extends ConsumerStatefulWidget {
  const HistoryScreen({super.key});

  @override
  ConsumerState<HistoryScreen> createState() => _HistoryScreenState();
}

class _HistoryScreenState extends ConsumerState<HistoryScreen> {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (mounted) {
        ref.read(historyProvider.notifier).fetchHistory();
      }
    });
  }

  String _formatIntervalLabel(int minutes) {
    if (minutes < 60) return '${minutes}m';
    final hours = (minutes / 60).round();
    return '${hours}h';
  }

  String _formatIntervalFull(int minutes) {
    switch (minutes) {
      case 15:
        return '15 Minutes';
      case 60:
        return '1 Hour';
      case 360:
        return '6 Hours';
      case 1440:
        return '24 Hours';
      default:
        return '$minutes Minutes';
    }
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(historyProvider);
    final notifier = ref.read(historyProvider.notifier);
    final points = state.historyData?.points ?? [];

    // Calculate Summary Statistics based on truthful sampled duration
    double avgPower = 0.0;
    double maxPower = 0.0;
    double minPower = 0.0;
    double energyKwh = 0.0;
    int sampledMinutes = 0;

    if (points.isNotEmpty) {
      final powers = points.map((p) => p.activePowerW).toList();
      maxPower = powers.reduce(math.max);
      minPower = powers.reduce(math.min);
      final sum = powers.reduce((a, b) => a + b);
      avgPower = sum / powers.length;

      // Compute truthful sampled duration from points timestamps rather than multiplying by full requested window
      if (points.length >= 2) {
        final spanSec = math.max(0, points.last.timestamp.difference(points.first.timestamp).inSeconds);
        sampledMinutes = math.max(1, (spanSec / 60.0).round());
      } else {
        sampledMinutes = 1;
      }
      final actualHours = sampledMinutes / 60.0;
      energyKwh = (avgPower * actualHours) / 1000.0;
    }

    // Deduplicate transitions in window by event description and minute bucket
    final seenKeys = <String>{};
    final eventsWithPoints = <HistoryPoint>[];
    for (final pt in points) {
      if (pt.applianceEvent != null && pt.applianceEvent!.isNotEmpty) {
        final key = '${pt.applianceEvent}_${pt.timestamp.year}_${pt.timestamp.month}_${pt.timestamp.day}_${pt.timestamp.hour}_${pt.timestamp.minute}';
        if (seenKeys.add(key)) {
          eventsWithPoints.add(pt);
        }
      }
    }

    return Scaffold(
      backgroundColor: EnergyMirrorColors.obsidianCanvas,
      body: SafeArea(
        child: RefreshIndicator(
          onRefresh: notifier.fetchHistory,
          color: EnergyMirrorColors.livingCurrentCyan,
          backgroundColor: EnergyMirrorColors.surfaceElevated,
          child: SingleChildScrollView(
            physics: const AlwaysScrollableScrollPhysics(),
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                // 1. Header with Truth Badge
                Row(
                  children: [
                    const Icon(Icons.analytics_rounded, size: 20, color: EnergyMirrorColors.livingCurrentCyan),
                    const SizedBox(width: 8),
                    const Expanded(
                      child: Text(
                        'ANALYTICS & HISTORY',
                        style: TextStyle(
                          color: EnergyMirrorColors.textPrimary,
                          fontSize: 14,
                          fontWeight: FontWeight.w700,
                          letterSpacing: 0.8,
                        ),
                        overflow: TextOverflow.ellipsis,
                      ),
                    ),
                    const SizedBox(width: 8),
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 3),
                      decoration: BoxDecoration(
                        color: EnergyMirrorColors.solarAmber.withValues(alpha: 0.12),
                        borderRadius: BorderRadius.circular(4),
                        border: Border.all(color: EnergyMirrorColors.solarAmber.withValues(alpha: 0.4)),
                      ),
                      child: const Text(
                        'SIMULATED DATA',
                        style: TextStyle(
                          color: EnergyMirrorColors.solarAmber,
                          fontSize: 9,
                          fontWeight: FontWeight.w700,
                          letterSpacing: 0.4,
                        ),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 14),

                // Top Error Notification Banner with Retry Action (when stale points exist)
                if (state.errorMessage != null && points.isNotEmpty)
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
                        const Icon(Icons.error_outline, size: 18, color: EnergyMirrorColors.alertCoral),
                        const SizedBox(width: 10),
                        Expanded(
                          child: Text(
                            state.errorMessage!,
                            style: const TextStyle(color: EnergyMirrorColors.alertCoral, fontSize: 11.5),
                          ),
                        ),
                        TextButton(
                          onPressed: notifier.fetchHistory,
                          style: TextButton.styleFrom(
                            foregroundColor: EnergyMirrorColors.alertCoral,
                            padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                          ),
                          child: const Text('Retry'),
                        ),
                      ],
                    ),
                  ),

                // 2. Selectable Interval Buttons: 15m, 1h, 6h, 24h
                Container(
                  padding: const EdgeInsets.all(4),
                  decoration: BoxDecoration(
                    color: EnergyMirrorColors.surfaceElevated,
                    borderRadius: BorderRadius.circular(10),
                    border: Border.all(color: EnergyMirrorColors.surfaceBorder),
                  ),
                  child: Row(
                    children: [15, 60, 360, 1440].map((interval) {
                      final isSelected = state.selectedIntervalMinutes == interval;
                      return Expanded(
                        child: GestureDetector(
                          onTap: () => notifier.selectInterval(interval),
                          child: AnimatedContainer(
                            duration: const Duration(milliseconds: 200),
                            padding: const EdgeInsets.symmetric(vertical: 8),
                            decoration: BoxDecoration(
                              color: isSelected
                                  ? EnergyMirrorColors.livingCurrentCyan.withValues(alpha: 0.15)
                                  : Colors.transparent,
                              borderRadius: BorderRadius.circular(8),
                              border: Border.all(
                                color: isSelected
                                    ? EnergyMirrorColors.livingCurrentCyan.withValues(alpha: 0.6)
                                    : Colors.transparent,
                              ),
                            ),
                            child: Center(
                              child: Text(
                                _formatIntervalLabel(interval),
                                style: TextStyle(
                                  color: isSelected
                                      ? EnergyMirrorColors.livingCurrentCyan
                                      : EnergyMirrorColors.textSecondary,
                                  fontSize: 12,
                                  fontWeight: isSelected ? FontWeight.w700 : FontWeight.w500,
                                ),
                              ),
                            ),
                          ),
                        ),
                      );
                    }).toList(),
                  ),
                ),
                const SizedBox(height: 12),

                // 3. Honest Range Banner (if data span < selected window)
                if (state.historyData?.availableRangeMinutes != null &&
                    state.historyData!.availableRangeMinutes! < state.selectedIntervalMinutes)
                  Container(
                    margin: const EdgeInsets.only(bottom: 12),
                    padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 8),
                    decoration: BoxDecoration(
                      color: EnergyMirrorColors.surfaceCard,
                      borderRadius: BorderRadius.circular(8),
                      border: Border.all(color: EnergyMirrorColors.surfaceBorder),
                    ),
                    child: Row(
                      children: [
                        const Icon(Icons.info_outline, size: 14, color: EnergyMirrorColors.solarAmber),
                        const SizedBox(width: 8),
                        Expanded(
                          child: Text(
                            'Showing available ${state.historyData!.availableRangeMinutes}m of requested ${_formatIntervalFull(state.selectedIntervalMinutes)} window (no artificial gap interpolation).',
                            style: const TextStyle(
                              color: EnergyMirrorColors.textSecondary,
                              fontSize: 10.5,
                            ),
                          ),
                        ),
                      ],
                    ),
                  ),

                // 4. Loading / Error / Content State
                if (state.isLoading && points.isEmpty)
                  Container(
                    height: 200,
                    alignment: Alignment.center,
                    child: const Column(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        CircularProgressIndicator(
                          strokeWidth: 2.5,
                          color: EnergyMirrorColors.livingCurrentCyan,
                        ),
                        SizedBox(height: 12),
                        Text(
                          'Loading telemetry history...',
                          style: TextStyle(color: EnergyMirrorColors.textMuted, fontSize: 12),
                        ),
                      ],
                    ),
                  )
                else if (state.errorMessage != null && points.isEmpty)
                  Container(
                    padding: const EdgeInsets.all(16),
                    decoration: BoxDecoration(
                      color: EnergyMirrorColors.alertCoral.withValues(alpha: 0.1),
                      borderRadius: BorderRadius.circular(10),
                      border: Border.all(color: EnergyMirrorColors.alertCoral.withValues(alpha: 0.3)),
                    ),
                    child: Column(
                      children: [
                        const Icon(Icons.error_outline, size: 28, color: EnergyMirrorColors.alertCoral),
                        const SizedBox(height: 8),
                        const Text(
                          'History Unavailable',
                          style: TextStyle(
                            color: EnergyMirrorColors.alertCoral,
                            fontSize: 14,
                            fontWeight: FontWeight.w700,
                          ),
                        ),
                        const SizedBox(height: 4),
                        Text(
                          state.errorMessage!,
                          style: const TextStyle(color: EnergyMirrorColors.alertCoral, fontSize: 12),
                          textAlign: TextAlign.center,
                        ),
                        const SizedBox(height: 12),
                        ElevatedButton.icon(
                          onPressed: notifier.fetchHistory,
                          icon: const Icon(Icons.refresh, size: 16),
                          label: const Text('Retry'),
                          style: ElevatedButton.styleFrom(
                            backgroundColor: EnergyMirrorColors.alertCoral,
                            foregroundColor: Colors.white,
                          ),
                        ),
                      ],
                    ),
                  )
                else if (points.isEmpty)
                  Container(
                    padding: const EdgeInsets.symmetric(vertical: 40, horizontal: 16),
                    alignment: Alignment.center,
                    decoration: BoxDecoration(
                      color: EnergyMirrorColors.surfaceElevated,
                      borderRadius: BorderRadius.circular(12),
                      border: Border.all(color: EnergyMirrorColors.surfaceBorder),
                    ),
                    child: Column(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        const Icon(Icons.history_toggle_off_rounded, size: 36, color: EnergyMirrorColors.textMuted),
                        const SizedBox(height: 10),
                        const Text(
                          'No telemetry samples recorded in this window.',
                          style: TextStyle(color: EnergyMirrorColors.textSecondary, fontSize: 13, fontWeight: FontWeight.w600),
                          textAlign: TextAlign.center,
                        ),
                        const SizedBox(height: 4),
                        const Text(
                          'Try selecting a wider interval or ensure the simulator is generating telemetry.',
                          style: TextStyle(color: EnergyMirrorColors.textMuted, fontSize: 11),
                          textAlign: TextAlign.center,
                        ),
                        const SizedBox(height: 14),
                        OutlinedButton.icon(
                          onPressed: notifier.fetchHistory,
                          icon: const Icon(Icons.refresh, size: 14),
                          label: const Text('Refresh'),
                          style: OutlinedButton.styleFrom(
                            foregroundColor: EnergyMirrorColors.livingCurrentCyan,
                            side: const BorderSide(color: EnergyMirrorColors.livingCurrentCyan),
                          ),
                        ),
                      ],
                    ),
                  )
                else ...[
                  // 5. Summary Statistics Grid
                  Row(
                    children: [
                      _buildMetricCard(
                        label: 'AVERAGE LOAD',
                        value: '${avgPower.toInt()} W',
                        color: EnergyMirrorColors.livingCurrentCyan,
                        icon: Icons.electric_meter_outlined,
                      ),
                      const SizedBox(width: 8),
                      _buildMetricCard(
                        label: 'PEAK LOAD',
                        value: '${maxPower.toInt()} W',
                        color: EnergyMirrorColors.solarAmber,
                        icon: Icons.trending_up_rounded,
                      ),
                    ],
                  ),
                  const SizedBox(height: 8),
                  Row(
                    children: [
                      _buildMetricCard(
                        label: 'MINIMUM LOAD',
                        value: '${minPower.toInt()} W',
                        color: EnergyMirrorColors.ecoEmerald,
                        icon: Icons.trending_down_rounded,
                      ),
                      const SizedBox(width: 8),
                      _buildMetricCard(
                        label: 'EST. ENERGY',
                        value: '${energyKwh.toStringAsFixed(3)} kWh',
                        color: EnergyMirrorColors.textPrimary,
                        icon: Icons.battery_charging_full_outlined,
                      ),
                    ],
                  ),
                  const SizedBox(height: 14),

                  // 6. Interactive Power Timeline Chart
                  Container(
                    padding: const EdgeInsets.all(14),
                    decoration: BoxDecoration(
                      color: EnergyMirrorColors.surfaceElevated,
                      borderRadius: BorderRadius.circular(12),
                      border: Border.all(color: EnergyMirrorColors.surfaceBorder),
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Row(
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          children: [
                            const Expanded(
                              child: Text(
                                'AGGREGATE ACTIVE POWER (W)',
                                overflow: TextOverflow.ellipsis,
                                style: TextStyle(
                                  color: EnergyMirrorColors.textMuted,
                                  fontSize: 10.5,
                                  fontWeight: FontWeight.w700,
                                  letterSpacing: 0.6,
                                ),
                              ),
                            ),
                            const SizedBox(width: 8),
                            Text(
                              '${points.length} samples',
                              style: const TextStyle(
                                color: EnergyMirrorColors.textMuted,
                                fontSize: 10,
                              ),
                            ),
                          ],
                        ),
                        const SizedBox(height: 16),
                        SizedBox(
                          height: 180,
                          child: LineChart(
                            LineChartData(
                              lineTouchData: LineTouchData(
                                enabled: true,
                                touchTooltipData: LineTouchTooltipData(
                                  getTooltipColor: (_) => EnergyMirrorColors.obsidianCanvas,
                                  tooltipRoundedRadius: 8,
                                  tooltipPadding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                                  tooltipBorder: const BorderSide(color: EnergyMirrorColors.surfaceBorder, width: 1),
                                  fitInsideHorizontally: true,
                                  fitInsideVertically: true,
                                  getTooltipItems: (touchedSpots) {
                                    return touchedSpots.map((spot) {
                                      final idx = spot.spotIndex;
                                      final pt = idx >= 0 && idx < points.length ? points[idx] : null;
                                      final timeStr = pt != null
                                          ? '${pt.timestamp.hour.toString().padLeft(2, '0')}:${pt.timestamp.minute.toString().padLeft(2, '0')}'
                                          : '';
                                      final eventStr = pt?.applianceEvent != null ? '\n${pt!.applianceEvent}' : '';
                                      return LineTooltipItem(
                                        '${spot.y.toInt()} W ($timeStr)$eventStr',
                                        const TextStyle(
                                          color: EnergyMirrorColors.livingCurrentCyan,
                                          fontSize: 10.5,
                                          fontWeight: FontWeight.w700,
                                        ),
                                      );
                                    }).toList();
                                  },
                                ),
                                getTouchedSpotIndicator: (barData, spotIndexes) {
                                  return spotIndexes.map((spotIndex) {
                                    return TouchedSpotIndicatorData(
                                      FlLine(color: EnergyMirrorColors.livingCurrentCyan.withValues(alpha: 0.4), strokeWidth: 1.2, dashArray: [4, 4]),
                                      FlDotData(
                                        show: true,
                                        getDotPainter: (spot, percent, barData, index) => FlDotCirclePainter(
                                          radius: 4.5,
                                          color: EnergyMirrorColors.livingCurrentCyan,
                                          strokeWidth: 2,
                                          strokeColor: Colors.white,
                                        ),
                                      ),
                                    );
                                  }).toList();
                                },
                              ),
                              gridData: FlGridData(
                                show: true,
                                drawVerticalLine: false,
                                horizontalInterval: 100,
                                getDrawingHorizontalLine: (value) => FlLine(
                                  color: EnergyMirrorColors.surfaceBorder.withValues(alpha: 0.5),
                                  strokeWidth: 0.8,
                                ),
                              ),
                              titlesData: FlTitlesData(
                                show: true,
                                rightTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
                                topTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
                                leftTitles: AxisTitles(
                                  sideTitles: SideTitles(
                                    showTitles: true,
                                    reservedSize: 38,
                                    interval: 100,
                                    getTitlesWidget: (val, meta) {
                                      if (val == meta.max || val == meta.min) return const SizedBox.shrink();
                                      return Text(
                                        '${val.toInt()}W',
                                        style: const TextStyle(
                                          color: EnergyMirrorColors.textMuted,
                                          fontSize: 9,
                                        ),
                                      );
                                    },
                                  ),
                                ),
                                bottomTitles: AxisTitles(
                                  sideTitles: SideTitles(
                                    showTitles: true,
                                    reservedSize: 22,
                                    interval: math.max(1, points.length / 4),
                                    getTitlesWidget: (val, meta) {
                                      final idx = val.toInt();
                                      if (idx < 0 || idx >= points.length) return const SizedBox.shrink();
                                      if (idx == 0) {
                                        return Text(
                                          '-${_formatIntervalLabel(state.selectedIntervalMinutes)}',
                                          style: const TextStyle(color: EnergyMirrorColors.textMuted, fontSize: 9),
                                        );
                                      } else if (idx >= points.length - 1) {
                                        return const Text(
                                          'Now',
                                          style: TextStyle(
                                            color: EnergyMirrorColors.livingCurrentCyan,
                                            fontSize: 9,
                                            fontWeight: FontWeight.bold,
                                          ),
                                        );
                                      }
                                      return const SizedBox.shrink();
                                    },
                                  ),
                                ),
                              ),
                              borderData: FlBorderData(show: false),
                              minY: 0,
                              maxY: math.max(350, (maxPower * 1.15)),
                              lineBarsData: [
                                LineChartBarData(
                                  spots: points.asMap().entries.map((e) {
                                    return FlSpot(e.key.toDouble(), e.value.activePowerW);
                                  }).toList(),
                                  isCurved: true,
                                  curveSmoothness: 0.15,
                                  color: EnergyMirrorColors.livingCurrentCyan,
                                  barWidth: 2.2,
                                  isStrokeCapRound: true,
                                  dotData: FlDotData(
                                    show: true,
                                    checkToShowDot: (spot, barData) {
                                      final idx = spot.x.toInt();
                                      return idx < points.length &&
                                          points[idx].applianceEvent != null &&
                                          points[idx].applianceEvent!.isNotEmpty;
                                    },
                                    getDotPainter: (spot, percent, barData, index) {
                                      return FlDotCirclePainter(
                                        radius: 4.0,
                                        color: EnergyMirrorColors.solarAmber,
                                        strokeWidth: 1.5,
                                        strokeColor: Colors.black,
                                      );
                                    },
                                  ),
                                  belowBarData: BarAreaData(
                                    show: true,
                                    gradient: LinearGradient(
                                      begin: Alignment.topCenter,
                                      end: Alignment.bottomCenter,
                                      colors: [
                                        EnergyMirrorColors.livingCurrentCyan.withValues(alpha: 0.22),
                                        EnergyMirrorColors.livingCurrentCyan.withValues(alpha: 0.0),
                                      ],
                                    ),
                                  ),
                                ),
                              ],
                            ),
                          ),
                        ),
                      ],
                    ),
                  ),
                  // 6.5. Timeline Point Transitions in Window
                  Container(
                    padding: const EdgeInsets.all(14),
                    decoration: BoxDecoration(
                      color: EnergyMirrorColors.surfaceElevated,
                      borderRadius: BorderRadius.circular(12),
                      border: Border.all(color: EnergyMirrorColors.surfaceBorder),
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Row(
                          children: [
                            const Expanded(
                              child: Text(
                                'DETECTED LOAD TRANSITIONS IN WINDOW',
                                overflow: TextOverflow.ellipsis,
                                style: TextStyle(
                                  color: EnergyMirrorColors.textMuted,
                                  fontSize: 10.5,
                                  fontWeight: FontWeight.w700,
                                  letterSpacing: 0.6,
                                ),
                              ),
                            ),
                            const SizedBox(width: 8),
                            Text(
                              '${eventsWithPoints.length} events',
                              style: const TextStyle(
                                color: EnergyMirrorColors.solarAmber,
                                fontSize: 10,
                                fontWeight: FontWeight.w600,
                              ),
                            ),
                          ],
                        ),
                        const SizedBox(height: 10),
                        if (eventsWithPoints.isEmpty)
                          const Padding(
                            padding: EdgeInsets.symmetric(vertical: 8.0),
                            child: Text(
                              'No discrete load switching events recorded in this time window.',
                              style: TextStyle(color: EnergyMirrorColors.textMuted, fontSize: 11),
                            ),
                          )
                        else
                          Column(
                            children: eventsWithPoints.map((pt) {
                              return Container(
                                margin: const EdgeInsets.only(bottom: 6),
                                padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 8),
                                decoration: BoxDecoration(
                                  color: EnergyMirrorColors.obsidianCanvas,
                                  borderRadius: BorderRadius.circular(8),
                                  border: Border.all(color: EnergyMirrorColors.surfaceBorder),
                                ),
                                child: Row(
                                  children: [
                                    Container(
                                      width: 6,
                                      height: 6,
                                      decoration: const BoxDecoration(
                                        color: EnergyMirrorColors.solarAmber,
                                        shape: BoxShape.circle,
                                      ),
                                    ),
                                    const SizedBox(width: 8),
                                    Expanded(
                                      child: Column(
                                        crossAxisAlignment: CrossAxisAlignment.start,
                                        children: [
                                          Text(
                                            pt.applianceEvent ?? 'Load Transition',
                                            style: const TextStyle(
                                              color: EnergyMirrorColors.textPrimary,
                                              fontSize: 11.5,
                                              fontWeight: FontWeight.w600,
                                            ),
                                          ),
                                          Text(
                                            '${pt.timestamp.toLocal().hour.toString().padLeft(2, '0')}:${pt.timestamp.toLocal().minute.toString().padLeft(2, '0')}',
                                            style: const TextStyle(
                                              color: EnergyMirrorColors.textMuted,
                                              fontSize: 9.5,
                                            ),
                                          ),
                                        ],
                                      ),
                                    ),
                                    Text(
                                      '${pt.activePowerW.toInt()} W',
                                      style: const TextStyle(
                                        color: EnergyMirrorColors.livingCurrentCyan,
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
                  ),
                  const SizedBox(height: 14),

                  // 7. Recorded Durable Load Events in Window (SQLite Archive)
                  Builder(
                    builder: (context) {
                      final persistedEvents = state.historyData?.events ?? [];
                      return Container(
                        padding: const EdgeInsets.all(14),
                        decoration: BoxDecoration(
                          color: EnergyMirrorColors.surfaceElevated,
                          borderRadius: BorderRadius.circular(12),
                          border: Border.all(color: EnergyMirrorColors.surfaceBorder),
                        ),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Row(
                              children: [
                                const Icon(
                                  Icons.inventory_2_outlined,
                                  size: 16,
                                  color: EnergyMirrorColors.livingCurrentCyan,
                                ),
                                const SizedBox(width: 8),
                                const Expanded(
                                  child: Text(
                                    'DURABLE EVENT ARCHIVE (SQLITE)',
                                    overflow: TextOverflow.ellipsis,
                                    style: TextStyle(
                                      color: EnergyMirrorColors.textMuted,
                                      fontSize: 10.5,
                                      fontWeight: FontWeight.w700,
                                      letterSpacing: 0.6,
                                    ),
                                  ),
                                ),
                                const SizedBox(width: 8),
                                Container(
                                  padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                                  decoration: BoxDecoration(
                                    color: EnergyMirrorColors.livingCurrentCyan.withValues(alpha: 0.12),
                                    borderRadius: BorderRadius.circular(4),
                                    border: Border.all(
                                      color: EnergyMirrorColors.livingCurrentCyan.withValues(alpha: 0.4),
                                    ),
                                  ),
                                  child: Text(
                                    '${persistedEvents.length} events',
                                    style: const TextStyle(
                                      color: EnergyMirrorColors.livingCurrentCyan,
                                      fontSize: 9.5,
                                      fontWeight: FontWeight.w700,
                                    ),
                                  ),
                                ),
                              ],
                            ),
                            const SizedBox(height: 6),
                            // Distinct Architecture Notice
                            Container(
                              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 5),
                              decoration: BoxDecoration(
                                color: EnergyMirrorColors.obsidianCanvas,
                                borderRadius: BorderRadius.circular(6),
                                border: Border.all(
                                  color: EnergyMirrorColors.surfaceBorder.withValues(alpha: 0.5),
                                ),
                              ),
                              child: const Row(
                                children: [
                                  Icon(
                                    Icons.dns_outlined,
                                    size: 12,
                                    color: EnergyMirrorColors.solarAmber,
                                  ),
                                  SizedBox(width: 6),
                                  Expanded(
                                    child: Text(
                                      'Durable event log stored in SQLite; survives server restarts (distinct from the transient simulator feed in Simulator Lab).',
                                      style: TextStyle(
                                        color: EnergyMirrorColors.textMuted,
                                        fontSize: 9.5,
                                      ),
                                    ),
                                  ),
                                ],
                              ),
                            ),
                            const SizedBox(height: 10),
                            if (persistedEvents.isEmpty)
                              Container(
                                padding: const EdgeInsets.symmetric(vertical: 16.0, horizontal: 8.0),
                                alignment: Alignment.center,
                                child: Column(
                                  children: [
                                    Icon(
                                      Icons.history_toggle_off_rounded,
                                      size: 28,
                                      color: EnergyMirrorColors.textMuted.withValues(alpha: 0.6),
                                    ),
                                    const SizedBox(height: 6),
                                    const Text(
                                      'No durable events recorded in this time window.',
                                      style: TextStyle(
                                        color: EnergyMirrorColors.textMuted,
                                        fontSize: 11,
                                        fontWeight: FontWeight.w600,
                                      ),
                                    ),
                                    const SizedBox(height: 3),
                                    const Text(
                                      'Toggle virtual appliances in Simulator Lab to record durable event transitions in SQLite.',
                                      style: TextStyle(
                                        color: EnergyMirrorColors.textMuted,
                                        fontSize: 10,
                                      ),
                                      textAlign: TextAlign.center,
                                    ),
                                  ],
                                ),
                              )
                            else
                              Column(
                                children: persistedEvents.map((evt) {
                                  final isMatched = evt.status == 'MATCHED';
                                  final isPositive = evt.deltaPowerW >= 0;
                                  final statusColor = isMatched
                                      ? EnergyMirrorColors.livingCurrentCyan
                                      : EnergyMirrorColors.solarAmber;
                                  final deltaColor = isPositive
                                      ? EnergyMirrorColors.solarAmber
                                      : EnergyMirrorColors.livingCurrentCyan;

                                  final timeStr =
                                      '${evt.timestamp.hour.toString().padLeft(2, '0')}:${evt.timestamp.minute.toString().padLeft(2, '0')}:${evt.timestamp.second.toString().padLeft(2, '0')}';

                                  return Container(
                                    margin: const EdgeInsets.only(bottom: 8),
                                    padding: const EdgeInsets.all(10),
                                    decoration: BoxDecoration(
                                      color: EnergyMirrorColors.obsidianCanvas,
                                      borderRadius: BorderRadius.circular(8),
                                      border: Border.all(
                                        color: statusColor.withValues(alpha: 0.3),
                                      ),
                                    ),
                                    child: Column(
                                      crossAxisAlignment: CrossAxisAlignment.start,
                                      children: [
                                        // Header Row: Status, Appliance / Step, Delta W
                                        Row(
                                          children: [
                                            Container(
                                              padding: const EdgeInsets.symmetric(horizontal: 5, vertical: 2),
                                              decoration: BoxDecoration(
                                                color: statusColor.withValues(alpha: 0.15),
                                                borderRadius: BorderRadius.circular(4),
                                                border: Border.all(
                                                  color: statusColor.withValues(alpha: 0.5),
                                                ),
                                              ),
                                              child: Text(
                                                evt.status,
                                                style: TextStyle(
                                                  color: statusColor,
                                                  fontSize: 9,
                                                  fontWeight: FontWeight.w700,
                                                  letterSpacing: 0.4,
                                                ),
                                              ),
                                            ),
                                            const SizedBox(width: 8),
                                            Expanded(
                                              child: Text(
                                                evt.applianceName ??
                                                    (evt.status == 'AMBIGUOUS'
                                                        ? 'Ambiguous Step'
                                                        : 'Load Transition'),
                                                style: const TextStyle(
                                                  color: EnergyMirrorColors.textPrimary,
                                                  fontSize: 12,
                                                  fontWeight: FontWeight.w600,
                                                ),
                                                overflow: TextOverflow.ellipsis,
                                              ),
                                            ),
                                            if (evt.transitionType != null) ...[
                                              Container(
                                                padding: const EdgeInsets.symmetric(horizontal: 5, vertical: 1.5),
                                                margin: const EdgeInsets.only(right: 6),
                                                decoration: BoxDecoration(
                                                  color: evt.transitionType == 'ON'
                                                      ? EnergyMirrorColors.solarAmber.withValues(alpha: 0.15)
                                                      : EnergyMirrorColors.livingCurrentCyan.withValues(alpha: 0.15),
                                                  borderRadius: BorderRadius.circular(4),
                                                ),
                                                child: Text(
                                                  evt.transitionType!,
                                                  style: TextStyle(
                                                    color: evt.transitionType == 'ON'
                                                        ? EnergyMirrorColors.solarAmber
                                                        : EnergyMirrorColors.livingCurrentCyan,
                                                    fontSize: 9,
                                                    fontWeight: FontWeight.w700,
                                                  ),
                                                ),
                                              ),
                                            ],
                                            Text(
                                              '${isPositive ? '+' : ''}${evt.deltaPowerW.toStringAsFixed(1)} W',
                                              style: TextStyle(
                                                color: deltaColor,
                                                fontSize: 12,
                                                fontWeight: FontWeight.w700,
                                              ),
                                            ),
                                          ],
                                        ),
                                        const SizedBox(height: 6),
                                        // Metadata Row: Time, Delta PF, Classification (Wrap to prevent overflow on compact mobile)
                                        Wrap(
                                          spacing: 8,
                                          runSpacing: 4,
                                          crossAxisAlignment: WrapCrossAlignment.center,
                                          children: [
                                            Text(
                                              timeStr,
                                              style: const TextStyle(
                                                color: EnergyMirrorColors.textMuted,
                                                fontSize: 10,
                                                fontWeight: FontWeight.w500,
                                              ),
                                            ),
                                            if (evt.deltaPf != null)
                                              Text(
                                                'ΔPF: ${evt.deltaPf! >= 0 ? '+' : ''}${evt.deltaPf!.toStringAsFixed(2)}',
                                                style: const TextStyle(
                                                  color: EnergyMirrorColors.textSecondary,
                                                  fontSize: 9.5,
                                                ),
                                              ),
                                            Container(
                                              padding: const EdgeInsets.symmetric(horizontal: 4, vertical: 1),
                                              decoration: BoxDecoration(
                                                color: EnergyMirrorColors.surfaceElevated,
                                                borderRadius: BorderRadius.circular(3),
                                                border: Border.all(
                                                  color: EnergyMirrorColors.surfaceBorder,
                                                ),
                                              ),
                                              child: Text(
                                                evt.dataClassification,
                                                style: const TextStyle(
                                                  color: EnergyMirrorColors.textMuted,
                                                  fontSize: 8.5,
                                                  fontWeight: FontWeight.w600,
                                                ),
                                              ),
                                            ),
                                          ],
                                        ),

                                        const SizedBox(height: 4),
                                        // Rule Description
                                        Text(
                                          evt.ruleDescription,
                                          style: const TextStyle(
                                            color: EnergyMirrorColors.textMuted,
                                            fontSize: 9.5,
                                            height: 1.3,
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
                    },
                  ),

                ],
                const SizedBox(height: 24),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildMetricCard({
    required String label,
    required String value,
    required Color color,
    required IconData icon,
  }) {
    return Expanded(
      child: Container(
        padding: const EdgeInsets.all(12),
        decoration: BoxDecoration(
          color: EnergyMirrorColors.surfaceElevated,
          borderRadius: BorderRadius.circular(10),
          border: Border.all(color: EnergyMirrorColors.surfaceBorder),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(icon, size: 14, color: color.withValues(alpha: 0.8)),
                const SizedBox(width: 6),
                Expanded(
                  child: Text(
                    label,
                    style: const TextStyle(
                      color: EnergyMirrorColors.textMuted,
                      fontSize: 9.5,
                      fontWeight: FontWeight.w700,
                      letterSpacing: 0.4,
                    ),
                    overflow: TextOverflow.ellipsis,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 6),
            Text(
              value,
              style: TextStyle(
                color: color,
                fontSize: 18,
                fontWeight: FontWeight.w800,
              ),
            ),
          ],
        ),
      ),
    );
  }
}
