import 'package:flutter/material.dart';

import 'app_controller.dart';
import 'screens/shell_page.dart';
import 'screens/welcome_page.dart';
import 'theme/app_theme.dart';

class DalaApp extends StatelessWidget {
  const DalaApp({super.key, required this.controller});

  final DalaAppController controller;

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: controller,
      builder: (context, _) {
        return MaterialApp(
          title: 'Dala',
          debugShowCheckedModeBanner: false,
          theme: AppTheme.light(),
          home: controller.isBootstrapping
              ? const _BootstrapPage()
              : controller.hasSession
              ? DalaShellPage(controller: controller)
              : WelcomePage(controller: controller),
        );
      },
    );
  }
}

class _BootstrapPage extends StatelessWidget {
  const _BootstrapPage();

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: DecoratedBox(
        decoration: const BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topCenter,
            end: Alignment.bottomCenter,
            colors: [Color(0xFFF7F1E8), Color(0xFFECE4D9)],
          ),
        ),
        child: const Center(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              SizedBox(
                width: 28,
                height: 28,
                child: CircularProgressIndicator(strokeWidth: 3),
              ),
              SizedBox(height: 16),
              Text('Restoring your Dala space...'),
            ],
          ),
        ),
      ),
    );
  }
}
