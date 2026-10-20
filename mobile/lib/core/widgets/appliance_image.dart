import 'package:flutter/material.dart';

/// Resilient appliance visual widget rendering high-fidelity illustrations
/// with graceful fallback and accessibility semantics.
class ApplianceImage extends StatelessWidget {
  final String applianceId;
  final double size;
  final BoxFit fit;
  final BorderRadius? borderRadius;
  final bool isActive;
  final String? customSemanticLabel;

  const ApplianceImage({
    super.key,
    required this.applianceId,
    this.size = 56.0,
    this.fit = BoxFit.cover,
    this.borderRadius,
    this.isActive = true,
    this.customSemanticLabel,
  });

  static String normalizeId(String id) {
    final lower = id.toLowerCase().trim().replaceAll(' ', '_');
    if (lower.contains('heater')) return 'water_heater';
    if (lower.contains('pump')) return 'water_pump';
    if (lower.contains('fan')) return 'ceiling_fan';
    if (lower.contains('bulb') || lower.contains('light') || lower.contains('led')) return 'led_bulb';
    return lower;
  }

  static String getDisplayName(String id) {
    final norm = normalizeId(id);
    switch (norm) {
      case 'water_heater':
        return 'Water Heater';
      case 'water_pump':
        return 'Water Pump';
      case 'ceiling_fan':
        return 'Ceiling Fan';
      case 'led_bulb':
        return 'LED Bulb';
      default:
        return id;
    }
  }

  static IconData getFallbackIcon(String id) {
    final norm = normalizeId(id);
    switch (norm) {
      case 'water_heater':
        return Icons.water_drop_rounded;
      case 'water_pump':
        return Icons.cyclone_rounded;
      case 'ceiling_fan':
        return Icons.air_rounded;
      case 'led_bulb':
        return Icons.lightbulb_outline_rounded;
      default:
        return Icons.electrical_services_rounded;
    }
  }

  @override
  Widget build(BuildContext context) {
    final normalized = normalizeId(applianceId);
    final assetPath = 'assets/images/appliances/$normalized.png';
    final radius = borderRadius ?? BorderRadius.circular(10.0);
    final displayName = getDisplayName(applianceId);
    final semanticLabel = customSemanticLabel ??
        '$displayName product illustration, state: ${isActive ? 'Active' : 'Off'}';

    final effectiveImage = ClipRRect(
      borderRadius: radius,
      child: Image.asset(
        assetPath,
        width: size,
        height: size,
        fit: fit,
        semanticLabel: semanticLabel,
        errorBuilder: (context, error, stackTrace) {
          return _buildFallback(context, normalized, radius);
        },
      ),
    );

    // Subtle dimming and saturation reduction when inactive for instant glanceability
    Widget content = effectiveImage;
    if (!isActive) {
      content = Opacity(
        opacity: 0.55,
        child: ColorFiltered(
          colorFilter: const ColorFilter.matrix(<double>[
            0.2126, 0.7152, 0.0722, 0, 0,
            0.2126, 0.7152, 0.0722, 0, 0,
            0.2126, 0.7152, 0.0722, 0, 0,
            0,      0,      0,      1, 0,
          ]),
          child: effectiveImage,
        ),
      );
    }

    return Semantics(
      label: semanticLabel,
      image: true,
      child: Container(
        width: size,
        height: size,
        decoration: BoxDecoration(
          borderRadius: radius,
          color: Colors.white,
          border: Border.all(
            color: isActive ? const Color(0xFF3159C9).withValues(alpha: 0.25) : const Color(0xFFE0E6EE),
            width: 1.0,
          ),
          boxShadow: [
            BoxShadow(
              color: const Color(0x0A0F1728),
              blurRadius: 4,
              offset: const Offset(0, 1),
            ),
          ],
        ),
        child: content,
      ),
    );
  }

  Widget _buildFallback(BuildContext context, String normalized, BorderRadius radius) {
    return Container(
      width: size,
      height: size,
      decoration: BoxDecoration(
        color: const Color(0xFFF1F5F9),
        borderRadius: radius,
      ),
      child: Center(
        child: Icon(
          getFallbackIcon(normalized),
          size: size * 0.5,
          color: const Color(0xFF52627A),
        ),
      ),
    );
  }
}
