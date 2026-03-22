import 'dart:math';

import 'package:flutter/foundation.dart';

enum AppTab { home, companion, paths, circles, profile }

enum ChatMode { listen, reflect, ground }

class AppUser {
  const AppUser({
    required this.name,
    required this.memberSince,
    required this.streakDays,
    required this.totalMoodEntries,
    required this.totalConversations,
    required this.milestoneCount,
    required this.isAnonymous,
  });

  final String name;
  final DateTime memberSince;
  final int streakDays;
  final int totalMoodEntries;
  final int totalConversations;
  final int milestoneCount;
  final bool isAnonymous;

  AppUser copyWith({
    String? name,
    DateTime? memberSince,
    int? streakDays,
    int? totalMoodEntries,
    int? totalConversations,
    int? milestoneCount,
    bool? isAnonymous,
  }) {
    return AppUser(
      name: name ?? this.name,
      memberSince: memberSince ?? this.memberSince,
      streakDays: streakDays ?? this.streakDays,
      totalMoodEntries: totalMoodEntries ?? this.totalMoodEntries,
      totalConversations: totalConversations ?? this.totalConversations,
      milestoneCount: milestoneCount ?? this.milestoneCount,
      isAnonymous: isAnonymous ?? this.isAnonymous,
    );
  }
}

class MoodOption {
  const MoodOption({
    required this.score,
    required this.label,
    required this.emoji,
    required this.description,
  });

  final int score;
  final String label;
  final String emoji;
  final String description;
}

class VerseMoment {
  const VerseMoment({
    required this.verse,
    required this.reference,
    required this.devotional,
  });

  final String verse;
  final String reference;
  final String devotional;
}

class ReflectionEntry {
  const ReflectionEntry({
    required this.note,
    required this.moodScore,
    required this.createdAt,
  });

  final String note;
  final int moodScore;
  final DateTime createdAt;
}

class MoodCheckin {
  const MoodCheckin({
    required this.score,
    required this.label,
    required this.createdAt,
  });

  final int score;
  final String label;
  final DateTime createdAt;
}

class ChatMessage {
  const ChatMessage({
    required this.id,
    required this.role,
    required this.text,
    required this.sentAt,
  });

  final String id;
  final String role;
  final String text;
  final DateTime sentAt;
}

class PathJourney {
  const PathJourney({
    required this.title,
    required this.subtitle,
    required this.duration,
    required this.focus,
  });

  final String title;
  final String subtitle;
  final String duration;
  final String focus;
}

class CircleGroup {
  const CircleGroup({
    required this.name,
    required this.description,
    required this.members,
    required this.energy,
  });

  final String name;
  final String description;
  final int members;
  final String energy;
}

class DalaAppController extends ChangeNotifier {
  DalaAppController() {
    _seedSessionData();
  }

  static const List<MoodOption> moodOptions = [
    MoodOption(
      score: 1,
      label: 'Heavy',
      emoji: '😔',
      description: 'A day that feels hard to carry.',
    ),
    MoodOption(
      score: 2,
      label: 'Tender',
      emoji: '😟',
      description: 'A little overwhelmed and needing gentleness.',
    ),
    MoodOption(
      score: 3,
      label: 'Steady',
      emoji: '🙂',
      description: 'Holding things together one step at a time.',
    ),
    MoodOption(
      score: 4,
      label: 'Bright',
      emoji: '😊',
      description: 'Feeling lighter and more hopeful.',
    ),
    MoodOption(
      score: 5,
      label: 'Grateful',
      emoji: '🤍',
      description: 'Sensing peace and noticing the good.',
    ),
  ];

  static const Map<int, VerseMoment> verseMoments = {
    1: VerseMoment(
      verse: 'The Lord is close to the brokenhearted.',
      reference: 'Psalm 34:18',
      devotional: 'You do not have to be strong first. God comes near before the healing feels complete.',
    ),
    2: VerseMoment(
      verse: 'Cast all your anxiety on Him because He cares for you.',
      reference: '1 Peter 5:7',
      devotional: 'Today can be small and honest. Even a whispered prayer still counts as reaching for hope.',
    ),
    3: VerseMoment(
      verse: 'Your word is a lamp to my feet and a light to my path.',
      reference: 'Psalm 119:105',
      devotional: 'Steady days matter too. Faithfulness often looks like taking the next kind step, not seeing the whole road.',
    ),
    4: VerseMoment(
      verse: 'May the God of hope fill you with all joy and peace.',
      reference: 'Romans 15:13',
      devotional: 'Let hope have room today. Notice what is growing, even if it still feels new and fragile.',
    ),
    5: VerseMoment(
      verse: 'Give thanks in all circumstances.',
      reference: '1 Thessalonians 5:18',
      devotional: 'Gratitude does not ignore pain. It simply lets grace be visible beside it.',
    ),
  };

  final List<PathJourney> paths = const [
    PathJourney(
      title: 'Quieting Anxiety',
      subtitle: 'Breath prayers, grounding, and gentle reflection.',
      duration: '7 days',
      focus: 'Calm your body and mind',
    ),
    PathJourney(
      title: 'Rebuilding Hope',
      subtitle: 'Small prompts for when joy feels far away.',
      duration: '14 days',
      focus: 'Find language for hope again',
    ),
    PathJourney(
      title: 'Rest and Recovery',
      subtitle: 'A slower rhythm for tired hearts and minds.',
      duration: '10 days',
      focus: 'Recover emotionally and spiritually',
    ),
  ];

  final List<CircleGroup> circles = const [
    CircleGroup(
      name: 'Gentle Evenings',
      description: 'A quiet space for people winding down after demanding days.',
      members: 42,
      energy: 'Soft and supportive',
    ),
    CircleGroup(
      name: 'Young Adults Prayer Circle',
      description: 'Short reflections, prayer requests, and honest check-ins.',
      members: 87,
      energy: 'Warm and open',
    ),
    CircleGroup(
      name: 'Starting Over',
      description: 'For anyone navigating change, grief, or a new season.',
      members: 58,
      energy: 'Courageous and honest',
    ),
  ];

  AppUser? _user;
  AppTab _selectedTab = AppTab.home;
  ChatMode _chatMode = ChatMode.listen;
  bool _isCreatingSession = false;
  bool _isSendingMessage = false;
  int _selectedMoodScore = 3;
  final List<MoodCheckin> _moodHistory = [];
  final List<ReflectionEntry> _reflections = [];
  final List<ChatMessage> _messages = [];
  final List<String> _safetyPlan = const [
    'Text my sister or closest friend when the day feels too heavy.',
    'Step outside and name five things I can see before reacting.',
    'Use a short breath prayer: "Jesus, hold me steady."',
    'If I feel unsafe, contact local emergency support immediately.',
  ];

  bool get hasSession => _user != null;
  AppUser? get user => _user;
  AppTab get selectedTab => _selectedTab;
  ChatMode get chatMode => _chatMode;
  bool get isCreatingSession => _isCreatingSession;
  bool get isSendingMessage => _isSendingMessage;
  int get selectedMoodScore => _selectedMoodScore;
  List<MoodCheckin> get moodHistory => List.unmodifiable(_moodHistory);
  List<ReflectionEntry> get reflections => List.unmodifiable(_reflections);
  List<ChatMessage> get messages => List.unmodifiable(_messages);
  List<String> get safetyPlan => List.unmodifiable(_safetyPlan);
  VerseMoment get currentVerse => verseMoments[_selectedMoodScore] ?? verseMoments[3]!;

  Future<void> continueAnonymously() async {
    if (_isCreatingSession) {
      return;
    }

    _isCreatingSession = true;
    notifyListeners();

    await Future<void>.delayed(const Duration(milliseconds: 700));

    final randomId = 100000 + Random().nextInt(899999);
    _user = AppUser(
      name: 'anonymous_$randomId',
      memberSince: DateTime.now().subtract(const Duration(days: 18)),
      streakDays: 6,
      totalMoodEntries: _moodHistory.length,
      totalConversations: 12,
      milestoneCount: 4,
      isAnonymous: true,
    );
    _seedChatMessages();

    _isCreatingSession = false;
    notifyListeners();
  }

  void selectTab(AppTab tab) {
    if (_selectedTab == tab) {
      return;
    }
    _selectedTab = tab;
    notifyListeners();
  }

  void setChatMode(ChatMode mode) {
    if (_chatMode == mode) {
      return;
    }
    _chatMode = mode;
    notifyListeners();
  }

  void selectMood(int score) {
    _selectedMoodScore = score;

    final option = moodOptions.firstWhere(
      (item) => item.score == score,
      orElse: () => moodOptions[2],
    );

    _moodHistory.insert(
      0,
      MoodCheckin(
        score: option.score,
        label: option.label,
        createdAt: DateTime.now(),
      ),
    );

    if (_user != null) {
      _user = _user!.copyWith(
        totalMoodEntries: _moodHistory.length,
        streakDays: max(_user!.streakDays, 1),
      );
    }

    notifyListeners();
  }

  void addReflection(String note) {
    if (note.trim().isEmpty) {
      return;
    }

    _reflections.insert(
      0,
      ReflectionEntry(
        note: note.trim(),
        moodScore: _selectedMoodScore,
        createdAt: DateTime.now(),
      ),
    );

    notifyListeners();
  }

  Future<void> sendMessage(String text) async {
    final trimmed = text.trim();
    if (trimmed.isEmpty || _isSendingMessage) {
      return;
    }

    _messages.add(
      ChatMessage(
        id: DateTime.now().microsecondsSinceEpoch.toString(),
        role: 'user',
        text: trimmed,
        sentAt: DateTime.now(),
      ),
    );
    _isSendingMessage = true;
    notifyListeners();

    await Future<void>.delayed(const Duration(milliseconds: 900));

    _messages.add(
      ChatMessage(
        id: DateTime.now().microsecondsSinceEpoch.toString(),
        role: 'assistant',
        text: _buildAssistantReply(trimmed),
        sentAt: DateTime.now(),
      ),
    );
    _isSendingMessage = false;
    notifyListeners();
  }

  void logout() {
    _user = null;
    _selectedTab = AppTab.home;
    _chatMode = ChatMode.listen;
    _selectedMoodScore = 3;
    _seedSessionData();
    notifyListeners();
  }

  void _seedSessionData() {
    _moodHistory
      ..clear()
      ..addAll([
        MoodCheckin(score: 4, label: 'Bright', createdAt: DateTime.now().subtract(const Duration(days: 0))),
        MoodCheckin(score: 3, label: 'Steady', createdAt: DateTime.now().subtract(const Duration(days: 1))),
        MoodCheckin(score: 2, label: 'Tender', createdAt: DateTime.now().subtract(const Duration(days: 2))),
        MoodCheckin(score: 4, label: 'Bright', createdAt: DateTime.now().subtract(const Duration(days: 3))),
        MoodCheckin(score: 5, label: 'Grateful', createdAt: DateTime.now().subtract(const Duration(days: 4))),
        MoodCheckin(score: 3, label: 'Steady', createdAt: DateTime.now().subtract(const Duration(days: 5))),
        MoodCheckin(score: 2, label: 'Tender', createdAt: DateTime.now().subtract(const Duration(days: 6))),
      ]);

    _reflections
      ..clear()
      ..addAll([
        ReflectionEntry(
          note: 'I felt more grounded after taking a short walk and praying before dinner.',
          moodScore: 4,
          createdAt: DateTime.now().subtract(const Duration(hours: 8)),
        ),
        ReflectionEntry(
          note: 'Today was tender. I still showed up, and that matters.',
          moodScore: 2,
          createdAt: DateTime.now().subtract(const Duration(days: 1, hours: 3)),
        ),
      ]);

    _messages.clear();
  }

  void _seedChatMessages() {
    if (_messages.isNotEmpty) {
      return;
    }

    _messages.add(
      ChatMessage(
        id: 'welcome-message',
        role: 'assistant',
        text: 'Hi, I\'m Dala. I\'m here to listen with gentleness. What feels most present for you today?',
        sentAt: DateTime.now(),
      ),
    );
  }

  String _buildAssistantReply(String text) {
    final moodLabel = moodOptions
        .firstWhere(
          (item) => item.score == _selectedMoodScore,
          orElse: () => moodOptions[2],
        )
        .label
        .toLowerCase();

    switch (_chatMode) {
      case ChatMode.listen:
        return 'Thank you for sharing that. It sounds like today feels $moodLabel in a very real way, and you do not have to carry it alone. What part of this feels heaviest right now?';
      case ChatMode.reflect:
        return 'I notice there may be a pattern between what you said and how your body has been holding the day. If we slowed it down, what do you think this moment is asking for: rest, honesty, or reassurance?';
      case ChatMode.ground:
        return 'Let\'s take one steady step together. Plant both feet on the floor, loosen your shoulders, and take one slow breath in for four counts and out for six. Stay with that for a moment and tell me what shifts, even slightly.';
    }
  }
}
