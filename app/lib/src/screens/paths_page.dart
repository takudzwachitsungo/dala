import 'package:flutter/material.dart';

import '../app_controller.dart';
import '../theme/app_theme.dart';
import '../widgets/dala_scaffold.dart';

class PathsPage extends StatelessWidget {
  const PathsPage({super.key, required this.controller});

  final DalaAppController controller;

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: controller,
      builder: (context, _) {
        return DalaScaffold(
          child: ListView(
            padding: const EdgeInsets.fromLTRB(20, 18, 20, 120),
            children: [
              if (controller.isPathsLoading) const LinearProgressIndicator(),
              if (controller.isPathsLoading) const SizedBox(height: 18),
              Text(
                'Guided Paths',
                style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                  fontWeight: FontWeight.w700,
                ),
              ),
              const SizedBox(height: 8),
              Text(
                'Short journeys that blend emotional support, reflection, and faith.',
                style: Theme.of(
                  context,
                ).textTheme.bodyMedium?.copyWith(color: AppTheme.muted),
              ),
              const SizedBox(height: 20),
              if (controller.paths.isEmpty)
                const _EmptyState()
              else
                ...controller.paths.map(
                  (path) => Padding(
                    padding: const EdgeInsets.only(bottom: 14),
                    child: Card(
                      child: Padding(
                        padding: const EdgeInsets.all(20),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              path.title,
                              style: Theme.of(context).textTheme.titleLarge
                                  ?.copyWith(fontWeight: FontWeight.w700),
                            ),
                            const SizedBox(height: 8),
                            Text(
                              'A ${path.difficulty} path for ${path.category}.',
                              style: Theme.of(context).textTheme.bodyMedium
                                  ?.copyWith(
                                    color: AppTheme.muted,
                                    height: 1.4,
                                  ),
                            ),
                            const SizedBox(height: 14),
                            Wrap(
                              spacing: 8,
                              runSpacing: 8,
                              children: [
                                _MetaChip(
                                  icon: Icons.timelapse_rounded,
                                  label: path.duration == null
                                      ? 'Flexible pace'
                                      : '${path.duration} min',
                                ),
                                _MetaChip(
                                  icon: Icons.flag_rounded,
                                  label: '${path.stepCount} steps',
                                ),
                                _MetaChip(
                                  icon: Icons.groups_rounded,
                                  label: '${path.enrollmentCount} joined',
                                ),
                              ],
                            ),
                            const SizedBox(height: 16),
                            FilledButton(
                              onPressed: path.isEnrolled
                                  ? null
                                  : () => controller.enrollInPath(path.id),
                              child: Text(
                                path.isEnrolled ? 'Enrolled' : 'Start path',
                              ),
                            ),
                          ],
                        ),
                      ),
                    ),
                  ),
                ),
            ],
          ),
        );
      },
    );
  }
}

class _EmptyState extends StatelessWidget {
  const _EmptyState();

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'No paths available yet',
              style: Theme.of(
                context,
              ).textTheme.titleMedium?.copyWith(fontWeight: FontWeight.w700),
            ),
            const SizedBox(height: 8),
            Text(
              'Once your backend returns path content, it will show up here automatically.',
              style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                color: AppTheme.muted,
                height: 1.4,
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _MetaChip extends StatelessWidget {
  const _MetaChip({required this.icon, required this.label});

  final IconData icon;
  final String label;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
      decoration: BoxDecoration(
        color: const Color(0xFFF8F4EE),
        borderRadius: BorderRadius.circular(999),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, size: 16, color: AppTheme.sage),
          const SizedBox(width: 6),
          Text(
            label,
            style: Theme.of(context).textTheme.bodySmall?.copyWith(
              fontWeight: FontWeight.w600,
              color: AppTheme.ink,
            ),
          ),
        ],
      ),
    );
  }
}
