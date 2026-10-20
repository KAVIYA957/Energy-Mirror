import 'package:go_router/go_router.dart';
import '../features/navigation/widgets/app_shell.dart';
import '../features/dashboard/screens/dashboard_screen.dart';
import '../features/history/screens/history_screen.dart';
import '../features/simulator/screens/simulator_screen.dart';
import '../features/diagnostics/screens/diagnostics_screen.dart';

GoRouter createRouter({String initialLocation = '/'}) => GoRouter(
  initialLocation: initialLocation,
  routes: [
    ShellRoute(
      builder: (context, state, child) => AppShell(child: child),
      routes: [
        GoRoute(
          path: '/',
          builder: (context, state) => const DashboardScreen(),
        ),
        GoRoute(
          path: '/history',
          builder: (context, state) => const HistoryScreen(),
        ),
        GoRoute(
          path: '/simulator',
          builder: (context, state) => const SimulatorScreen(),
        ),
        GoRoute(
          path: '/diagnostics',
          builder: (context, state) => const DiagnosticsScreen(),
        ),
      ],
    ),
  ],
);

final appRouter = createRouter();
