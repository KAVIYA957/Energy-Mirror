import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

/// Electrum Slate (Luminous Energy Intelligence) Design System
/// WCAG AAA-compliant analytical aesthetic with tabular figures,
/// calm slate surfaces, and calibrated electrical signal accents.
class EnergyMirrorColors {
  // Canvas & Surfaces (Calm Slate Architecture)
  static const Color canvas = Color(0xFFF8FAFC);         // Slate 50
  static const Color surface = Color(0xFFFFFFFF);        // Pure White
  static const Color surfaceElevated = Color(0xFFFFFFFF);
  static const Color surfaceCard = Color(0xFFFFFFFF);
  static const Color surfaceSubtle = Color(0xFFF1F5F9);   // Slate 100
  static const Color surfaceBorder = Color(0xFFE2E8F0);   // Slate 200 Hairline
  static const Color surfaceBorderHover = Color(0xFFCBD5E1); // Slate 300
  static const Color surfaceHighlight = Color(0xFFEFF6FF); // Blue 50
  static const Color panelDark = Color(0xFF0F172A);       // Slate 900 for dark telemetry chips

  // Backward compatibility alias for canvas
  static const Color obsidianCanvas = canvas;

  // Luminous Brand & State Accents
  static const Color electricBlue = Color(0xFF2563EB);    // Blue 600 - High Contrast Primary
  static const Color primaryBlue = electricBlue;
  static const Color primaryInteraction = electricBlue;
  static const Color softSky = Color(0xFFEFF6FF);        // Blue 50
  static const Color softBlue = softSky;

  // Backward compatibility aliases for primary interaction
  static const Color livingCurrentCyan = primaryBlue;
  static const Color cyanFilament = Color(0x332563EB);

  // Mint / Eco / Active Load Flow
  static const Color mintAccent = Color(0xFF059669);      // Emerald 600
  static const Color softMint = Color(0xFFECFDF5);        // Emerald 50
  static const Color ecoEmerald = mintAccent;

  // Amber / Warning / Simulation Badge
  static const Color amberAccent = Color(0xFFD97706);     // Amber 600
  static const Color softAmber = Color(0xFFFFFBEB);       // Amber 50
  static const Color solarAmber = amberAccent;
  static const Color amberBadgeBg = softAmber;

  // Coral / Alert / Disconnect
  static const Color alertCoral = Color(0xFFDC2626);      // Red 600
  static const Color softCoral = Color(0xFFFEF2F2);       // Red 50

  // Purple / Lavender / Residual Floor & Unattributed Load
  static const Color residualPurple = Color(0xFF7C3AED);  // Violet 600
  static const Color softPurple = Color(0xFFF5F3FF);      // Violet 50
  static const Color lavenderAccent = residualPurple;
  static const Color softLavender = softPurple;

  // Typography (Slate Ink Hierarchy)
  static const Color textPrimary = Color(0xFF0F172A);     // Slate 900 - Contrast 16.2:1 (AAA)
  static const Color textSecondary = Color(0xFF475569);   // Slate 600 - Contrast 7.1:1 (AAA)
  static const Color textMuted = Color(0xFF64748B);       // Slate 500 - Contrast 4.6:1 (AA)
  static const Color textAccent = primaryBlue;
  static const Color textInverse = Colors.white;

  /// High-legibility Tabular Figures helper for numerical measurements (Watts, Volts, Amps, %)
  /// Eliminates digit jitter during 1-second live telemetry polling.
  static TextStyle tabularFigures({
    double fontSize = 14,
    FontWeight fontWeight = FontWeight.w700,
    Color? color,
    double? letterSpacing,
    double? height,
  }) {
    return GoogleFonts.inter(
      fontSize: fontSize,
      fontWeight: fontWeight,
      color: color ?? textPrimary,
      letterSpacing: letterSpacing,
      height: height,
      fontFeatures: const [FontFeature.tabularFigures()],
    );
  }
}

class EnergyMirrorTheme {
  static ThemeData get lightTheme {
    final baseTextTheme = GoogleFonts.interTextTheme();

    return ThemeData(
      useMaterial3: true,
      brightness: Brightness.light,
      scaffoldBackgroundColor: EnergyMirrorColors.canvas,
      colorScheme: const ColorScheme.light(
        primary: EnergyMirrorColors.primaryBlue,
        secondary: EnergyMirrorColors.amberAccent,
        surface: EnergyMirrorColors.surfaceElevated,
        surfaceContainerHighest: EnergyMirrorColors.surfaceSubtle,
        onPrimary: Colors.white,
        onSecondary: Colors.white,
        onSurface: EnergyMirrorColors.textPrimary,
        outline: EnergyMirrorColors.surfaceBorder,
        error: EnergyMirrorColors.alertCoral,
      ),
      textTheme: baseTextTheme.copyWith(
        displayLarge: baseTextTheme.displayLarge?.copyWith(
          color: EnergyMirrorColors.textPrimary,
          fontWeight: FontWeight.w800,
          letterSpacing: -1.5,
        ),
        headlineMedium: baseTextTheme.headlineMedium?.copyWith(
          color: EnergyMirrorColors.textPrimary,
          fontWeight: FontWeight.w700,
          letterSpacing: -0.5,
        ),
        titleLarge: baseTextTheme.titleLarge?.copyWith(
          color: EnergyMirrorColors.textPrimary,
          fontWeight: FontWeight.w700,
          fontSize: 18,
        ),
        titleMedium: baseTextTheme.titleMedium?.copyWith(
          color: EnergyMirrorColors.textPrimary,
          fontWeight: FontWeight.w600,
          fontSize: 15,
        ),
        bodyLarge: baseTextTheme.bodyLarge?.copyWith(
          color: EnergyMirrorColors.textPrimary,
          fontSize: 14,
        ),
        bodyMedium: baseTextTheme.bodyMedium?.copyWith(
          color: EnergyMirrorColors.textSecondary,
          fontSize: 13,
        ),
        bodySmall: baseTextTheme.bodySmall?.copyWith(
          color: EnergyMirrorColors.textMuted,
          fontSize: 11,
          fontWeight: FontWeight.w500,
        ),
      ),
      cardTheme: CardThemeData(
        color: EnergyMirrorColors.surfaceElevated,
        elevation: 0,
        shape: RoundedRectangleBorder(
          side: const BorderSide(color: EnergyMirrorColors.surfaceBorder, width: 1),
          borderRadius: BorderRadius.circular(14),
        ),
        shadowColor: const Color(0x080F1728),
      ),
      dividerTheme: const DividerThemeData(
        color: EnergyMirrorColors.surfaceBorder,
        thickness: 1,
        space: 1,
      ),
      navigationBarTheme: NavigationBarThemeData(
        backgroundColor: EnergyMirrorColors.surface,
        indicatorColor: EnergyMirrorColors.softSky,
        surfaceTintColor: Colors.transparent,
        elevation: 2,
        labelTextStyle: WidgetStateProperty.resolveWith((states) {
          if (states.contains(WidgetState.selected)) {
            return GoogleFonts.inter(
              color: EnergyMirrorColors.primaryBlue,
              fontWeight: FontWeight.w700,
              fontSize: 11,
            );
          }
          return GoogleFonts.inter(
            color: EnergyMirrorColors.textMuted,
            fontWeight: FontWeight.w500,
            fontSize: 11,
          );
        }),
        iconTheme: WidgetStateProperty.resolveWith((states) {
          if (states.contains(WidgetState.selected)) {
            return const IconThemeData(color: EnergyMirrorColors.primaryBlue, size: 22);
          }
          return const IconThemeData(color: EnergyMirrorColors.textMuted, size: 22);
        }),
      ),
      navigationRailTheme: NavigationRailThemeData(
        backgroundColor: EnergyMirrorColors.surface,
        indicatorColor: EnergyMirrorColors.softSky,
        selectedLabelTextStyle: GoogleFonts.inter(
          color: EnergyMirrorColors.primaryBlue,
          fontSize: 11,
          fontWeight: FontWeight.w700,
        ),
        unselectedLabelTextStyle: GoogleFonts.inter(
          color: EnergyMirrorColors.textMuted,
          fontSize: 11,
          fontWeight: FontWeight.w500,
        ),
        selectedIconTheme: const IconThemeData(color: EnergyMirrorColors.primaryBlue),
        unselectedIconTheme: const IconThemeData(color: EnergyMirrorColors.textMuted),
      ),
      bottomSheetTheme: const BottomSheetThemeData(
        backgroundColor: EnergyMirrorColors.surfaceElevated,
        surfaceTintColor: Colors.transparent,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
        ),
      ),
    );
  }

  // Alias darkTheme to lightTheme to enforce Electrum Slate design system
  static ThemeData get darkTheme => lightTheme;
}
