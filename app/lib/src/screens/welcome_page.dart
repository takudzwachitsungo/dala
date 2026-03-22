import 'package:flutter/material.dart';

import '../app_controller.dart';
import '../theme/app_theme.dart';
import '../widgets/dala_scaffold.dart';

class WelcomePage extends StatelessWidget {
  const WelcomePage({super.key, required this.controller});

  final DalaAppController controller;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: DalaScaffold(
        child: LayoutBuilder(
          builder: (context, constraints) {
            return SingleChildScrollView(
              padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 20),
              child: ConstrainedBox(
                constraints: BoxConstraints(minHeight: constraints.maxHeight),
                child: IntrinsicHeight(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: [
                      const Spacer(),
                      Container(
                        padding: const EdgeInsets.all(24),
                        decoration: BoxDecoration(
                          color: Colors.white.withValues(alpha: 0.7),
                          borderRadius: BorderRadius.circular(32),
                          border: Border.all(color: const Color(0x14FFFFFF)),
                        ),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Container(
                              width: 56,
                              height: 56,
                              decoration: const BoxDecoration(
                                color: AppTheme.sageSoft,
                                shape: BoxShape.circle,
                              ),
                              child: const Icon(
                                Icons.spa_rounded,
                                color: AppTheme.sage,
                              ),
                            ),
                            const SizedBox(height: 20),
                            Text(
                              'Welcome to Dala',
                              style: Theme.of(context).textTheme.headlineMedium
                                  ?.copyWith(fontWeight: FontWeight.w700),
                            ),
                            const SizedBox(height: 12),
                            Text(
                              'A safe place to pause, breathe, and feel heard. We\'re starting with an anonymous mobile foundation so the experience can grow around calm, care, and privacy.',
                              style: Theme.of(context).textTheme.bodyLarge
                                  ?.copyWith(
                                    color: AppTheme.muted,
                                    height: 1.45,
                                  ),
                            ),
                            if (controller.errorMessage != null) ...[
                              const SizedBox(height: 18),
                              Container(
                                width: double.infinity,
                                padding: const EdgeInsets.all(14),
                                decoration: BoxDecoration(
                                  color: const Color(0xFFF8ECE6),
                                  borderRadius: BorderRadius.circular(18),
                                ),
                                child: Text(
                                  controller.errorMessage!,
                                  style: Theme.of(context).textTheme.bodySmall
                                      ?.copyWith(
                                        color: AppTheme.ink,
                                        height: 1.35,
                                      ),
                                ),
                              ),
                            ],
                            const SizedBox(height: 24),
                            FilledButton(
                              onPressed: controller.isCreatingSession
                                  ? null
                                  : () => controller.continueAnonymously(),
                              child: Text(
                                controller.isCreatingSession
                                    ? 'Creating your space...'
                                    : 'Continue anonymously',
                              ),
                            ),
                            const SizedBox(height: 12),
                            OutlinedButton(
                              onPressed: () => _showComingSoon(context),
                              child: const Text('Create account'),
                            ),
                            const SizedBox(height: 12),
                            Center(
                              child: TextButton(
                                onPressed: () => _showComingSoon(context),
                                child: const Text('I already have an account'),
                              ),
                            ),
                          ],
                        ),
                      ),
                      const SizedBox(height: 28),
                      Wrap(
                        spacing: 10,
                        runSpacing: 10,
                        children: const [
                          _FeaturePill(label: 'Mood check-ins'),
                          _FeaturePill(label: 'Companion chat'),
                          _FeaturePill(label: 'Guided paths'),
                          _FeaturePill(label: 'Safety plan'),
                        ],
                      ),
                      const Spacer(),
                    ],
                  ),
                ),
              ),
            );
          },
        ),
      ),
    );
  }

  void _showComingSoon(BuildContext context) {
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text(
          'Account sign up and login can be the next mobile slice.',
        ),
      ),
    );
  }
}

class _FeaturePill extends StatelessWidget {
  const _FeaturePill({required this.label});

  final String label;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
      decoration: BoxDecoration(
        color: Colors.white.withValues(alpha: 0.75),
        borderRadius: BorderRadius.circular(999),
      ),
      child: Text(
        label,
        style: Theme.of(context).textTheme.bodySmall?.copyWith(
          color: AppTheme.muted,
          fontWeight: FontWeight.w600,
        ),
      ),
    );
  }
}
