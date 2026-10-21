import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mobile/core/models/appliance_definition_model.dart';
import 'package:mobile/features/dashboard/providers/appliance_registry_provider.dart';
import 'package:mobile/features/dashboard/widgets/appliance_registry_panel.dart';

void main() {
  group('ApplianceDefinition Model Tests', () {
    test('Correctly identifies protected default appliances', () {
      final protectedApp = ApplianceDefinition(
        applianceId: 'pump_01',
        name: 'Water Pump',
        nominalPowerW: 75.0,
        category: 'Motor',
        detectionCapability: 'PRODUCTION_RULE_MATCHED',
        evidenceNotes: 'Submersible water pump',
      );

      final customApp = ApplianceDefinition(
        applianceId: 'toaster_01',
        name: 'Kitchen Toaster',
        nominalPowerW: 800.0,
        category: 'Heating',
        detectionCapability: 'UNSUPPORTED',
        evidenceNotes: '2-slice toaster',
      );

      expect(protectedApp.isProtected, isTrue);
      expect(customApp.isProtected, isFalse);
      expect(protectedApp.description, equals('Submersible water pump'));
    });

    test('Serializes to and from JSON correctly', () {
      final json = {
        'id': 10,
        'appliance_id': 'ac_01',
        'name': 'Living Room AC',
        'nominal_power_w': 1200.0,
        'category': 'Cooling',
        'detection_capability': 'UNSUPPORTED',
        'is_enabled': true,
        'is_simulator_supported': false,
        'evidence_notes': 'Split inverter AC',
        'created_at': '2026-10-21T12:00:00Z',
        'updated_at': '2026-10-21T12:00:00Z',
      };

      final app = ApplianceDefinition.fromJson(json);
      expect(app.applianceId, equals('ac_01'));
      expect(app.name, equals('Living Room AC'));
      expect(app.nominalPowerW, equals(1200.0));
      expect(app.detectionCapability, equals('UNSUPPORTED'));
      expect(app.evidenceNotes, equals('Split inverter AC'));
      expect(app.description, equals('Split inverter AC'));

      final outJson = app.toJson();
      expect(outJson['appliance_id'], equals('ac_01'));
      expect(outJson['nominal_power_w'], equals(1200.0));
    });
  });

  group('ApplianceRegistryPanel Widget Tests', () {
    final mockAppliances = [
      ApplianceDefinition(
        applianceId: 'heater_01',
        name: 'Water Heater',
        nominalPowerW: 140.0,
        category: 'Heating',
        detectionCapability: 'PRODUCTION_RULE_MATCHED',
      ),
      ApplianceDefinition(
        applianceId: 'pump_01',
        name: 'Water Pump',
        nominalPowerW: 75.0,
        category: 'Motor',
        detectionCapability: 'PRODUCTION_RULE_MATCHED',
      ),
      ApplianceDefinition(
        applianceId: 'custom_iron',
        name: 'Electric Iron',
        nominalPowerW: 1000.0,
        category: 'Heating',
        detectionCapability: 'UNSUPPORTED',
      ),
    ];

    Widget wrapForTesting({
      required Widget child,
      List<Override> overrides = const [],
    }) {
      return ProviderScope(
        overrides: overrides,
        child: MaterialApp(
          home: Scaffold(
            body: SingleChildScrollView(
              child: child,
            ),
          ),
        ),
      );
    }

    testWidgets('Renders registry header, count chip, and appliance cards', (tester) async {
      await tester.pumpWidget(
        wrapForTesting(
          overrides: [
            applianceRegistryProvider.overrideWith(
              (ref) => ApplianceRegistryNotifier(
                initialState: ApplianceRegistryState(appliances: mockAppliances),
                autoLoad: false,
              ),
            ),
          ],
          child: const ApplianceRegistryPanel(),
        ),
      );

      await tester.pumpAndSettle();

      expect(find.text('APPLIANCE REGISTRY'), findsOneWidget);
      expect(find.text('3 Devices'), findsOneWidget);
      expect(find.text('Water Heater'), findsOneWidget);
      expect(find.text('Water Pump'), findsOneWidget);
      expect(find.text('Electric Iron'), findsOneWidget);
      expect(find.text('140 W'), findsOneWidget);
      expect(find.text('75 W'), findsOneWidget);
      expect(find.text('1000 W'), findsOneWidget);

      // Verify protected badge on default appliances
      expect(find.byIcon(Icons.lock_outline_rounded), findsNWidgets(2));

      // Verify capability badges
      expect(find.text('UNSUPPORTED'), findsOneWidget);
    });

    testWidgets('Opens Add Appliance dialog with required form controls', (tester) async {
      await tester.pumpWidget(
        wrapForTesting(
          overrides: [
            applianceRegistryProvider.overrideWith(
              (ref) => ApplianceRegistryNotifier(
                initialState: ApplianceRegistryState(appliances: mockAppliances),
                autoLoad: false,
              ),
            ),
          ],
          child: const ApplianceRegistryPanel(),
        ),
      );

      await tester.pumpAndSettle();

      // Click Add Appliance button
      final addButton = find.byKey(const Key('add_appliance_button'));
      expect(addButton, findsOneWidget);
      await tester.tap(addButton);
      await tester.pumpAndSettle();

      // Verify dialog is open
      expect(find.text('Register New Appliance'), findsOneWidget);
      expect(find.text('Appliance ID *'), findsOneWidget);
      expect(find.text('Display Name *'), findsOneWidget);
      expect(find.text('Watts *'), findsOneWidget);
      expect(find.text('Category'), findsOneWidget);
      expect(find.text('Detection Capability'), findsOneWidget);
      expect(find.text('Admin API Key (if connecting remotely)'), findsOneWidget);
      expect(find.text('Cancel'), findsOneWidget);
      expect(find.text('Register'), findsOneWidget);
    });
  });
}
