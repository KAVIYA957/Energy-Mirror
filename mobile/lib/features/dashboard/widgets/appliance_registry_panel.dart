import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:google_fonts/google_fonts.dart';
import '../../../app/theme.dart';
import '../../../core/models/appliance_definition_model.dart';
import '../../../core/widgets/appliance_image.dart';
import '../providers/appliance_registry_provider.dart';

class ApplianceRegistryPanel extends ConsumerStatefulWidget {
  const ApplianceRegistryPanel({super.key});

  @override
  ConsumerState<ApplianceRegistryPanel> createState() => _ApplianceRegistryPanelState();
}

class _ApplianceRegistryPanelState extends ConsumerState<ApplianceRegistryPanel> {
  final _adminKeyController = TextEditingController();

  @override
  void dispose() {
    _adminKeyController.dispose();
    super.dispose();
  }

  void _showAddDialog() {
    showDialog(
      context: context,
      builder: (ctx) => _ApplianceFormDialog(
        title: 'Register New Appliance',
        isEdit: false,
        onSubmit: (payload, adminKey) async {
          final success = await ref
              .read(applianceRegistryProvider.notifier)
              .registerAppliance(payload, adminKey: adminKey);
          if (success && mounted) {
            ScaffoldMessenger.of(context).showSnackBar(
              SnackBar(
                content: Text('Appliance "${payload["name"]}" registered successfully.'),
                backgroundColor: EnergyMirrorColors.mintAccent,
                behavior: SnackBarBehavior.floating,
              ),
            );
          }
          return success;
        },
      ),
    );
  }

  void _showEditDialog(ApplianceDefinition appliance) {
    showDialog(
      context: context,
      builder: (ctx) => _ApplianceFormDialog(
        title: 'Edit Appliance: ${appliance.name}',
        isEdit: true,
        initialData: appliance,
        onSubmit: (payload, adminKey) async {
          final success = await ref
              .read(applianceRegistryProvider.notifier)
              .updateAppliance(appliance.applianceId, payload, adminKey: adminKey);
          if (success && mounted) {
            ScaffoldMessenger.of(context).showSnackBar(
              SnackBar(
                content: Text('Appliance "${appliance.name}" updated successfully.'),
                backgroundColor: EnergyMirrorColors.mintAccent,
                behavior: SnackBarBehavior.floating,
              ),
            );
          }
          return success;
        },
      ),
    );
  }

  void _confirmDelete(ApplianceDefinition appliance) {
    if (appliance.isProtected) {
      showDialog(
        context: context,
        builder: (ctx) => AlertDialog(
          backgroundColor: EnergyMirrorColors.surfaceElevated,
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
          title: Row(
            children: [
              const Icon(Icons.shield_rounded, color: EnergyMirrorColors.amberAccent, size: 22),
              const SizedBox(width: 8),
              Text(
                'Protected Appliance',
                style: GoogleFonts.inter(fontSize: 16, fontWeight: FontWeight.w700),
              ),
            ],
          ),
          content: Text(
            'Cannot delete protected default baseline appliance "${appliance.name}" (${appliance.applianceId}).\n\n'
            'This appliance is required for physical baseline accounting in the simulator. You can edit its ratings or disable it instead.',
            style: GoogleFonts.inter(fontSize: 13, color: EnergyMirrorColors.textSecondary),
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.of(ctx).pop(),
              child: const Text('OK'),
            ),
          ],
        ),
      );
      return;
    }

    final keyCtrl = TextEditingController();
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        backgroundColor: EnergyMirrorColors.surfaceElevated,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
        title: Row(
          children: [
            const Icon(Icons.delete_outline_rounded, color: EnergyMirrorColors.alertCoral, size: 22),
            const SizedBox(width: 8),
            Text(
              'Delete Appliance?',
              style: GoogleFonts.inter(fontSize: 16, fontWeight: FontWeight.w700),
            ),
          ],
        ),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Are you sure you want to delete "${appliance.name}" (${appliance.applianceId}) from the registry?\n\n'
              'This will remove it from the dynamic inventory and simulator subsystems.',
              style: GoogleFonts.inter(fontSize: 13, color: EnergyMirrorColors.textSecondary),
            ),
            const SizedBox(height: 12),
            TextField(
              controller: keyCtrl,
              obscureText: true,
              decoration: const InputDecoration(
                labelText: 'Admin API Key (if remote)',
                hintText: 'Optional for local loopback',
                isDense: true,
                border: OutlineInputBorder(),
              ),
              style: GoogleFonts.inter(fontSize: 12),
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(ctx).pop(),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            style: ElevatedButton.styleFrom(
              backgroundColor: EnergyMirrorColors.alertCoral,
              foregroundColor: Colors.white,
            ),
            onPressed: () async {
              Navigator.of(ctx).pop();
              final success = await ref
                  .read(applianceRegistryProvider.notifier)
                  .deleteAppliance(appliance.applianceId, adminKey: keyCtrl.text.trim());
              if (success && mounted) {
                ScaffoldMessenger.of(context).showSnackBar(
                  SnackBar(
                    content: Text('Appliance "${appliance.name}" deleted.'),
                    backgroundColor: EnergyMirrorColors.mintAccent,
                    behavior: SnackBarBehavior.floating,
                  ),
                );
              }
            },
            child: const Text('Delete'),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final regState = ref.watch(applianceRegistryProvider);
    final notifier = ref.read(applianceRegistryProvider.notifier);
    final appliances = regState.appliances;

    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: EnergyMirrorColors.surfaceElevated,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: EnergyMirrorColors.surfaceBorder, width: 1.2),
        boxShadow: const [
          BoxShadow(
            color: Color(0x080F1728),
            blurRadius: 10,
            offset: Offset(0, 3),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Header: Title, Count Badge, and Add Appliance Button
          Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Container(
                padding: const EdgeInsets.all(6),
                decoration: const BoxDecoration(
                  color: EnergyMirrorColors.softSky,
                  shape: BoxShape.circle,
                ),
                child: const Icon(
                  Icons.app_registration_rounded,
                  size: 16,
                  color: EnergyMirrorColors.primaryBlue,
                ),
              ),
              const SizedBox(width: 8),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Flexible(
                          child: Text(
                            'APPLIANCE REGISTRY',
                            style: GoogleFonts.inter(
                              color: EnergyMirrorColors.textPrimary,
                              fontSize: 13,
                              fontWeight: FontWeight.w800,
                              letterSpacing: 0.6,
                            ),
                            overflow: TextOverflow.ellipsis,
                          ),
                        ),
                        const SizedBox(width: 6),
                        Container(
                          padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                          decoration: BoxDecoration(
                            color: EnergyMirrorColors.softSky,
                            borderRadius: BorderRadius.circular(4),
                          ),
                          child: Text(
                            '${appliances.length} Devices',
                            style: GoogleFonts.inter(
                              color: EnergyMirrorColors.primaryBlue,
                              fontSize: 10,
                              fontWeight: FontWeight.w700,
                            ),
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 2),
                    Text(
                      'Dynamic definitions & NILM calibration gating',
                      style: GoogleFonts.inter(
                        color: EnergyMirrorColors.textMuted,
                        fontSize: 10.5,
                      ),
                      overflow: TextOverflow.ellipsis,
                    ),
                  ],
                ),
              ),
              IconButton(
                key: const Key('refresh_registry_button'),
                icon: const Icon(Icons.refresh_rounded, size: 16, color: EnergyMirrorColors.textMuted),
                tooltip: 'Refresh registry',
                onPressed: () => ref.read(applianceRegistryProvider.notifier).loadAppliances(),
                visualDensity: VisualDensity.compact,
                padding: EdgeInsets.zero,
                constraints: const BoxConstraints(),
              ),
              const SizedBox(width: 8),
              ElevatedButton.icon(
                key: const Key('add_appliance_button'),
                onPressed: _showAddDialog,
                icon: const Icon(Icons.add_rounded, size: 14),
                label: const Text('Add'),
                style: ElevatedButton.styleFrom(
                  backgroundColor: EnergyMirrorColors.primaryBlue,
                  foregroundColor: Colors.white,
                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                  textStyle: GoogleFonts.inter(fontSize: 11, fontWeight: FontWeight.w700),
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
                  elevation: 0,
                  visualDensity: VisualDensity.compact,
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),

          // Error banner if any
          if (regState.errorMessage != null)
            Container(
              margin: const EdgeInsets.only(bottom: 12),
              padding: const EdgeInsets.all(10),
              decoration: BoxDecoration(
                color: EnergyMirrorColors.softCoral,
                borderRadius: BorderRadius.circular(8),
                border: Border.all(color: EnergyMirrorColors.alertCoral.withValues(alpha: 0.3)),
              ),
              child: Row(
                children: [
                  const Icon(Icons.error_outline, size: 16, color: EnergyMirrorColors.alertCoral),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      regState.errorMessage!,
                      style: GoogleFonts.inter(color: EnergyMirrorColors.alertCoral, fontSize: 11),
                    ),
                  ),
                  IconButton(
                    icon: const Icon(Icons.close, size: 14, color: EnergyMirrorColors.alertCoral),
                    onPressed: () => notifier.clearMessages(),
                    padding: EdgeInsets.zero,
                    constraints: const BoxConstraints(minWidth: 20, minHeight: 20),
                  ),
                ],
              ),
            ),

          if (regState.isLoading && appliances.isEmpty)
            const Padding(
              padding: EdgeInsets.symmetric(vertical: 24),
              child: Center(
                child: CircularProgressIndicator(
                  strokeWidth: 2.5,
                  color: EnergyMirrorColors.primaryBlue,
                ),
              ),
            )
          else if (appliances.isEmpty)
            Container(
              padding: const EdgeInsets.symmetric(vertical: 24),
              alignment: Alignment.center,
              child: Column(
                children: [
                  const Icon(Icons.inventory_2_outlined, size: 32, color: EnergyMirrorColors.textMuted),
                  const SizedBox(height: 8),
                  Text(
                    'No appliances defined in registry.',
                    style: GoogleFonts.inter(color: EnergyMirrorColors.textMuted, fontSize: 12),
                  ),
                ],
              ),
            )
          else
            ListView.separated(
              shrinkWrap: true,
              physics: const NeverScrollableScrollPhysics(),
              itemCount: appliances.length,
              separatorBuilder: (_, _) => const Divider(
                height: 14,
                thickness: 0.8,
                color: EnergyMirrorColors.surfaceBorder,
              ),
              itemBuilder: (ctx, idx) {
                final app = appliances[idx];
                final isCalibrated = app.detectionCapability == 'PRODUCTION_RULE_MATCHED';
                final isUnsupported = app.detectionCapability == 'UNSUPPORTED';

                return Row(
                  children: [
                    ApplianceImage(
                      applianceId: app.applianceId,
                      size: 40,
                      isActive: app.isEnabled,
                    ),
                    const SizedBox(width: 10),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Row(
                            children: [
                              Text(
                                app.name,
                                style: GoogleFonts.inter(
                                  color: EnergyMirrorColors.textPrimary,
                                  fontSize: 13,
                                  fontWeight: FontWeight.w700,
                                ),
                              ),
                              if (app.isProtected) ...[
                                const SizedBox(width: 4),
                                const Tooltip(
                                  message: 'Protected default baseline appliance',
                                  child: Icon(Icons.lock_outline_rounded, size: 13, color: EnergyMirrorColors.textMuted),
                                ),
                              ],
                            ],
                          ),
                          const SizedBox(height: 3),
                          Wrap(
                            spacing: 6,
                            runSpacing: 4,
                            crossAxisAlignment: WrapCrossAlignment.center,
                            children: [
                              Text(
                                '${app.nominalPowerW.toInt()} W',
                                style: GoogleFonts.inter(
                                  color: EnergyMirrorColors.primaryBlue,
                                  fontSize: 11,
                                  fontWeight: FontWeight.w700,
                                ),
                              ),
                              if (app.expectedPf != null)
                                Text(
                                  '• PF ${app.expectedPf!.toStringAsFixed(2)}',
                                  style: GoogleFonts.inter(
                                    color: EnergyMirrorColors.textSecondary,
                                    fontSize: 10.5,
                                  ),
                                ),
                              Container(
                                padding: const EdgeInsets.symmetric(horizontal: 5, vertical: 1.5),
                                decoration: BoxDecoration(
                                  color: isCalibrated
                                      ? EnergyMirrorColors.softMint
                                      : (isUnsupported ? EnergyMirrorColors.softAmber : EnergyMirrorColors.softSky),
                                  borderRadius: BorderRadius.circular(4),
                                ),
                                child: Text(
                                  isCalibrated
                                      ? 'CALIBRATED (±${app.toleranceW?.toInt() ?? 0}W)'
                                      : (isUnsupported ? 'UNSUPPORTED' : 'EXPERIMENTAL'),
                                  style: GoogleFonts.inter(
                                    color: isCalibrated
                                        ? EnergyMirrorColors.mintAccent
                                        : (isUnsupported ? EnergyMirrorColors.amberAccent : EnergyMirrorColors.primaryBlue),
                                    fontSize: 9,
                                    fontWeight: FontWeight.w700,
                                  ),
                                ),
                              ),
                              if (!app.isSimulatorSupported)
                                Container(
                                  padding: const EdgeInsets.symmetric(horizontal: 5, vertical: 1.5),
                                  decoration: BoxDecoration(
                                    color: EnergyMirrorColors.surfaceSubtle,
                                    borderRadius: BorderRadius.circular(4),
                                  ),
                                  child: Text(
                                    'NON-SIMULATED',
                                    style: GoogleFonts.inter(
                                      color: EnergyMirrorColors.textMuted,
                                      fontSize: 9,
                                      fontWeight: FontWeight.w600,
                                    ),
                                  ),
                                ),
                            ],
                          ),
                        ],
                      ),
                    ),
                    IconButton(
                      icon: const Icon(Icons.edit_outlined, size: 17, color: EnergyMirrorColors.textSecondary),
                      tooltip: 'Edit appliance',
                      onPressed: () => _showEditDialog(app),
                      visualDensity: VisualDensity.compact,
                    ),
                    IconButton(
                      icon: Icon(
                        Icons.delete_outline_rounded,
                        size: 17,
                        color: app.isProtected ? EnergyMirrorColors.textMuted.withValues(alpha: 0.4) : EnergyMirrorColors.alertCoral,
                      ),
                      tooltip: app.isProtected ? 'Protected appliance' : 'Delete appliance',
                      onPressed: () => _confirmDelete(app),
                      visualDensity: VisualDensity.compact,
                    ),
                  ],
                );
              },
            ),
        ],
      ),
    );
  }
}

class _ApplianceFormDialog extends StatefulWidget {
  final String title;
  final bool isEdit;
  final ApplianceDefinition? initialData;
  final Future<bool> Function(Map<String, dynamic> payload, String? adminKey) onSubmit;

  const _ApplianceFormDialog({
    required this.title,
    required this.isEdit,
    this.initialData,
    required this.onSubmit,
  });

  @override
  State<_ApplianceFormDialog> createState() => _ApplianceFormDialogState();
}

class _ApplianceFormDialogState extends State<_ApplianceFormDialog> {
  final _formKey = GlobalKey<FormState>();

  late TextEditingController _idCtrl;
  late TextEditingController _nameCtrl;
  late TextEditingController _powerCtrl;
  late TextEditingController _pfCtrl;
  late TextEditingController _toleranceCtrl;
  late TextEditingController _notesCtrl;
  late TextEditingController _adminKeyCtrl;

  late String _category;
  late String _capability;
  late bool _isEnabled;
  late bool _isSimulatorSupported;
  bool _isSubmitting = false;
  String? _dialogError;

  final _categories = [
    'Heating',
    'Motor',
    'Lighting',
    'Cooking',
    'Refrigeration',
    'HVAC',
    'Electronics',
    'General',
  ];

  final _capabilities = [
    'UNSUPPORTED',
    'PRODUCTION_RULE_MATCHED',
    'EXPERIMENTAL_ONLY',
  ];

  @override
  void initState() {
    super.initState();
    final d = widget.initialData;
    _idCtrl = TextEditingController(text: d?.applianceId ?? '');
    _nameCtrl = TextEditingController(text: d?.name ?? '');
    _powerCtrl = TextEditingController(text: d != null ? d.nominalPowerW.toString() : '');
    _pfCtrl = TextEditingController(text: d?.expectedPf?.toString() ?? '0.95');
    _toleranceCtrl = TextEditingController(text: d?.toleranceW?.toString() ?? '10.0');
    _notesCtrl = TextEditingController(text: d?.evidenceNotes ?? '');
    _adminKeyCtrl = TextEditingController();

    _category = d != null && _categories.contains(d.category) ? d.category : 'General';
    _capability = d != null && _capabilities.contains(d.detectionCapability) ? d.detectionCapability : 'UNSUPPORTED';
    _isEnabled = d?.isEnabled ?? true;
    _isSimulatorSupported = d?.isSimulatorSupported ?? (widget.isEdit ? true : false);
  }

  @override
  void dispose() {
    _idCtrl.dispose();
    _nameCtrl.dispose();
    _powerCtrl.dispose();
    _pfCtrl.dispose();
    _toleranceCtrl.dispose();
    _notesCtrl.dispose();
    _adminKeyCtrl.dispose();
    super.dispose();
  }

  Future<void> _submit() async {
    if (!_formKey.currentState!.validate()) return;

    final power = double.tryParse(_powerCtrl.text.trim());
    if (power == null || power <= 0) {
      setState(() => _dialogError = 'Nominal power must be a positive number.');
      return;
    }

    final pf = double.tryParse(_pfCtrl.text.trim());
    if (pf != null && (pf < 0.0 || pf > 1.0)) {
      setState(() => _dialogError = 'Power factor must be between 0.0 and 1.0.');
      return;
    }

    double? tolerance;
    if (_capability == 'PRODUCTION_RULE_MATCHED') {
      tolerance = double.tryParse(_toleranceCtrl.text.trim());
      if (tolerance == null || tolerance <= 0) {
        setState(() => _dialogError = 'Production rule-matched appliances require a positive tolerance envelope.');
        return;
      }
    }

    setState(() {
      _isSubmitting = true;
      _dialogError = null;
    });

    final payload = <String, dynamic>{
      'name': _nameCtrl.text.trim(),
      'category': _category,
      'nominal_power_w': power,
      'expected_pf': pf,
      'tolerance_w': tolerance,
      'is_enabled': _isEnabled,
      'is_simulator_supported': _isSimulatorSupported,
      'detection_capability': _capability,
      'evidence_notes': _notesCtrl.text.trim().isNotEmpty ? _notesCtrl.text.trim() : null,
    };

    if (!widget.isEdit) {
      payload['appliance_id'] = _idCtrl.text.trim();
    }

    try {
      final success = await widget.onSubmit(payload, _adminKeyCtrl.text.trim());
      if (success && mounted) {
        Navigator.of(context).pop();
      } else {
        setState(() {
          _isSubmitting = false;
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _isSubmitting = false;
          _dialogError = e.toString().replaceFirst('Exception: ', '');
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      backgroundColor: EnergyMirrorColors.surfaceElevated,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(18)),
      title: Text(
        widget.title,
        style: GoogleFonts.inter(fontSize: 16, fontWeight: FontWeight.w800),
      ),
      content: SizedBox(
        width: 420,
        child: SingleChildScrollView(
          child: Form(
            key: _formKey,
            child: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                if (_dialogError != null)
                  Container(
                    margin: const EdgeInsets.only(bottom: 12),
                    padding: const EdgeInsets.all(8),
                    decoration: BoxDecoration(
                      color: EnergyMirrorColors.softCoral,
                      borderRadius: BorderRadius.circular(6),
                    ),
                    child: Text(
                      _dialogError!,
                      style: GoogleFonts.inter(color: EnergyMirrorColors.alertCoral, fontSize: 11),
                    ),
                  ),

                if (!widget.isEdit) ...[
                  TextFormField(
                    controller: _idCtrl,
                    decoration: const InputDecoration(
                      labelText: 'Appliance ID *',
                      hintText: 'e.g. kettle_01, ac_living',
                      isDense: true,
                      border: OutlineInputBorder(),
                    ),
                    style: GoogleFonts.inter(fontSize: 12.5),
                    validator: (v) {
                      if (v == null || v.trim().isEmpty) return 'ID is required';
                      if (!RegExp(r'^[a-zA-Z0-9_\-]+$').hasMatch(v.trim())) {
                        return 'Only alphanumeric, underscores, and hyphens';
                      }
                      return null;
                    },
                  ),
                  const SizedBox(height: 10),
                ],

                TextFormField(
                  controller: _nameCtrl,
                  decoration: const InputDecoration(
                    labelText: 'Display Name *',
                    hintText: 'e.g. Electric Kettle',
                    isDense: true,
                    border: OutlineInputBorder(),
                  ),
                  style: GoogleFonts.inter(fontSize: 12.5),
                  validator: (v) {
                    if (v == null || v.trim().isEmpty) return 'Name is required';
                    if (v.trim().length < 2) return 'Name must be at least 2 characters';
                    return null;
                  },
                ),
                const SizedBox(height: 10),

                Row(
                  children: [
                    Expanded(
                      flex: 3,
                      child: DropdownButtonFormField<String>(
                        isExpanded: true,
                        initialValue: _category,
                        decoration: const InputDecoration(
                          labelText: 'Category',
                          isDense: true,
                          border: OutlineInputBorder(),
                        ),
                        items: _categories
                            .map((c) => DropdownMenuItem(value: c, child: Text(c, style: GoogleFonts.inter(fontSize: 12))))
                            .toList(),
                        onChanged: (val) {
                          if (val != null) setState(() => _category = val);
                        },
                      ),
                    ),
                    const SizedBox(width: 8),
                    Expanded(
                      flex: 2,
                      child: TextFormField(
                        controller: _powerCtrl,
                        keyboardType: const TextInputType.numberWithOptions(decimal: true),
                        decoration: const InputDecoration(
                          labelText: 'Watts *',
                          hintText: '1800.0',
                          isDense: true,
                          border: OutlineInputBorder(),
                        ),
                        style: GoogleFonts.inter(fontSize: 12.5),
                        validator: (v) {
                          if (v == null || v.trim().isEmpty) return 'Watts is required';
                          final p = double.tryParse(v.trim());
                          if (p == null || p <= 0) return 'Must be > 0';
                          return null;
                        },
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 10),

                Row(
                  children: [
                    Expanded(
                      child: TextFormField(
                        controller: _pfCtrl,
                        keyboardType: const TextInputType.numberWithOptions(decimal: true),
                        decoration: const InputDecoration(
                          labelText: 'Expected PF',
                          hintText: '0.99',
                          isDense: true,
                          border: OutlineInputBorder(),
                        ),
                        style: GoogleFonts.inter(fontSize: 12.5),
                      ),
                    ),
                    const SizedBox(width: 8),
                    Expanded(
                      child: TextFormField(
                        controller: _toleranceCtrl,
                        keyboardType: const TextInputType.numberWithOptions(decimal: true),
                        decoration: InputDecoration(
                          labelText: _capability == 'PRODUCTION_RULE_MATCHED' ? 'Tolerance (±W) *' : 'Tolerance (±W)',
                          hintText: '10.0',
                          isDense: true,
                          border: const OutlineInputBorder(),
                        ),
                        style: GoogleFonts.inter(fontSize: 12.5),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 10),

                DropdownButtonFormField<String>(
                  isExpanded: true,
                  initialValue: _capability,
                  decoration: const InputDecoration(
                    labelText: 'Detection Capability',
                    isDense: true,
                    border: OutlineInputBorder(),
                  ),
                  items: _capabilities
                      .map((c) => DropdownMenuItem(
                            value: c,
                            child: Text(
                              c == 'UNSUPPORTED'
                                  ? 'UNSUPPORTED (Uncalibrated)'
                                  : (c == 'PRODUCTION_RULE_MATCHED'
                                      ? 'PRODUCTION_RULE_MATCHED'
                                      : 'EXPERIMENTAL_ONLY'),
                              style: GoogleFonts.inter(fontSize: 11.5),
                              overflow: TextOverflow.ellipsis,
                            ),
                          ))
                      .toList(),
                  onChanged: (val) {
                    if (val != null) setState(() => _capability = val);
                  },
                ),
                const SizedBox(height: 6),
                Text(
                  _capability == 'UNSUPPORTED'
                      ? '• Registers appliance without falsely claiming NILM recognition.'
                      : '• Calibrated rule detector will match transitions within the tolerance window.',
                  style: GoogleFonts.inter(color: EnergyMirrorColors.textMuted, fontSize: 10.5),
                ),
                const SizedBox(height: 10),

                SwitchListTile(
                  title: Text(
                    'Include in Virtual Simulator',
                    style: GoogleFonts.inter(fontSize: 12, fontWeight: FontWeight.w600),
                  ),
                  subtitle: Text(
                    'Allows toggling this load in Simulator Lab',
                    style: GoogleFonts.inter(fontSize: 10.5, color: EnergyMirrorColors.textMuted),
                  ),
                  value: _isSimulatorSupported,
                  onChanged: (v) => setState(() => _isSimulatorSupported = v),
                  dense: true,
                  contentPadding: EdgeInsets.zero,
                ),

                TextFormField(
                  controller: _adminKeyCtrl,
                  obscureText: true,
                  decoration: const InputDecoration(
                    labelText: 'Admin API Key (if connecting remotely)',
                    hintText: 'Leave blank for local development',
                    isDense: true,
                    border: OutlineInputBorder(),
                  ),
                  style: GoogleFonts.inter(fontSize: 11.5),
                ),
              ],
            ),
          ),
        ),
      ),
      actions: [
        TextButton(
          onPressed: _isSubmitting ? null : () => Navigator.of(context).pop(),
          child: const Text('Cancel'),
        ),
        ElevatedButton(
          onPressed: _isSubmitting ? null : _submit,
          style: ElevatedButton.styleFrom(
            backgroundColor: EnergyMirrorColors.primaryBlue,
            foregroundColor: Colors.white,
          ),
          child: _isSubmitting
              ? const SizedBox(
                  width: 16,
                  height: 16,
                  child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white),
                )
              : Text(widget.isEdit ? 'Save Changes' : 'Register'),
        ),
      ],
    );
  }
}
