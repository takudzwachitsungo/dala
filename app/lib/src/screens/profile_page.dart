import 'package:flutter/material.dart';

import '../app_controller.dart';
import '../theme/app_theme.dart';
import '../widgets/dala_scaffold.dart';

class ProfilePage extends StatelessWidget {
  const ProfilePage({super.key, required this.controller});

  final DalaAppController controller;

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: controller,
      builder: (context, _) {
        final user = controller.user;
        if (user == null) {
          return const SizedBox.shrink();
        }

        final safetySections = _safetySections(controller.safetyPlan);

        return DalaScaffold(
          child: ListView(
            padding: const EdgeInsets.fromLTRB(20, 18, 20, 120),
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text(
                    'Your Space',
                    style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                      fontWeight: FontWeight.w700,
                    ),
                  ),
                  IconButton(
                    onPressed: () async {
                      await controller.logout();
                    },
                    icon: const Icon(Icons.logout_rounded),
                  ),
                ],
              ),
              if (controller.errorMessage != null) ...[
                const SizedBox(height: 16),
                _ProfileBanner(message: controller.errorMessage!),
              ],
              const SizedBox(height: 16),
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(20),
                  child: Row(
                    children: [
                      CircleAvatar(
                        radius: 30,
                        backgroundColor: AppTheme.subtle,
                        child: Text(
                          user.name.substring(0, 1).toUpperCase(),
                          style: Theme.of(context).textTheme.titleLarge
                              ?.copyWith(
                                color: AppTheme.sage,
                                fontWeight: FontWeight.w700,
                              ),
                        ),
                      ),
                      const SizedBox(width: 16),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              user.name,
                              style: Theme.of(context).textTheme.titleLarge
                                  ?.copyWith(fontWeight: FontWeight.w700),
                            ),
                            const SizedBox(height: 6),
                            Text(
                              'Member since ${_monthLabel(user.memberSince)} ${user.memberSince.year}',
                              style: Theme.of(context).textTheme.bodyMedium
                                  ?.copyWith(color: AppTheme.secondaryText),
                            ),
                          ],
                        ),
                      ),
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 16),
              Row(
                children: [
                  Expanded(
                    child: _MetricCard(
                      label: 'Streak',
                      value: '${user.streakDays} days',
                      icon: Icons.local_fire_department_rounded,
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: _MetricCard(
                      label: 'Milestones',
                      value: '${user.milestoneCount}',
                      icon: Icons.emoji_events_rounded,
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 12),
              _MetricCard(
                label: 'Activity',
                value:
                    '${user.totalConversations} conversations | ${controller.moodHistory.length} mood logs',
                icon: Icons.insights_rounded,
                compact: false,
              ),
              const SizedBox(height: 16),
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(20),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          Text(
                            'My Safety Plan',
                            style: Theme.of(context).textTheme.titleMedium
                                ?.copyWith(fontWeight: FontWeight.w700),
                          ),
                          TextButton.icon(
                            onPressed: controller.isSavingSafetyPlan
                                ? null
                                : () => _openSafetyPlanEditor(
                                    context,
                                    controller,
                                  ),
                            icon: controller.isSavingSafetyPlan
                                ? const SizedBox(
                                    width: 16,
                                    height: 16,
                                    child: CircularProgressIndicator(
                                      strokeWidth: 2,
                                    ),
                                  )
                                : const Icon(Icons.edit_rounded),
                            label: Text(
                              controller.isSavingSafetyPlan ? 'Saving' : 'Edit',
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 10),
                      Text(
                        'Private notes, grounding anchors, and who to contact first.',
                        style: Theme.of(
                          context,
                        ).textTheme.bodyMedium?.copyWith(color: AppTheme.secondaryText),
                      ),
                      const SizedBox(height: 14),
                      if (safetySections.isEmpty)
                        Text(
                          'Add your grounding steps, trusted contacts, and reasons to keep going so they are easy to reach when you need them.',
                          style: Theme.of(context).textTheme.bodyMedium
                              ?.copyWith(color: AppTheme.secondaryText, height: 1.4),
                        )
                      else
                        ...safetySections.map(
                          (section) => Padding(
                            padding: const EdgeInsets.only(bottom: 16),
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Text(
                                  section.title,
                                  style: Theme.of(context).textTheme.titleSmall
                                      ?.copyWith(fontWeight: FontWeight.w700),
                                ),
                                const SizedBox(height: 8),
                                ...section.items.map(
                                  (item) => Padding(
                                    padding: const EdgeInsets.only(bottom: 10),
                                    child: Row(
                                      crossAxisAlignment:
                                          CrossAxisAlignment.start,
                                      children: [
                                        const Padding(
                                          padding: EdgeInsets.only(top: 3),
                                          child: Icon(
                                            Icons.favorite_rounded,
                                            size: 16,
                                            color: Colors.redAccent,
                                          ),
                                        ),
                                        const SizedBox(width: 10),
                                        Expanded(
                                          child: Text(
                                            item,
                                            style: Theme.of(context)
                                                .textTheme
                                                .bodyMedium
                                                ?.copyWith(height: 1.4),
                                          ),
                                        ),
                                      ],
                                    ),
                                  ),
                                ),
                              ],
                            ),
                          ),
                        ),
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 16),
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(20),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'Mood history',
                        style: Theme.of(context).textTheme.titleMedium
                            ?.copyWith(fontWeight: FontWeight.w700),
                      ),
                      const SizedBox(height: 18),
                      if (controller.moodHistory.isEmpty)
                        Text(
                          'Your latest mood check-ins will show up here once you start logging them.',
                          style: Theme.of(context).textTheme.bodyMedium
                              ?.copyWith(color: AppTheme.secondaryText),
                        )
                      else
                        SizedBox(
                          height: 150,
                          child: Row(
                            crossAxisAlignment: CrossAxisAlignment.end,
                            mainAxisAlignment: MainAxisAlignment.spaceBetween,
                            children: controller.moodHistory
                                .take(7)
                                .toList()
                                .reversed
                                .map((entry) {
                                  final height = 26.0 + (entry.score * 18);
                                  return Column(
                                    mainAxisAlignment: MainAxisAlignment.end,
                                    children: [
                                      AnimatedContainer(
                                        duration: const Duration(
                                          milliseconds: 250,
                                        ),
                                        width: 24,
                                        height: height,
                                        decoration: BoxDecoration(
                                          color: entry.score >= 4
                                              ? AppTheme.sage
                                              : entry.score == 3
                                              ? AppTheme.sageHover
                                              : AppTheme.subtle,
                                          borderRadius: BorderRadius.circular(
                                            999,
                                          ),
                                        ),
                                      ),
                                      const SizedBox(height: 8),
                                      Text(
                                        _dayLabel(entry.createdAt),
                                        style: Theme.of(context)
                                            .textTheme
                                            .bodySmall
                                            ?.copyWith(color: AppTheme.secondaryText),
                                      ),
                                    ],
                                  );
                                })
                                .toList(),
                          ),
                        ),
                    ],
                  ),
                ),
              ),
            ],
          ),
        );
      },
    );
  }

  Future<void> _openSafetyPlanEditor(
    BuildContext context,
    DalaAppController controller,
  ) async {
    final result = await showModalBottomSheet<SafetyPlanData>(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (context) =>
          _SafetyPlanEditor(initialValue: controller.safetyPlan),
    );

    if (result != null) {
      await controller.saveSafetyPlan(result);
    }
  }

  List<_SafetySection> _safetySections(SafetyPlanData plan) {
    final sections = <_SafetySection>[
      _SafetySection('Warning signs', plan.warningSigns),
      _SafetySection('Internal coping', plan.internalCoping),
      _SafetySection('Social contacts', plan.socialContacts),
      _SafetySection('People to ask', plan.peopleToAsk),
      _SafetySection('Professionals', plan.professionals),
      _SafetySection('Emergency contacts', plan.emergencyContacts),
      if ((plan.safeEnvironment ?? '').trim().isNotEmpty)
        _SafetySection('Safe environment', [plan.safeEnvironment!.trim()]),
      _SafetySection('Reasons to live', plan.reasonsToLive),
    ];

    return sections.where((section) => section.items.isNotEmpty).toList();
  }

  String _monthLabel(DateTime date) {
    const months = [
      'Jan',
      'Feb',
      'Mar',
      'Apr',
      'May',
      'Jun',
      'Jul',
      'Aug',
      'Sep',
      'Oct',
      'Nov',
      'Dec',
    ];

    return months[date.month - 1];
  }

  String _dayLabel(DateTime date) {
    const days = ['M', 'T', 'W', 'T', 'F', 'S', 'S'];
    return days[date.weekday - 1];
  }
}

class _SafetySection {
  _SafetySection(this.title, List<String> rawItems)
    : items = _cleanItems(rawItems);

  final String title;
  final List<String> items;

  static List<String> _cleanItems(List<String> rawItems) {
    return rawItems
        .map((item) => item.trim())
        .where((item) => item.isNotEmpty)
        .toList();
  }
}

class _ProfileBanner extends StatelessWidget {
  const _ProfileBanner({required this.message});

  final String message;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: const Color(0xFFF8ECE6),
        borderRadius: BorderRadius.circular(18),
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Icon(Icons.info_outline_rounded, color: AppTheme.primaryText),
          const SizedBox(width: 10),
          Expanded(
            child: Text(
              message,
              style: Theme.of(context).textTheme.bodySmall?.copyWith(
                color: AppTheme.primaryText,
                height: 1.35,
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class _MetricCard extends StatelessWidget {
  const _MetricCard({
    required this.label,
    required this.value,
    required this.icon,
    this.compact = true,
  });

  final String label;
  final String value;
  final IconData icon;
  final bool compact;

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(18),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Icon(icon, color: AppTheme.sage),
            const SizedBox(height: 10),
            Text(
              label,
              style: Theme.of(
                context,
              ).textTheme.bodySmall?.copyWith(color: AppTheme.secondaryText),
            ),
            const SizedBox(height: 6),
            Text(
              value,
              style:
                  (compact
                          ? Theme.of(context).textTheme.titleLarge
                          : Theme.of(context).textTheme.titleMedium)
                      ?.copyWith(fontWeight: FontWeight.w700),
            ),
          ],
        ),
      ),
    );
  }
}

class _SafetyPlanEditor extends StatefulWidget {
  const _SafetyPlanEditor({required this.initialValue});

  final SafetyPlanData initialValue;

  @override
  State<_SafetyPlanEditor> createState() => _SafetyPlanEditorState();
}

class _SafetyPlanEditorState extends State<_SafetyPlanEditor> {
  late final TextEditingController _warningSignsController;
  late final TextEditingController _internalCopingController;
  late final TextEditingController _socialContactsController;
  late final TextEditingController _peopleToAskController;
  late final TextEditingController _professionalsController;
  late final TextEditingController _emergencyContactsController;
  late final TextEditingController _safeEnvironmentController;
  late final TextEditingController _reasonsToLiveController;

  @override
  void initState() {
    super.initState();
    _warningSignsController = TextEditingController(
      text: widget.initialValue.warningSigns.join('\n'),
    );
    _internalCopingController = TextEditingController(
      text: widget.initialValue.internalCoping.join('\n'),
    );
    _socialContactsController = TextEditingController(
      text: widget.initialValue.socialContacts.join('\n'),
    );
    _peopleToAskController = TextEditingController(
      text: widget.initialValue.peopleToAsk.join('\n'),
    );
    _professionalsController = TextEditingController(
      text: widget.initialValue.professionals.join('\n'),
    );
    _emergencyContactsController = TextEditingController(
      text: widget.initialValue.emergencyContacts.join('\n'),
    );
    _safeEnvironmentController = TextEditingController(
      text: widget.initialValue.safeEnvironment ?? '',
    );
    _reasonsToLiveController = TextEditingController(
      text: widget.initialValue.reasonsToLive.join('\n'),
    );
  }

  @override
  void dispose() {
    _warningSignsController.dispose();
    _internalCopingController.dispose();
    _socialContactsController.dispose();
    _peopleToAskController.dispose();
    _professionalsController.dispose();
    _emergencyContactsController.dispose();
    _safeEnvironmentController.dispose();
    _reasonsToLiveController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final bottomInset = MediaQuery.of(context).viewInsets.bottom;

    return Padding(
      padding: EdgeInsets.only(bottom: bottomInset),
      child: DraggableScrollableSheet(
        initialChildSize: 0.88,
        minChildSize: 0.65,
        maxChildSize: 0.95,
        builder: (context, scrollController) {
          return Container(
            decoration: const BoxDecoration(
              color: Color(0xFFFFFBF6),
              borderRadius: BorderRadius.vertical(top: Radius.circular(30)),
            ),
            child: Column(
              children: [
                const SizedBox(height: 12),
                Container(
                  width: 44,
                  height: 4,
                  decoration: BoxDecoration(
                    color: const Color(0xFFD5CBBB),
                    borderRadius: BorderRadius.circular(999),
                  ),
                ),
                Expanded(
                  child: ListView(
                    controller: scrollController,
                    padding: const EdgeInsets.fromLTRB(20, 20, 20, 24),
                    children: [
                      Text(
                        'Edit safety plan',
                        style: Theme.of(context).textTheme.headlineSmall
                            ?.copyWith(fontWeight: FontWeight.w700),
                      ),
                      const SizedBox(height: 8),
                      Text(
                        'Use one line per item so the app can present your plan clearly when you need it.',
                        style: Theme.of(
                          context,
                        ).textTheme.bodyMedium?.copyWith(color: AppTheme.secondaryText),
                      ),
                      const SizedBox(height: 20),
                      _EditorField(
                        label: 'Warning signs',
                        controller: _warningSignsController,
                      ),
                      _EditorField(
                        label: 'Internal coping',
                        controller: _internalCopingController,
                      ),
                      _EditorField(
                        label: 'Social contacts',
                        controller: _socialContactsController,
                      ),
                      _EditorField(
                        label: 'People to ask',
                        controller: _peopleToAskController,
                      ),
                      _EditorField(
                        label: 'Professionals',
                        controller: _professionalsController,
                      ),
                      _EditorField(
                        label: 'Emergency contacts',
                        controller: _emergencyContactsController,
                      ),
                      _EditorField(
                        label: 'Safe environment',
                        controller: _safeEnvironmentController,
                        minLines: 2,
                      ),
                      _EditorField(
                        label: 'Reasons to live',
                        controller: _reasonsToLiveController,
                      ),
                    ],
                  ),
                ),
                Padding(
                  padding: const EdgeInsets.fromLTRB(20, 12, 20, 20),
                  child: Row(
                    children: [
                      Expanded(
                        child: OutlinedButton(
                          onPressed: () => Navigator.of(context).pop(),
                          child: const Text('Cancel'),
                        ),
                      ),
                      const SizedBox(width: 12),
                      Expanded(
                        child: FilledButton(
                          onPressed: () {
                            Navigator.of(context).pop(
                              SafetyPlanData(
                                warningSigns: _splitLines(
                                  _warningSignsController.text,
                                ),
                                internalCoping: _splitLines(
                                  _internalCopingController.text,
                                ),
                                socialContacts: _splitLines(
                                  _socialContactsController.text,
                                ),
                                peopleToAsk: _splitLines(
                                  _peopleToAskController.text,
                                ),
                                professionals: _splitLines(
                                  _professionalsController.text,
                                ),
                                emergencyContacts: _splitLines(
                                  _emergencyContactsController.text,
                                ),
                                safeEnvironment:
                                    _safeEnvironmentController.text
                                        .trim()
                                        .isEmpty
                                    ? null
                                    : _safeEnvironmentController.text.trim(),
                                reasonsToLive: _splitLines(
                                  _reasonsToLiveController.text,
                                ),
                              ),
                            );
                          },
                          child: const Text('Save plan'),
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          );
        },
      ),
    );
  }

  List<String> _splitLines(String value) {
    return value
        .split('\n')
        .map((item) => item.trim())
        .where((item) => item.isNotEmpty)
        .toList();
  }
}

class _EditorField extends StatelessWidget {
  const _EditorField({
    required this.label,
    required this.controller,
    this.minLines = 3,
  });

  final String label;
  final TextEditingController controller;
  final int minLines;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 14),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            label,
            style: Theme.of(
              context,
            ).textTheme.titleSmall?.copyWith(fontWeight: FontWeight.w700),
          ),
          const SizedBox(height: 8),
          TextField(
            controller: controller,
            minLines: minLines,
            maxLines: minLines + 2,
            decoration: InputDecoration(hintText: 'Add $label'),
          ),
        ],
      ),
    );
  }
}
