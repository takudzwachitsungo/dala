import 'package:flutter/material.dart';

import '../app_controller.dart';
import '../theme/app_theme.dart';
import '../widgets/dala_scaffold.dart';

class CirclesPage extends StatelessWidget {
  const CirclesPage({super.key, required this.controller});

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
              if (controller.isCirclesLoading) const LinearProgressIndicator(),
              if (controller.isCirclesLoading) const SizedBox(height: 18),
              Text(
                'Circles',
                style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                  fontWeight: FontWeight.w700,
                ),
              ),
              const SizedBox(height: 8),
              Text(
                'Community spaces for shared encouragement, prayer, and healing rhythms.',
                style: Theme.of(
                  context,
                ).textTheme.bodyMedium?.copyWith(color: AppTheme.secondaryText),
              ),
              const SizedBox(height: 20),
              if (controller.circles.isEmpty)
                const _EmptyCircleState()
              else
                ...controller.circles.map(
                  (circle) => Padding(
                    padding: const EdgeInsets.only(bottom: 14),
                    child: Card(
                      child: Padding(
                        padding: const EdgeInsets.all(20),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Row(
                              children: [
                                Container(
                                  width: 42,
                                  height: 42,
                                  decoration: const BoxDecoration(
                                    color: AppTheme.subtle,
                                    shape: BoxShape.circle,
                                  ),
                                  child: const Icon(
                                    Icons.groups_rounded,
                                    color: AppTheme.sage,
                                  ),
                                ),
                                const SizedBox(width: 12),
                                Expanded(
                                  child: Text(
                                    circle.name,
                                    style: Theme.of(context)
                                        .textTheme
                                        .titleMedium
                                        ?.copyWith(fontWeight: FontWeight.w700),
                                  ),
                                ),
                                OutlinedButton(
                                  onPressed: () =>
                                      controller.toggleCircleMembership(
                                        circle.id,
                                        !circle.isMember,
                                      ),
                                  child: Text(
                                    circle.isMember ? 'Leave' : 'Join',
                                  ),
                                ),
                              ],
                            ),
                            const SizedBox(height: 14),
                            Text(
                              circle.description,
                              style: Theme.of(context).textTheme.bodyMedium
                                  ?.copyWith(
                                    color: AppTheme.secondaryText,
                                    height: 1.45,
                                  ),
                            ),
                            const SizedBox(height: 16),
                            Wrap(
                              spacing: 20,
                              runSpacing: 12,
                              children: [
                                _Stat(
                                  label: '${circle.members}',
                                  caption: 'members',
                                ),
                                _Stat(label: circle.topic, caption: 'topic'),
                                _Stat(
                                  label: '${circle.postCount}',
                                  caption: 'posts',
                                ),
                              ],
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

class _EmptyCircleState extends StatelessWidget {
  const _EmptyCircleState();

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'No circles available yet',
              style: Theme.of(
                context,
              ).textTheme.titleMedium?.copyWith(fontWeight: FontWeight.w700),
            ),
            const SizedBox(height: 8),
            Text(
              'This section will populate as soon as the backend serves community groups.',
              style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                color: AppTheme.secondaryText,
                height: 1.4,
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _Stat extends StatelessWidget {
  const _Stat({required this.label, required this.caption});

  final String label;
  final String caption;

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          label,
          style: Theme.of(context).textTheme.titleSmall?.copyWith(
            fontWeight: FontWeight.w700,
            color: AppTheme.primaryText,
          ),
        ),
        const SizedBox(height: 2),
        Text(
          caption,
          style: Theme.of(
            context,
          ).textTheme.bodySmall?.copyWith(color: AppTheme.secondaryText),
        ),
      ],
    );
  }
}
