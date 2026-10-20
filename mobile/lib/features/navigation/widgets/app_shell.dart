import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:google_fonts/google_fonts.dart';
import '../../../app/theme.dart';

class AppShell extends StatelessWidget {
  final Widget child;

  const AppShell({super.key, required this.child});

  int _calculateSelectedIndex(BuildContext context) {
    final location = GoRouterState.of(context).uri.path;
    if (location.startsWith('/history')) return 1;
    if (location.startsWith('/simulator')) return 2;
    if (location.startsWith('/diagnostics')) return 3;
    return 0;
  }

  void _onItemTapped(BuildContext context, int index) {
    switch (index) {
      case 0:
        context.go('/');
        break;
      case 1:
        context.go('/history');
        break;
      case 2:
        context.go('/simulator');
        break;
      case 3:
        context.go('/diagnostics');
        break;
    }
  }

  @override
  Widget build(BuildContext context) {
    final selectedIndex = _calculateSelectedIndex(context);
    final isWide = MediaQuery.of(context).size.width >= 720;

    if (isWide) {
      return Scaffold(
        backgroundColor: EnergyMirrorColors.canvas,
        body: Row(
          children: [
            // Responsive Sidebar Navigation Rail for Tablet & Desktop
            NavigationRail(
              backgroundColor: EnergyMirrorColors.surface,
              selectedIndex: selectedIndex,
              onDestinationSelected: (idx) => _onItemTapped(context, idx),
              labelType: NavigationRailLabelType.all,
              indicatorColor: EnergyMirrorColors.softSky,
              leading: Padding(
                padding: const EdgeInsets.symmetric(vertical: 16.0),
                child: Column(
                  children: [
                    Container(
                      width: 40,
                      height: 40,
                      decoration: BoxDecoration(
                        shape: BoxShape.circle,
                        color: EnergyMirrorColors.softSky,
                        border: Border.all(
                          color: EnergyMirrorColors.primaryBlue.withValues(alpha: 0.3),
                        ),
                      ),
                      child: const Center(
                        child: Icon(
                          Icons.bolt_rounded,
                          size: 22,
                          color: EnergyMirrorColors.primaryBlue,
                        ),
                      ),
                    ),
                    const SizedBox(height: 6),
                    Text(
                      'MIRROR',
                      style: GoogleFonts.inter(
                        color: EnergyMirrorColors.primaryBlue,
                        fontSize: 10,
                        fontWeight: FontWeight.w800,
                        letterSpacing: 1.2,
                      ),
                    ),
                  ],
                ),
              ),
              selectedIconTheme: const IconThemeData(color: EnergyMirrorColors.primaryBlue),
              unselectedIconTheme: const IconThemeData(color: EnergyMirrorColors.textMuted),
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
              destinations: const [
                NavigationRailDestination(
                  icon: Icon(Icons.dashboard_outlined),
                  selectedIcon: Icon(Icons.dashboard_rounded),
                  label: Text('Dashboard'),
                ),
                NavigationRailDestination(
                  icon: Icon(Icons.analytics_outlined),
                  selectedIcon: Icon(Icons.analytics_rounded),
                  label: Text('History'),
                ),
                NavigationRailDestination(
                  icon: Icon(Icons.tune_outlined),
                  selectedIcon: Icon(Icons.tune_rounded),
                  label: Text('Simulator'),
                ),
                NavigationRailDestination(
                  icon: Icon(Icons.monitor_heart_outlined),
                  selectedIcon: Icon(Icons.monitor_heart_rounded),
                  label: Text('Diagnostics'),
                ),
              ],
            ),
            const VerticalDivider(
              thickness: 1,
              width: 1,
              color: EnergyMirrorColors.surfaceBorder,
            ),
            Expanded(child: child),
          ],
        ),
      );
    }

    // Compact Mobile Navigation Bar
    return Scaffold(
      backgroundColor: EnergyMirrorColors.canvas,
      body: child,
      bottomNavigationBar: SafeArea(
        top: false,
        child: Container(
          decoration: const BoxDecoration(
            border: Border(
              top: BorderSide(color: EnergyMirrorColors.surfaceBorder, width: 1.0),
            ),
          ),
          child: NavigationBar(
            backgroundColor: EnergyMirrorColors.surface,
            indicatorColor: EnergyMirrorColors.softSky,
            selectedIndex: selectedIndex,
            onDestinationSelected: (idx) => _onItemTapped(context, idx),
            height: 64,
            labelBehavior: NavigationDestinationLabelBehavior.alwaysShow,
            destinations: const [
              NavigationDestination(
                icon: Icon(Icons.dashboard_outlined, color: EnergyMirrorColors.textMuted),
                selectedIcon: Icon(Icons.dashboard_rounded, color: EnergyMirrorColors.primaryBlue),
                label: 'Dashboard',
              ),
              NavigationDestination(
                icon: Icon(Icons.analytics_outlined, color: EnergyMirrorColors.textMuted),
                selectedIcon: Icon(Icons.analytics_rounded, color: EnergyMirrorColors.primaryBlue),
                label: 'History',
              ),
              NavigationDestination(
                icon: Icon(Icons.tune_outlined, color: EnergyMirrorColors.textMuted),
                selectedIcon: Icon(Icons.tune_rounded, color: EnergyMirrorColors.primaryBlue),
                label: 'Simulator',
              ),
              NavigationDestination(
                icon: Icon(Icons.monitor_heart_outlined, color: EnergyMirrorColors.textMuted),
                selectedIcon: Icon(Icons.monitor_heart_rounded, color: EnergyMirrorColors.primaryBlue),
                label: 'Diagnostics',
              ),
            ],
          ),
        ),
      ),
    );
  }
}
