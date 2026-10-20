import 'package:flutter/material.dart';
import 'package:fl_chart/fl_chart.dart';
import 'package:google_fonts/google_fonts.dart';
import '../../../app/theme.dart';
import '../../../core/models/telemetry_model.dart';

class PowerTimelineChart extends StatelessWidget {
  final List<HistoryPoint> points;
  final bool isSimulated;

  const PowerTimelineChart({
    super.key,
    required this.points,
    this.isSimulated = true,
  });

  @override
  Widget build(BuildContext context) {
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
                  'POWER TIMELINE',
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
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                decoration: BoxDecoration(
                  color: EnergyMirrorColors.softSky,
                  borderRadius: BorderRadius.circular(4),
                ),
                child: Text(
                  '60 MIN WINDOW',
                  style: GoogleFonts.inter(
                    color: EnergyMirrorColors.primaryBlue,
                    fontSize: 9,
                    fontWeight: FontWeight.w700,
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          if (points.isEmpty)
            SizedBox(
              height: 140,
              child: Center(
                child: Text(
                  'No historical telemetry points available',
                  style: GoogleFonts.inter(color: EnergyMirrorColors.textMuted, fontSize: 12),
                ),
              ),
            )
          else
            SizedBox(
              height: 140,
              child: LineChart(
                LineChartData(
                  gridData: FlGridData(
                    show: true,
                    drawVerticalLine: false,
                    horizontalInterval: 100,
                    getDrawingHorizontalLine: (value) => FlLine(
                      color: EnergyMirrorColors.surfaceBorder,
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
                        reservedSize: 42,
                        interval: 100,
                        getTitlesWidget: (val, meta) {
                          if (val == meta.max || val == meta.min) return const SizedBox.shrink();
                          return Text(
                            '${val.toInt()}W',
                            style: GoogleFonts.inter(
                              color: EnergyMirrorColors.textMuted,
                              fontSize: 9.5,
                              fontWeight: FontWeight.w500,
                            ),
                          );
                        },
                      ),
                    ),
                    bottomTitles: AxisTitles(
                      sideTitles: SideTitles(
                        showTitles: true,
                        reservedSize: 22,
                        interval: points.length > 5 ? (points.length / 4).floorToDouble() : 1,
                        getTitlesWidget: (val, meta) {
                          final idx = val.toInt();
                          if (idx >= 0 && idx < points.length && idx % 10 == 0) {
                            final pt = points[idx];
                            final timeStr = '${pt.timestamp.hour.toString().padLeft(2, '0')}:${pt.timestamp.minute.toString().padLeft(2, '0')}';
                            return Text(
                              timeStr,
                              style: GoogleFonts.inter(
                                color: EnergyMirrorColors.textMuted,
                                fontSize: 9,
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
                  maxY: 350,
                  lineBarsData: [
                    LineChartBarData(
                      spots: points
                          .asMap()
                          .entries
                          .map((e) => FlSpot(e.key.toDouble(), e.value.activePowerW))
                          .toList(),
                      isCurved: true,
                      curveSmoothness: 0.2,
                      color: EnergyMirrorColors.primaryBlue,
                      barWidth: 2.2,
                      isStrokeCapRound: true,
                      dotData: FlDotData(
                        show: true,
                        checkToShowDot: (spot, barData) {
                          final idx = spot.x.toInt();
                          if (idx >= 0 && idx < points.length) {
                            return points[idx].applianceEvent != null &&
                                points[idx].applianceEvent!.isNotEmpty;
                          }
                          return false;
                        },
                        getDotPainter: (spot, percent, barData, index) {
                          return FlDotCirclePainter(
                            radius: 4,
                            color: EnergyMirrorColors.amberAccent,
                            strokeWidth: 2,
                            strokeColor: Colors.white,
                          );
                        },
                      ),
                      belowBarData: BarAreaData(
                        show: true,
                        gradient: LinearGradient(
                          begin: Alignment.topCenter,
                          end: Alignment.bottomCenter,
                          colors: [
                            EnergyMirrorColors.primaryBlue.withValues(alpha: 0.15),
                            EnergyMirrorColors.primaryBlue.withValues(alpha: 0.0),
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
    );
  }
}
