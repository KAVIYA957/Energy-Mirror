import 'dart:math' as math;
import 'package:flutter/material.dart';
import '../../../app/theme.dart';

class EnergyPulsePainter extends CustomPainter {
  final double animationProgress; // 0.0 to 1.0 from AnimationController
  final double activePowerW;
  final bool isSimulated;
  final bool isStale;

  EnergyPulsePainter({
    required this.animationProgress,
    required this.activePowerW,
    this.isSimulated = true,
    this.isStale = false,
  });

  @override
  void paint(Canvas canvas, Size size) {
    final center = Offset(size.width / 2, size.height / 2);
    final baseRadius = math.min(size.width, size.height) * 0.44;

    // 1. Polar Coordinate Background Grid & Degree Tick Marks
    final tickPaint = Paint()
      ..color = EnergyMirrorColors.surfaceBorder
      ..strokeWidth = 0.8;

    final cardinalPaint = Paint()
      ..color = EnergyMirrorColors.primaryBlue.withValues(alpha: 0.3)
      ..strokeWidth = 1.2;

    const totalTicks = 72;
    for (int i = 0; i < totalTicks; i++) {
      final angle = (i * 2 * math.pi) / totalTicks;
      final isMajor = i % 18 == 0;
      final isMedium = i % 6 == 0;
      final tickLength = isMajor ? 8.0 : (isMedium ? 5.0 : 3.0);
      final outerR = baseRadius + 12;
      final innerR = outerR - tickLength;

      final p1 = Offset(center.dx + outerR * math.cos(angle), center.dy + outerR * math.sin(angle));
      final p2 = Offset(center.dx + innerR * math.cos(angle), center.dy + innerR * math.sin(angle));

      canvas.drawLine(p1, p2, isMajor ? cardinalPaint : tickPaint);
    }

    // 2. Concentric Instrumentation Rings
    final ringPaint = Paint()
      ..style = PaintingStyle.stroke
      ..strokeWidth = 0.8
      ..color = EnergyMirrorColors.surfaceBorder.withValues(alpha: 0.7);

    canvas.drawCircle(center, baseRadius * 0.72, ringPaint);
    canvas.drawCircle(center, baseRadius * 0.88, ringPaint);
    canvas.drawCircle(center, baseRadius * 1.04, ringPaint);

    // 3. Dynamic Sine-Wave Current Waveform (Luminous Precision Blue)
    if (!isStale) {
      final waveColor = isSimulated
          ? EnergyMirrorColors.primaryBlue
          : EnergyMirrorColors.mintAccent;

      final wavePaint = Paint()
        ..style = PaintingStyle.stroke
        ..strokeWidth = 2.0
        ..color = waveColor.withValues(alpha: 0.85);

      final glowPaint = Paint()
        ..style = PaintingStyle.stroke
        ..strokeWidth = 4.0
        ..color = waveColor.withValues(alpha: 0.15)
        ..maskFilter = const MaskFilter.blur(BlurStyle.normal, 3);

      final path = Path();
      const numPoints = 120;
      final waveRadius = baseRadius * 0.88;
      final amplitude = 3.0 + (math.min(activePowerW, 3000.0) / 3000.0) * 5.0;

      for (int i = 0; i <= numPoints; i++) {
        final theta = (i * 2 * math.pi) / numPoints;
        final phase = animationProgress * 2 * math.pi;

        final rOffset = amplitude * math.sin(4 * theta - phase) +
            (amplitude * 0.35) * math.cos(8 * theta + phase);
        final r = waveRadius + rOffset;

        final x = center.dx + r * math.cos(theta);
        final y = center.dy + r * math.sin(theta);

        if (i == 0) {
          path.moveTo(x, y);
        } else {
          path.lineTo(x, y);
        }
      }
      path.close();

      canvas.drawPath(path, glowPaint);
      canvas.drawPath(path, wavePaint);
    }

    // 4. Center Cutout Rim & Inner White Disc
    final innerDiscPaint = Paint()
      ..style = PaintingStyle.fill
      ..color = EnergyMirrorColors.surface;
    canvas.drawCircle(center, baseRadius * 0.62, innerDiscPaint);

    final centerRimPaint = Paint()
      ..style = PaintingStyle.stroke
      ..strokeWidth = 1.0
      ..color = EnergyMirrorColors.surfaceBorder;
    canvas.drawCircle(center, baseRadius * 0.62, centerRimPaint);
  }

  @override
  bool shouldRepaint(covariant EnergyPulsePainter oldDelegate) {
    return oldDelegate.animationProgress != animationProgress ||
        oldDelegate.activePowerW != activePowerW ||
        oldDelegate.isStale != isStale ||
        oldDelegate.isSimulated != isSimulated;
  }
}
