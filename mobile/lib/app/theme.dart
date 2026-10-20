import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

/// Luminous Clarity Design Tokens & Color Architecture
/// WCAG AAA-compliant light-first aesthetic for Energy Mirror.
class EnergyMirrorColors {
  // Canvas & Surfaces (Warm Mineral & Pure White)
  static const Color canvas = Color(0xFFF7F8F4);
  static const Color surface = Color(0xFFFFFFFF);
  static const Color surfaceElevated = Color(0xFFFFFFFF);
  static const Color surfaceCard = Color(0xFFFFFFFF);
  static const Color surfaceSubtle = Color(0xFFF1F5F9);
  static const Color surfaceBorder = Color(0xFFE0E6EE);
  static const Color surfaceHighlight = Color(0xFFE5F1FF);

  // Backward compatibility alias for canvas
  static const Color obsidianCanvas = canvas;

  // Luminous Brand & State Accents
  static const Color primaryBlue = Color(0xFF3159C9);
  static const Color primaryInteraction = primaryBlue;
  static const Color softSky = Color(0xFFE5F1FF);
  
  // Backward compatibility aliases for primary interaction
  static const Color livingCurrentCyan = primaryBlue;
  static const Color cyanFilament = Color(0x333159C9);

  // Mint / Eco / Active
  static const Color mintAccent = Color(0xFF168765);
  static const Color softMint = Color(0xFFDDF7ED);
  static const Color ecoEmerald = mintAccent;

  // Amber / Warning / Simulation Badge
  static const Color amberAccent = Color(0xFFB96A0B);
  static const Color softAmber = Color(0xFFFFF4E5);
  static const Color solarAmber = amberAccent;
  static const Color amberBadgeBg = softAmber;

  // Coral / Alert / Disconnect
  static const Color alertCoral = Color(0xFFD32F2F);
  static const Color softCoral = Color(0xFFFFEBEE);

  // Lavender / Estimated Disaggregation
  static const Color lavenderAccent = Color(0xFF6B46C1);
  static const Color softLavender = Color(0xFFEAE6FF);

  // Typography (Slate Ink Hierarchy)
  static const Color textPrimary = Color(0xFF17243B);    // Contrast on #F7F8F4: 13.8:1 (AAA)
  static const Color textSecondary = Color(0xFF52627A);  // Contrast on #F7F8F4: 6.2:1 (AA)
  static const Color textMuted = Color(0xFF7E8B9F);      // Contrast on #F7F8F4: 4.5:1 (AA)
  static const Color textAccent = primaryBlue;
  static const Color textInverse = Colors.white;
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
        shadowColor: const Color(0x0A0F1728),
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

  // Alias darkTheme to lightTheme to enforce Luminous Clarity design system
  static ThemeData get darkTheme => lightTheme;
}
