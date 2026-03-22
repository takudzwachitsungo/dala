import 'package:flutter/material.dart';

import '../app_controller.dart';
import '../theme/app_theme.dart';
import '../widgets/dala_scaffold.dart';

class HomePage extends StatefulWidget {
  const HomePage({super.key, required this.controller});

  final DalaAppController controller;

  @override
  State<HomePage> createState() => _HomePageState();
}

class _HomePageState extends State<HomePage> {
  final TextEditingController _reflectionController = TextEditingController();

  @override
  void dispose() {
    _reflectionController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: widget.controller,
      builder: (context, _) {
        final verse = widget.controller.currentVerse;

        return DalaScaffold(
          child: SingleChildScrollView(
            padding: const EdgeInsets.fromLTRB(20, 18, 20, 120),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                if (widget.controller.isHomeLoading)
                  const Padding(
                    padding: EdgeInsets.only(bottom: 18),
                    child: LinearProgressIndicator(),
                  ),
                if (widget.controller.errorMessage != null)
                  Padding(
                    padding: const EdgeInsets.only(bottom: 18),
                    child: _InfoBanner(
                      message: widget.controller.errorMessage!,
                      tone: _BannerTone.warning,
                    ),
                  ),
                // Header
                Stack(
                  alignment: Alignment.center,
                  children: [
                    Column(
                      children: [
                        Text(
                          _greeting(),
                          style: Theme.of(context).textTheme.displaySmall?.copyWith(
                                color: AppTheme.primaryText,
                                fontWeight: FontWeight.w400,
                              ),
                        ),
                        const SizedBox(height: 8),
                        Text(
                          'Take a moment to arrive.',
                          style: Theme.of(context).textTheme.titleMedium?.copyWith(
                                color: AppTheme.secondaryText,
                                fontWeight: FontWeight.w400,
                              ),
                        ),
                      ],
                    ),
                    Positioned(
                      right: 0,
                      top: 0,
                      child: IconButton(
                        icon: const Icon(Icons.logout_rounded),
                        color: AppTheme.secondaryText,
                        onPressed: () {
                          // Implement logout or switch user later
                        },
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 48),

                // Mood Tracker Card
                Container(
                  padding: const EdgeInsets.symmetric(vertical: 32, horizontal: 24),
                  decoration: BoxDecoration(
                    color: Colors.white,
                    borderRadius: BorderRadius.circular(24),
                    boxShadow: const [
                      BoxShadow(
                        color: Color(0x08000000),
                        blurRadius: 20,
                        offset: Offset(0, 4),
                      ),
                    ],
                  ),
                  child: Column(
                    children: [
                      Text(
                        'HOW ARE YOU FEELING?',
                        style: Theme.of(context).textTheme.labelMedium?.copyWith(
                              color: AppTheme.secondaryText,
                              letterSpacing: 1.5,
                              fontWeight: FontWeight.w600,
                            ),
                      ),
                      const SizedBox(height: 32),
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: DalaAppController.moodOptions.map((mood) {
                          final isSelected =
                              mood.score == widget.controller.selectedMoodScore;
                          return GestureDetector(
                            onTap: () async {
                              await widget.controller.selectMood(mood.score);
                            },
                            behavior: HitTestBehavior.opaque,
                            child: Column(
                              mainAxisSize: MainAxisSize.min,
                              children: [
                                Container(
                                  width: 20,
                                  height: 20,
                                  decoration: BoxDecoration(
                                    shape: BoxShape.circle,
                                    color: isSelected
                                        ? AppTheme.sage
                                        : Colors.transparent,
                                    border: isSelected
                                        ? null
                                        : Border.all(
                                            color: AppTheme.secondaryText.withValues(alpha: 0.4),
                                            width: 1.5,
                                          ),
                                  ),
                                ),
                                const SizedBox(height: 12),
                                Text(
                                  mood.label,
                                  style: Theme.of(context)
                                      .textTheme
                                      .labelMedium
                                      ?.copyWith(
                                        color: isSelected
                                            ? AppTheme.primaryText
                                            : AppTheme.subtle,
                                        fontWeight: FontWeight.w500,
                                      ),
                                ),
                              ],
                            ),
                          );
                        }).toList(),
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 32),

                // Conditional Bible Verse Card
                if (verse.verse.isNotEmpty) ...[
                  Container(
                    width: double.infinity,
                    padding: const EdgeInsets.all(24),
                    decoration: BoxDecoration(
                      color: Colors.white,
                      borderRadius: BorderRadius.circular(24),
                      gradient: LinearGradient(
                        begin: Alignment.topLeft,
                        end: Alignment.bottomRight,
                        colors: [
                          Colors.white,
                          AppTheme.sage.withValues(alpha: 0.15)
                        ],
                      ),
                      boxShadow: const [
                        BoxShadow(
                          color: Color(0x08000000),
                          blurRadius: 20,
                          offset: Offset(0, 4),
                        ),
                      ],
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          'A word for this moment',
                          style: Theme.of(context).textTheme.labelMedium?.copyWith(
                                color: AppTheme.sage,
                                letterSpacing: 1.2,
                                fontWeight: FontWeight.w600,
                              ),
                        ),
                        const SizedBox(height: 16),
                        Text(
                          '"${verse.verse}"',
                          style: Theme.of(context).textTheme.titleLarge?.copyWith(
                                height: 1.35,
                                fontWeight: FontWeight.w500,
                              ),
                        ),
                        const SizedBox(height: 12),
                        Text(
                          verse.reference,
                          style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                                color: AppTheme.sage,
                                fontWeight: FontWeight.w600,
                              ),
                        ),
                        const SizedBox(height: 12),
                        Text(
                          verse.devotional,
                          style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                                color: AppTheme.secondaryText,
                                height: 1.5,
                              ),
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(height: 32),
                ],

                // Quick Actions
                Row(
                  children: [
                    Expanded(
                      child: _QuickActionCard(
                        icon: Icons.chat_bubble_outline_rounded,
                        title: 'Talk to Dala',
                        iconBgColor: const Color(0xFFF1F4EC),
                        iconColor: AppTheme.sage,
                        onTap: () =>
                            widget.controller.selectTab(AppTab.companion),
                      ),
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: _QuickActionCard(
                        icon: Icons.edit_outlined,
                        title: 'Reflect',
                        iconBgColor: const Color(0xFFFEF0E6),
                        iconColor: const Color(0xFFD97736),
                        onTap: () {}, // Handled by scrolling to reflect!
                      ),
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: _QuickActionCard(
                        icon: Icons.explore_outlined,
                        title: 'Explore',
                        iconBgColor: const Color(0xFFEDF2FE),
                        iconColor: const Color(0xFF3B68E5),
                        onTap: () => widget.controller.selectTab(AppTab.paths),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 64),

                // Reflect Text Input
                ValueListenableBuilder<TextEditingValue>(
                  valueListenable: _reflectionController,
                  builder: (context, value, _) {
                    final hasText = value.text.trim().isNotEmpty;
                    return Column(
                      crossAxisAlignment: CrossAxisAlignment.stretch,
                      children: [
                        TextField(
                          controller: _reflectionController,
                          minLines: 1,
                          maxLines: null,
                          textInputAction: TextInputAction.newline,
                          style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                                color: AppTheme.primaryText,
                                fontWeight: FontWeight.w400,
                              ),
                          decoration: InputDecoration(
                            hintText: 'How are you feeling right now?',
                            hintStyle:
                                Theme.of(context).textTheme.headlineSmall?.copyWith(
                                      color: AppTheme.subtle,
                                      fontWeight: FontWeight.w400,
                                    ),
                            border: InputBorder.none,
                            focusedBorder: InputBorder.none,
                            enabledBorder: InputBorder.none,
                            filled: false,
                            contentPadding: EdgeInsets.zero,
                          ),
                        ),
                        if (hasText) ...[
                          const SizedBox(height: 16),
                          Align(
                            alignment: Alignment.centerRight,
                            child: FilledButton(
                              onPressed: () async {
                                await widget.controller.addReflection(
                                  _reflectionController.text,
                                );
                                _reflectionController.clear();
                              },
                              child: const Text('Save entry'),
                            ),
                          ),
                        ],
                      ],
                    );
                  },
                ),
                const SizedBox(height: 160),

                // Recent Reflections
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text(
                      'RECENT REFLECTIONS',
                      style: Theme.of(context).textTheme.labelMedium?.copyWith(
                            color: AppTheme.secondaryText,
                            letterSpacing: 1.2,
                            fontWeight: FontWeight.w600,
                          ),
                    ),
                    Container(
                      padding: const EdgeInsets.symmetric(
                        horizontal: 12,
                        vertical: 6,
                      ),
                      decoration: BoxDecoration(
                        color: AppTheme.sage.withValues(alpha: 0.1),
                        borderRadius: BorderRadius.circular(12),
                      ),
                      child: Text(
                        '${widget.controller.reflections.length} entries',
                        style: Theme.of(context).textTheme.labelSmall?.copyWith(
                              color: AppTheme.sage,
                              fontWeight: FontWeight.w600,
                            ),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 32),

                if (widget.controller.reflections.isEmpty)
                  Padding(
                    padding: const EdgeInsets.symmetric(vertical: 24),
                    child: Center(
                      child: Text(
                        'Breathe in. Start writing.',
                        style: Theme.of(context).textTheme.titleLarge?.copyWith(
                              color: AppTheme.subtle,
                              fontStyle: FontStyle.italic,
                              fontWeight: FontWeight.w400,
                            ),
                      ),
                    ),
                  )
                else
                  ...widget.controller.reflections.take(5).map(
                        (entry) => Padding(
                          padding: const EdgeInsets.only(bottom: 16),
                          child: Container(
                            padding: const EdgeInsets.all(20),
                            decoration: BoxDecoration(
                              color: Colors.white,
                              borderRadius: BorderRadius.circular(20),
                              border: Border.all(
                                color: AppTheme.dividerBg.withValues(alpha: 0.5),
                              ),
                            ),
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Text(
                                  entry.note,
                                  style: Theme.of(context)
                                      .textTheme
                                      .bodyLarge
                                      ?.copyWith(height: 1.4),
                                ),
                                const SizedBox(height: 12),
                                Text(
                                  _formatDate(entry.createdAt),
                                  style: Theme.of(context)
                                      .textTheme
                                      .bodySmall
                                      ?.copyWith(color: AppTheme.secondaryText),
                                ),
                              ],
                            ),
                          ),
                        ),
                      ),
              ],
            ),
          ),
        );
      },
    );
  }

  String _greeting() {
    final hour = DateTime.now().hour;
    if (hour < 12) {
      return 'Good morning';
    } else if (hour < 17) {
      return 'Good afternoon';
    } else {
      return 'Good evening';
    }
  }

  String _formatDate(DateTime date) {
    final monthNames = [
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
    return '${monthNames[date.month - 1]} ${date.day}';
  }
}

enum _BannerTone { success, warning }

class _InfoBanner extends StatelessWidget {
  const _InfoBanner({required this.message, required this.tone});

  final String message;
  final _BannerTone tone;

  @override
  Widget build(BuildContext context) {
    final background = tone == _BannerTone.success
        ? AppTheme.subtle
        : const Color(0xFFF8ECE6);
    final foreground = tone == _BannerTone.success
        ? AppTheme.sage
        : AppTheme.primaryText;

    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: background,
        borderRadius: BorderRadius.circular(18),
      ),
      child: Row(
        children: [
          Icon(
            tone == _BannerTone.success
                ? Icons.cloud_done_rounded
                : Icons.info_outline_rounded,
            color: foreground,
          ),
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

class _QuickActionCard extends StatelessWidget {
  const _QuickActionCard({
    required this.icon,
    required this.title,
    required this.iconBgColor,
    required this.iconColor,
    required this.onTap,
  });

  final IconData icon;
  final String title;
  final Color iconBgColor;
  final Color iconColor;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(20),
      child: Container(
        padding: const EdgeInsets.symmetric(vertical: 20, horizontal: 8),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(20),
          boxShadow: const [
            BoxShadow(
              color: Color(0x06000000),
              blurRadius: 10,
              offset: Offset(0, 2),
            ),
          ],
        ),
        child: Column(
          children: [
            Container(
              width: 52,
              height: 52,
              decoration: BoxDecoration(
                color: iconBgColor,
                shape: BoxShape.circle,
              ),
              child: Icon(icon, color: iconColor, size: 24),
            ),
            const SizedBox(height: 16),
            Text(
              title,
              textAlign: TextAlign.center,
              style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                    fontWeight: FontWeight.w600,
                    color: AppTheme.primaryText,
                  ),
            ),
          ],
        ),
      ),
    );
  }
}
