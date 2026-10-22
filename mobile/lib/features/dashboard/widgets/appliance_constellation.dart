import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import '../../../app/theme.dart';
import '../../../core/models/telemetry_model.dart';
import 'appliance_node.dart';
import 'appliance_detail_sheet.dart';

class ApplianceConstellation extends StatefulWidget {
  final List<ApplianceEstimate> appliances;
  final double aggregatePowerW;

  const ApplianceConstellation({
    super.key,
    required this.appliances,
    required this.aggregatePowerW,
  });

  @override
  State<ApplianceConstellation> createState() => _ApplianceConstellationState();
}

class _ApplianceConstellationState extends State<ApplianceConstellation> {
  String _selectedCategory = 'ALL';

  void _showDetail(BuildContext context, ApplianceEstimate appliance) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (ctx) => ApplianceDetailSheet(appliance: appliance),
    );
  }

  @override
  Widget build(BuildContext context) {
    if (widget.appliances.isEmpty) {
      return Container(
        height: 100,
        margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: EnergyMirrorColors.surfaceElevated,
          borderRadius: BorderRadius.circular(14),
          border: Border.all(color: EnergyMirrorColors.surfaceBorder),
        ),
        child: Center(
          child: Text(
            'No appliance signatures detected',
            style: GoogleFonts.inter(color: EnergyMirrorColors.textMuted, fontSize: 13),
          ),
        ),
      );
    }

    final totalAttributedW = widget.appliances
        .fold<double>(0.0, (sum, a) => sum + a.estimatedPowerW)
        .toInt();

    // Extract categories
    final rawCategories = widget.appliances.map((a) => a.category.toUpperCase()).toSet().toList();
    final categories = ['ALL', ...rawCategories];

    final filteredAppliances = _selectedCategory == 'ALL'
        ? widget.appliances
        : widget.appliances
            .where((a) => a.category.toUpperCase() == _selectedCategory)
            .toList();

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'APPLIANCE BREAKDOWN',
                      style: GoogleFonts.inter(
                        color: EnergyMirrorColors.textPrimary,
                        fontSize: 13,
                        fontWeight: FontWeight.w800,
                        letterSpacing: 0.8,
                      ),
                    ),
                    const SizedBox(height: 2),
                    Text(
                      'Tap any appliance for signature details',
                      style: GoogleFonts.inter(
                        color: EnergyMirrorColors.textMuted,
                        fontSize: 11,
                      ),
                    ),
                  ],
                ),
              ),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                decoration: BoxDecoration(
                  color: EnergyMirrorColors.softSky,
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Text(
                  '$totalAttributedW W Attributed',
                  style: GoogleFonts.inter(
                    color: EnergyMirrorColors.primaryBlue,
                    fontSize: 11,
                    fontWeight: FontWeight.w700,
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 8),

          // Category filter pills if more than 1 category
          if (categories.length > 2)
            Padding(
              padding: const EdgeInsets.only(bottom: 8.0),
              child: SingleChildScrollView(
                scrollDirection: Axis.horizontal,
                child: Row(
                  children: categories.map((cat) {
                    final isSelected = _selectedCategory == cat;
                    return Padding(
                      padding: const EdgeInsets.only(right: 6.0),
                      child: InkWell(
                        onTap: () => setState(() => _selectedCategory = cat),
                        borderRadius: BorderRadius.circular(6),
                        child: Container(
                          padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3.5),
                          decoration: BoxDecoration(
                            color: isSelected
                                ? EnergyMirrorColors.primaryBlue
                                : EnergyMirrorColors.surfaceSubtle,
                            borderRadius: BorderRadius.circular(6),
                            border: Border.all(
                              color: isSelected
                                  ? EnergyMirrorColors.primaryBlue
                                  : EnergyMirrorColors.surfaceBorder,
                            ),
                          ),
                          child: Text(
                            cat,
                            style: GoogleFonts.inter(
                              color: isSelected ? Colors.white : EnergyMirrorColors.textSecondary,
                              fontSize: 10,
                              fontWeight: isSelected ? FontWeight.w700 : FontWeight.w500,
                            ),
                          ),
                        ),
                      ),
                    );
                  }).toList(),
                ),
              ),
            ),

          const SizedBox(height: 4),

          // Responsive grid layout (2-column on mobile, 4-column on tablet/desktop)
          LayoutBuilder(
            builder: (context, constraints) {
              final isNarrow = constraints.maxWidth < 600;
              final crossAxisCount = isNarrow ? 2 : 4;
              return GridView.builder(
                shrinkWrap: true,
                physics: const NeverScrollableScrollPhysics(),
                itemCount: filteredAppliances.length,
                gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
                  crossAxisCount: crossAxisCount,
                  crossAxisSpacing: 10,
                  mainAxisSpacing: 10,
                  childAspectRatio: isNarrow ? 1.05 : 1.22,
                ),
                itemBuilder: (context, index) {
                  final app = filteredAppliances[index];
                  return ApplianceNode(
                    appliance: app,
                    aggregatePowerW: widget.aggregatePowerW,
                    onTap: () => _showDetail(context, app),
                  );
                },
              );
            },
          ),
        ],
      ),
    );
  }
}
