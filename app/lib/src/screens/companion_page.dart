import 'package:flutter/material.dart';

import '../app_controller.dart';
import '../theme/app_theme.dart';
import '../widgets/dala_scaffold.dart';

class CompanionPage extends StatefulWidget {
  const CompanionPage({
    super.key,
    required this.controller,
  });

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
                      style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                            fontWeight: FontWeight.w700,
                          ),
                    ),
                    const SizedBox(height: 8),
                    Text(
                      'A mobile preview of the chat flow. The UI is ready for real backend wiring next.',
                      style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                            color: AppTheme.muted,
                          ),
                    ),
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
                              onSelected: (_) => widget.controller.setChatMode(mode),
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
                  itemCount: widget.controller.messages.length +
                      (widget.controller.isSendingMessage ? 1 : 0),
                  itemBuilder: (context, index) {
                    final isTypingIndicator =
                        widget.controller.isSendingMessage &&
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
                      alignment:
                          isUser ? Alignment.centerRight : Alignment.centerLeft,
                      child: Container(
                        constraints: const BoxConstraints(maxWidth: 320),
                        margin: const EdgeInsets.only(bottom: 12),
                        padding: const EdgeInsets.symmetric(
                          horizontal: 16,
                          vertical: 14,
                        ),
                        decoration: BoxDecoration(
                          color: isUser ? AppTheme.ink : Colors.white,
                          borderRadius: BorderRadius.circular(22),
                        ),
                        child: Text(
                          message.text,
                          style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                                color: isUser ? Colors.white : AppTheme.ink,
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
                        decoration: const InputDecoration(
                          hintText: 'Type what is on your heart...',
                        ),
                      ),
                    ),
                    const SizedBox(width: 12),
                    FilledButton(
                      onPressed: widget.controller.isSendingMessage
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
                color: [
                  AppTheme.sageSoft,
                  AppTheme.gold,
                  AppTheme.sage,
                ][index],
                shape: BoxShape.circle,
              ),
            ),
          ),
        ),
      ),
    );
  }
}
