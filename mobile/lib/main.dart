import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'app/routes.dart';
import 'app/theme.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  runApp(
    const ProviderScope(
      child: EnergyMirrorApp(),
    ),
  );
}

class EnergyMirrorApp extends StatelessWidget {
  const EnergyMirrorApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp.router(
      title: 'Energy Mirror',
      debugShowCheckedModeBanner: false,
      theme: EnergyMirrorTheme.lightTheme,
      routerConfig: appRouter,
    );
  }
}
