import 'package:flutter/material.dart';

import 'app_controller.dart';
import 'screens/shell_page.dart';
import 'screens/welcome_page.dart';
import 'theme/app_theme.dart';

class DalaApp extends StatelessWidget {
  const DalaApp({
    super.key,
    required this.controller,
  });

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
          home: controller.hasSession
              ? DalaShellPage(controller: controller)
              : WelcomePage(controller: controller),
        );
      },
    );
  }
}
