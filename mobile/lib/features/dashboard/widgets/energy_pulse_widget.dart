import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import '../../../app/theme.dart';
import 'energy_pulse_painter.dart';

class EnergyPulseWidget extends StatefulWidget {
  final double activePowerW;
  final bool isSimulated;
  final bool isStale;
  final double size;

  const EnergyPulseWidget({
    super.key,
    required this.activePowerW,
    this.isSimulated = true,
    this.isStale = false,
    this.size = 280,
  });

  @override
  State<EnergyPulseWidget> createState() => _EnergyPulseWidgetState();
}

class _EnergyPulseWidgetState extends State<EnergyPulseWidget>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      vsync: this,
      duration: const Duration(seconds: 4),
    );
    if (!widget.isStale) {
      _controller.repeat();
    }
  }

  @override
  void didUpdateWidget(covariant EnergyPulseWidget oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (widget.isStale && _controller.isAnimating) {
      _controller.stop();
    } else if (!widget.isStale && !_controller.isAnimating) {
      _controller.repeat();
    }
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: widget.size,
      height: widget.size,
      child: Stack(
        alignment: Alignment.center,
        children: [
          // Animated Canvas Layer
          AnimatedBuilder(
            animation: _controller,
            builder: (context, child) {
              return CustomPaint(
                size: Size(widget.size, widget.size),
                painter: EnergyPulsePainter(
                  animationProgress: _controller.value,
                  activePowerW: widget.activePowerW,
                  isSimulated: widget.isSimulated,
                  isStale: widget.isStale,
                ),
              );
            },
          ),
          // Central Readout Layer
          Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Text(
                'TOTAL POWER',
                style: GoogleFonts.inter(
                  color: widget.isStale
                      ? EnergyMirrorColors.textMuted
                      : EnergyMirrorColors.primaryBlue,
                  fontSize: 10.5,
                  fontWeight: FontWeight.w700,
                  letterSpacing: 1.2,
                ),
              ),
              const SizedBox(height: 2),
              Row(
                mainAxisSize: MainAxisSize.min,
                crossAxisAlignment: CrossAxisAlignment.baseline,
                textBaseline: TextBaseline.alphabetic,
                children: [
                  Text(
                    widget.isStale ? '--' : widget.activePowerW.toInt().toString(),
                    style: GoogleFonts.inter(
                      color: EnergyMirrorColors.textPrimary,
                      fontSize: widget.size < 220 ? 38 : 48,
                      fontWeight: FontWeight.w800,
                      letterSpacing: -1.5,
                    ),
                  ),
                  const SizedBox(width: 4),
                  Text(
                    'W',
                    style: GoogleFonts.inter(
                      color: widget.isStale
                          ? EnergyMirrorColors.textMuted
                          : EnergyMirrorColors.primaryBlue,
                      fontSize: widget.size < 220 ? 18 : 22,
                      fontWeight: FontWeight.w700,
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 2),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                decoration: BoxDecoration(
                  color: widget.isStale
                      ? EnergyMirrorColors.softAmber
                      : EnergyMirrorColors.softSky,
                  borderRadius: BorderRadius.circular(4),
                ),
                child: Text(
                  widget.isStale ? 'Data Stale' : 'Aggregate Load',
                  style: GoogleFonts.inter(
                    color: widget.isStale
                        ? EnergyMirrorColors.amberAccent
                        : EnergyMirrorColors.primaryBlue,
                    fontSize: 10,
                    fontWeight: FontWeight.w600,
                    letterSpacing: 0.3,
                  ),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }
}
