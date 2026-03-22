import 'package:flutter/material.dart';

import '../app_controller.dart';
import '../theme/app_theme.dart';
import '../widgets/dala_scaffold.dart';

class CompanionPage extends StatefulWidget {
  const CompanionPage({super.key, required this.controller});

  final DalaAppController controller;

  @override
  State<CompanionPage> createState() => _CompanionPageState();
}

class _CompanionPageState extends State<CompanionPage> {
  final TextEditingController _textController = TextEditingController();

  @override
  void dispose() {
    _textController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: widget.controller,
      builder: (context, _) {
        return DalaScaffold(
          child: Column(
            children: [
              Padding(
                padding: const EdgeInsets.fromLTRB(20, 18, 20, 12),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Dala Companion',
                      style: Theme.of(context).textTheme.headlineSmall
                          ?.copyWith(fontWeight: FontWeight.w700),
                    ),
                    const SizedBox(height: 8),
                    Text(
                      widget.controller.isChatConnected
                          ? 'Connected to your live Dala conversation.'
                          : 'Preparing the secure chat connection to your backend.',
                      style: Theme.of(
                        context,
                      ).textTheme.bodyMedium?.copyWith(color: AppTheme.secondaryText),
                    ),
                    const SizedBox(height: 18),
                    Wrap(
                      spacing: 10,
                      runSpacing: 10,
                      children: [
                        _StatusPill(
                          label: widget.controller.isChatConnected
                              ? 'Connected'
                              : widget.controller.isCompanionLoading
                              ? 'Connecting'
                              : 'Offline',
                          color: widget.controller.isChatConnected
                              ? AppTheme.sage
                              : AppTheme.primaryText,
                        ),
                        ActionChip(
                          avatar: const Icon(Icons.refresh_rounded, size: 18),
                          label: const Text('Reconnect'),
                          onPressed: widget.controller.isCompanionLoading
                              ? null
                              : () => widget.controller.ensureCompanionReady(),
                        ),
                      ],
                    ),
                    if (widget.controller.errorMessage != null) ...[
                      const SizedBox(height: 14),
                      _CompanionError(message: widget.controller.errorMessage!),
                    ],
                    const SizedBox(height: 18),
                    SingleChildScrollView(
                      scrollDirection: Axis.horizontal,
                      child: Row(
                        children: ChatMode.values.map((mode) {
                          final isSelected = widget.controller.chatMode == mode;
                          return Padding(
                            padding: const EdgeInsets.only(right: 10),
                            child: ChoiceChip(
                              selected: isSelected,
                              label: Text(_modeLabel(mode)),
                              onSelected: (_) =>
                                  widget.controller.setChatMode(mode),
                            ),
                          );
                        }).toList(),
                      ),
                    ),
                  ],
                ),
              ),
              Expanded(
                child: ListView.builder(
                  padding: const EdgeInsets.fromLTRB(20, 8, 20, 16),
                  itemCount:
                      widget.controller.messages.length +
                      (widget.controller.isTyping ? 1 : 0),
                  itemBuilder: (context, index) {
                    final isTypingIndicator =
                        widget.controller.isTyping &&
                        index == widget.controller.messages.length;

                    if (isTypingIndicator) {
                      return const Align(
                        alignment: Alignment.centerLeft,
                        child: _TypingBubble(),
                      );
                    }

                    final message = widget.controller.messages[index];
                    final isUser = message.role == 'user';
                    return Align(
                      alignment: isUser
                          ? Alignment.centerRight
                          : Alignment.centerLeft,
                      child: Container(
                        constraints: const BoxConstraints(maxWidth: 320),
                        margin: const EdgeInsets.only(bottom: 12),
                        padding: const EdgeInsets.symmetric(
                          horizontal: 16,
                          vertical: 14,
                        ),
                        decoration: BoxDecoration(
                          color: isUser ? AppTheme.primaryText : Colors.white,
                          borderRadius: BorderRadius.circular(22),
                        ),
                        child: Text(
                          message.text,
                          style: Theme.of(context).textTheme.bodyMedium
                              ?.copyWith(
                                color: isUser ? Colors.white : AppTheme.primaryText,
                                height: 1.45,
                              ),
                        ),
                      ),
                    );
                  },
                ),
              ),
              Padding(
                padding: const EdgeInsets.fromLTRB(16, 0, 16, 16),
                child: Row(
                  children: [
                    Expanded(
                      child: TextField(
                        controller: _textController,
                        minLines: 1,
                        maxLines: 4,
                        textInputAction: TextInputAction.send,
                        onSubmitted: (_) => _handleSend(),
                        enabled: !widget.controller.isCompanionLoading,
                        decoration: const InputDecoration(
                          hintText: 'Type what is on your heart...',
                        ),
                      ),
                    ),
                    const SizedBox(width: 12),
                    FilledButton(
                      onPressed:
                          widget.controller.isSendingMessage ||
                              widget.controller.isCompanionLoading
                          ? null
                          : _handleSend,
                      style: FilledButton.styleFrom(
                        shape: const CircleBorder(),
                        padding: const EdgeInsets.all(16),
                      ),
                      child: const Icon(Icons.send_rounded),
                    ),
                  ],
                ),
              ),
            ],
          ),
        );
      },
    );
  }

  Future<void> _handleSend() async {
    final text = _textController.text;
    _textController.clear();
    await widget.controller.sendMessage(text);
  }

  String _modeLabel(ChatMode mode) {
    switch (mode) {
      case ChatMode.listen:
        return 'Listen';
      case ChatMode.reflect:
        return 'Reflect';
      case ChatMode.ground:
        return 'Ground';
    }
  }
}

class _StatusPill extends StatelessWidget {
  const _StatusPill({required this.label, required this.color});

  final String label;
  final Color color;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.12),
        borderRadius: BorderRadius.circular(999),
      ),
      child: Text(
        label,
        style: Theme.of(context).textTheme.bodySmall?.copyWith(
          color: color,
          fontWeight: FontWeight.w700,
        ),
      ),
    );
  }
}

class _CompanionError extends StatelessWidget {
  const _CompanionError({required this.message});

  final String message;

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: const Color(0xFFF8ECE6),
        borderRadius: BorderRadius.circular(18),
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Icon(Icons.warning_amber_rounded, color: AppTheme.primaryText),
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

class _TypingBubble extends StatelessWidget {
  const _TypingBubble();

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(22),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: List.generate(
          3,
          (index) => Padding(
            padding: const EdgeInsets.symmetric(horizontal: 2),
            child: Container(
              width: 7,
              height: 7,
              decoration: BoxDecoration(
                color: [AppTheme.subtle, AppTheme.sageHover, AppTheme.sage][index],
                shape: BoxShape.circle,
              ),
            ),
          ),
        ),
      ),
    );
  }
}
