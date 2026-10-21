import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mobile/core/models/telemetry_model.dart';
import 'package:mobile/features/dashboard/widgets/appliance_constellation.dart';
import 'package:mobile/features/dashboard/widgets/appliance_node.dart';

void main() {
  Widget wrapForTesting(Widget child) {
    return MaterialApp(
      home: Scaffold(
        body: SingleChildScrollView(
          child: child,
        ),
      ),
    );
  }

  group('Dynamic Appliance Rendering Tests (Milestone 2C.13)', () {
    testWidgets('Empty state: Renders fallback banner when 0 appliances present', (tester) async {
      await tester.pumpWidget(
        wrapForTesting(
          const ApplianceConstellation(
            appliances: [],
            aggregatePowerW: 12.0,
          ),
        ),
      );

      expect(find.text('No appliance signatures detected'), findsOneWidget);
      expect(find.byType(ApplianceNode), findsNothing);
    });

    testWidgets('One-device state: Renders single appliance card correctly', (tester) async {
      final singleApp = [
        ApplianceEstimate(
          applianceId: 'pump_01',
          name: 'Water Pump',
          category: 'Motor',
          status: 'RUNNING',
          estimatedPowerW: 75.0,
          nominalPowerW: 75.0,
          detectionCapability: 'PRODUCTION_RULE_MATCHED',
          dataSource: 'NILM_ESTIMATED',
          timestamp: DateTime.now(),
        ),
      ];

      await tester.pumpWidget(
        wrapForTesting(
          ApplianceConstellation(
            appliances: singleApp,
            aggregatePowerW: 87.0,
          ),
        ),
      );

      expect(find.text('APPLIANCE BREAKDOWN'), findsOneWidget);
      expect(find.text('75 W Attributed'), findsOneWidget);
      expect(find.byType(ApplianceNode), findsOneWidget);
      expect(find.text('Water Pump'), findsOneWidget);
      expect(find.text('75W rated'), findsOneWidget);
      expect(find.text('RULE-BASED'), findsOneWidget);
    });

    testWidgets('Default four-device state: Renders all four baseline appliances', (tester) async {
      final fourApps = [
        ApplianceEstimate(
          applianceId: 'heater_01',
          name: 'Water Heater',
          category: 'Heating',
          status: 'RUNNING',
          estimatedPowerW: 140.0,
          nominalPowerW: 140.0,
          detectionCapability: 'PRODUCTION_RULE_MATCHED',
          dataSource: 'NILM_ESTIMATED',
          timestamp: DateTime.now(),
        ),
        ApplianceEstimate(
          applianceId: 'pump_01',
          name: 'Water Pump',
          category: 'Motor',
          status: 'RUNNING',
          estimatedPowerW: 75.0,
          nominalPowerW: 75.0,
          detectionCapability: 'PRODUCTION_RULE_MATCHED',
          dataSource: 'NILM_ESTIMATED',
          timestamp: DateTime.now(),
        ),
        ApplianceEstimate(
          applianceId: 'fan_01',
          name: 'Ceiling Fan',
          category: 'Motor',
          status: 'RUNNING',
          estimatedPowerW: 45.0,
          nominalPowerW: 45.0,
          detectionCapability: 'PRODUCTION_RULE_MATCHED',
          dataSource: 'NILM_ESTIMATED',
          timestamp: DateTime.now(),
        ),
        ApplianceEstimate(
          applianceId: 'bulb_01',
          name: 'LED Bulb',
          category: 'Lighting',
          status: 'RUNNING',
          estimatedPowerW: 12.0,
          nominalPowerW: 12.0,
          detectionCapability: 'PRODUCTION_RULE_MATCHED',
          dataSource: 'NILM_ESTIMATED',
          timestamp: DateTime.now(),
        ),
      ];

      await tester.pumpWidget(
        wrapForTesting(
          ApplianceConstellation(
            appliances: fourApps,
            aggregatePowerW: 284.0,
          ),
        ),
      );

      expect(find.byType(ApplianceNode), findsNWidgets(4));
      expect(find.text('Water Heater'), findsOneWidget);
      expect(find.text('Water Pump'), findsOneWidget);
      expect(find.text('Ceiling Fan'), findsOneWidget);
      expect(find.text('LED Bulb'), findsOneWidget);
      expect(find.text('272 W Attributed'), findsOneWidget);
    });

    testWidgets('More-than-four-device state: Renders variable number (6 devices) dynamically', (tester) async {
      final sixApps = [
        ApplianceEstimate(
          applianceId: 'heater_01',
          name: 'Water Heater',
          category: 'Heating',
          status: 'RUNNING',
          estimatedPowerW: 140.0,
          nominalPowerW: 140.0,
          detectionCapability: 'PRODUCTION_RULE_MATCHED',
          dataSource: 'NILM_ESTIMATED',
          timestamp: DateTime.now(),
        ),
        ApplianceEstimate(
          applianceId: 'pump_01',
          name: 'Water Pump',
          category: 'Motor',
          status: 'RUNNING',
          estimatedPowerW: 75.0,
          nominalPowerW: 75.0,
          detectionCapability: 'PRODUCTION_RULE_MATCHED',
          dataSource: 'NILM_ESTIMATED',
          timestamp: DateTime.now(),
        ),
        ApplianceEstimate(
          applianceId: 'fan_01',
          name: 'Ceiling Fan',
          category: 'Motor',
          status: 'RUNNING',
          estimatedPowerW: 45.0,
          nominalPowerW: 45.0,
          detectionCapability: 'PRODUCTION_RULE_MATCHED',
          dataSource: 'NILM_ESTIMATED',
          timestamp: DateTime.now(),
        ),
        ApplianceEstimate(
          applianceId: 'bulb_01',
          name: 'LED Bulb',
          category: 'Lighting',
          status: 'RUNNING',
          estimatedPowerW: 12.0,
          nominalPowerW: 12.0,
          detectionCapability: 'PRODUCTION_RULE_MATCHED',
          dataSource: 'NILM_ESTIMATED',
          timestamp: DateTime.now(),
        ),
        ApplianceEstimate(
          applianceId: 'toaster_01',
          name: 'Pop-up Toaster',
          category: 'Cooking',
          status: 'RUNNING',
          estimatedPowerW: 800.0,
          nominalPowerW: 800.0,
          detectionCapability: 'UNSUPPORTED',
          dataSource: 'NILM_ESTIMATED',
          timestamp: DateTime.now(),
        ),
        ApplianceEstimate(
          applianceId: 'air_cooler_01',
          name: 'Desert Air Cooler',
          category: 'Cooling',
          status: 'OFF',
          estimatedPowerW: 0.0,
          nominalPowerW: 165.0,
          detectionCapability: 'UNSUPPORTED',
          dataSource: 'NILM_ESTIMATED',
          timestamp: DateTime.now(),
        ),
      ];

      await tester.pumpWidget(
        wrapForTesting(
          ApplianceConstellation(
            appliances: sixApps,
            aggregatePowerW: 1084.0,
          ),
        ),
      );

      expect(find.byType(ApplianceNode), findsNWidgets(6));
      expect(find.text('Pop-up Toaster'), findsOneWidget);
      expect(find.text('800W rated'), findsOneWidget);
      expect(find.text('Desert Air Cooler'), findsOneWidget);
      expect(find.text('165W rated'), findsOneWidget);
      expect(find.text('1072 W Attributed'), findsOneWidget);
    });

    testWidgets('Detection honesty badge: Unsupported appliance renders SIMULATED badge', (tester) async {
      final uncalibratedApp = [
        ApplianceEstimate(
          applianceId: 'microwave_01',
          name: 'Microwave Oven',
          category: 'Cooking',
          status: 'RUNNING',
          estimatedPowerW: 950.0,
          nominalPowerW: 950.0,
          detectionCapability: 'UNSUPPORTED',
          dataSource: 'NILM_ESTIMATED',
          timestamp: DateTime.now(),
        ),
      ];

      await tester.pumpWidget(
        wrapForTesting(
          ApplianceConstellation(
            appliances: uncalibratedApp,
            aggregatePowerW: 962.0,
          ),
        ),
      );

      // Must display SIMULATED instead of RULE-BASED for unsupported detection capability
      expect(find.text('SIMULATED'), findsOneWidget);
      expect(find.text('RULE-BASED'), findsNothing);
    });
  });
}
