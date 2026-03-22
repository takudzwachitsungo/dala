import 'dart:async';
import 'dart:math';

import 'package:flutter/foundation.dart';

import 'data/api_client.dart';
import 'data/chat_socket_client.dart';
import 'data/session_store.dart';

enum AppTab { home, companion, paths, circles, profile }

enum ChatMode { listen, reflect, ground }

class AppUser {
  const AppUser({
    required this.id,
    required this.name,
    required this.memberSince,
    required this.streakDays,
    required this.totalMoodEntries,
    required this.totalConversations,
    required this.milestoneCount,
    required this.isAnonymous,
  });

  final String id;
  final String name;
  final DateTime memberSince;
  final int streakDays;
  final int totalMoodEntries;
  final int totalConversations;
  final int milestoneCount;
  final bool isAnonymous;

  factory AppUser.fromProfileJson(Map<String, dynamic> json) {
    return AppUser(
      id: '${json['id']}',
      name: '${json['username'] ?? 'friend'}',
      memberSince: DateTime.tryParse('${json['created_at']}') ?? DateTime.now(),
      streakDays: (json['streak_days'] as num?)?.toInt() ?? 0,
      totalMoodEntries: (json['total_mood_entries'] as num?)?.toInt() ?? 0,
      totalConversations: (json['total_conversations'] as num?)?.toInt() ?? 0,
      milestoneCount: (json['milestone_count'] as num?)?.toInt() ?? 0,
      isAnonymous: json['is_anonymous'] == true,
    );
  }

  AppUser copyWith({
    String? id,
    String? name,
    DateTime? memberSince,
    int? streakDays,
    int? totalMoodEntries,
    int? totalConversations,
    int? milestoneCount,
    bool? isAnonymous,
  }) {
    return AppUser(
      id: id ?? this.id,
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

  factory VerseMoment.fromJson(Map<String, dynamic> json) {
    return VerseMoment(
      verse: '${json['verse'] ?? ''}',
      reference: '${json['reference'] ?? ''}',
      devotional: '${json['devotional'] ?? ''}',
    );
  }
}

class ReflectionEntry {
  const ReflectionEntry({
    required this.id,
    required this.note,
    required this.moodScore,
    required this.createdAt,
  });

  final String id;
  final String note;
  final int moodScore;
  final DateTime createdAt;

  factory ReflectionEntry.fromMoodJson(Map<String, dynamic> json) {
    return ReflectionEntry(
      id: '${json['id']}',
      note: '${json['notes'] ?? ''}',
      moodScore: DalaAppController._normalizeMoodScore(
        (json['mood_score'] as num?)?.toInt() ?? 3,
      ),
      createdAt: DateTime.tryParse('${json['created_at']}') ?? DateTime.now(),
    );
  }
}

class MoodCheckin {
  const MoodCheckin({
    required this.id,
    required this.score,
    required this.label,
    required this.createdAt,
    this.note,
  });

  final String id;
  final int score;
  final String label;
  final DateTime createdAt;
  final String? note;

  factory MoodCheckin.fromJson(Map<String, dynamic> json) {
    final score = DalaAppController._normalizeMoodScore(
      (json['mood_score'] as num?)?.toInt() ?? 3,
    );
    return MoodCheckin(
      id: '${json['id']}',
      score: score,
      label: _moodLabel(score),
      createdAt: DateTime.tryParse('${json['created_at']}') ?? DateTime.now(),
      note: json['notes'] as String?,
    );
  }
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

  factory ChatMessage.fromJson(Map<String, dynamic> json) {
    return ChatMessage(
      id: '${json['id']}',
      role: '${json['role'] ?? 'assistant'}',
      text: '${json['content'] ?? ''}',
      sentAt: DateTime.tryParse('${json['created_at']}') ?? DateTime.now(),
    );
  }

  ChatMessage copyWith({
    String? id,
    String? role,
    String? text,
    DateTime? sentAt,
  }) {
    return ChatMessage(
      id: id ?? this.id,
      role: role ?? this.role,
      text: text ?? this.text,
      sentAt: sentAt ?? this.sentAt,
    );
  }
}

class PathJourney {
  const PathJourney({
    required this.id,
    required this.title,
    required this.category,
    required this.difficulty,
    required this.duration,
    required this.stepCount,
    required this.enrollmentCount,
    this.isEnrolled = false,
  });

  final String id;
  final String title;
  final String category;
  final String difficulty;
  final int? duration;
  final int stepCount;
  final int enrollmentCount;
  final bool isEnrolled;

  factory PathJourney.fromJson(Map<String, dynamic> json) {
    return PathJourney(
      id: '${json['id']}',
      title: '${json['name'] ?? 'Untitled path'}',
      category: '${json['category'] ?? 'growth'}',
      difficulty: '${json['difficulty'] ?? 'beginner'}',
      duration: (json['estimated_duration'] as num?)?.toInt(),
      stepCount: (json['step_count'] as num?)?.toInt() ?? 0,
      enrollmentCount: (json['enrollment_count'] as num?)?.toInt() ?? 0,
      isEnrolled: json['user_progress'] != null,
    );
  }

  PathJourney copyWith({bool? isEnrolled, int? enrollmentCount}) {
    return PathJourney(
      id: id,
      title: title,
      category: category,
      difficulty: difficulty,
      duration: duration,
      stepCount: stepCount,
      enrollmentCount: enrollmentCount ?? this.enrollmentCount,
      isEnrolled: isEnrolled ?? this.isEnrolled,
    );
  }
}

class CircleGroup {
  const CircleGroup({
    required this.id,
    required this.name,
    required this.topic,
    required this.description,
    required this.members,
    required this.postCount,
    this.icon,
    this.isMember = false,
  });

  final String id;
  final String name;
  final String topic;
  final String description;
  final int members;
  final int postCount;
  final String? icon;
  final bool isMember;

  factory CircleGroup.fromJson(Map<String, dynamic> json) {
    return CircleGroup(
      id: '${json['id']}',
      name: '${json['name'] ?? 'Unnamed circle'}',
      topic: '${json['topic'] ?? 'support'}',
      description: '${json['description'] ?? ''}',
      members: (json['member_count'] as num?)?.toInt() ?? 0,
      postCount: (json['post_count'] as num?)?.toInt() ?? 0,
      icon: json['icon'] as String?,
      isMember: json['is_member'] == true,
    );
  }

  CircleGroup copyWith({bool? isMember, int? members}) {
    return CircleGroup(
      id: id,
      name: name,
      topic: topic,
      description: description,
      members: members ?? this.members,
      postCount: postCount,
      icon: icon,
      isMember: isMember ?? this.isMember,
    );
  }
}

class SafetyPlanData {
  const SafetyPlanData({
    this.warningSigns = const [],
    this.internalCoping = const [],
    this.socialContacts = const [],
    this.peopleToAsk = const [],
    this.professionals = const [],
    this.emergencyContacts = const [],
    this.safeEnvironment,
    this.reasonsToLive = const [],
  });

  final List<String> warningSigns;
  final List<String> internalCoping;
  final List<String> socialContacts;
  final List<String> peopleToAsk;
  final List<String> professionals;
  final List<String> emergencyContacts;
  final String? safeEnvironment;
  final List<String> reasonsToLive;

  factory SafetyPlanData.fromJson(Map<String, dynamic> json) {
    return SafetyPlanData(
      warningSigns: _asStringList(json['warning_signs']),
      internalCoping: _asStringList(json['internal_coping']),
      socialContacts: _asStringList(json['social_contacts']),
      peopleToAsk: _asStringList(json['people_to_ask']),
      professionals: _asStringList(json['professionals']),
      emergencyContacts: _asStringList(json['emergency_contacts']),
      safeEnvironment: json['safe_environment'] as String?,
      reasonsToLive: _asStringList(json['reasons_to_live']),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'warning_signs': warningSigns,
      'internal_coping': internalCoping,
      'social_contacts': socialContacts,
      'people_to_ask': peopleToAsk,
      'professionals': professionals,
      'emergency_contacts': emergencyContacts,
      'safe_environment': safeEnvironment,
      'reasons_to_live': reasonsToLive,
    };
  }
}

class DalaAppController extends ChangeNotifier {
  DalaAppController({DalaApiClient? apiClient, SessionStore? sessionStore})
    : _apiClient = apiClient ?? DalaApiClient(),
      _sessionStore = sessionStore ?? SessionStore() {
    _initialize();
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

  final DalaApiClient _apiClient;
  final SessionStore _sessionStore;

  ChatSocketClient? _chatSocketClient;
  String? _token;
  String? _conversationId;
  String? _streamingMessageId;

  AppUser? _user;
  AppTab _selectedTab = AppTab.home;
  ChatMode _chatMode = ChatMode.listen;

  bool _isBootstrapping = true;
  bool _isCreatingSession = false;
  bool _isHomeLoading = false;
  bool _isPathsLoading = false;
  bool _isCirclesLoading = false;
  bool _isCompanionLoading = false;
  bool _isSendingMessage = false;
  bool _isTyping = false;
  bool _isChatConnected = false;
  bool _isSavingSafetyPlan = false;

  int _selectedMoodScore = 3;
  VerseMoment? _currentVerse;
  SafetyPlanData _safetyPlan = const SafetyPlanData();

  final List<MoodCheckin> _moodHistory = [];
  final List<ReflectionEntry> _reflections = [];
  final List<ChatMessage> _messages = [];
  final List<PathJourney> _paths = [];
  final List<CircleGroup> _circles = [];

  String? _errorMessage;

  bool get hasSession => _token != null && _user != null;
  bool get isBootstrapping => _isBootstrapping;
  bool get isCreatingSession => _isCreatingSession;
  bool get isHomeLoading => _isHomeLoading;
  bool get isPathsLoading => _isPathsLoading;
  bool get isCirclesLoading => _isCirclesLoading;
  bool get isCompanionLoading => _isCompanionLoading;
  bool get isSendingMessage => _isSendingMessage;
  bool get isTyping => _isTyping;
  bool get isChatConnected => _isChatConnected;
  bool get isSavingSafetyPlan => _isSavingSafetyPlan;
  int get selectedMoodScore => _selectedMoodScore;
  AppUser? get user => _user;
  AppTab get selectedTab => _selectedTab;
  ChatMode get chatMode => _chatMode;
  VerseMoment get currentVerse =>
      _currentVerse ??
      const VerseMoment(verse: '', reference: '', devotional: '');
  SafetyPlanData get safetyPlan => _safetyPlan;
  List<MoodCheckin> get moodHistory => List.unmodifiable(_moodHistory);
  List<ReflectionEntry> get reflections => List.unmodifiable(_reflections);
  List<ChatMessage> get messages => List.unmodifiable(_messages);
  List<PathJourney> get paths => List.unmodifiable(_paths);
  List<CircleGroup> get circles => List.unmodifiable(_circles);
  String? get errorMessage => _errorMessage;

  Future<void> _initialize() async {
    _isBootstrapping = true;
    notifyListeners();

    final savedToken = await _sessionStore.readToken();
    if (savedToken == null || savedToken.isEmpty) {
      _isBootstrapping = false;
      notifyListeners();
      return;
    }

    _token = savedToken;

    try {
      await _loadAuthenticatedData(connectChat: false);
    } catch (error) {
      await _resetSession();
      _setError(_describeError(error));
    } finally {
      _isBootstrapping = false;
      notifyListeners();
    }
  }

  Future<void> continueAnonymously() async {
    if (_isCreatingSession) {
      return;
    }

    _isCreatingSession = true;
    _clearError();
    notifyListeners();

    try {
      final response = await _apiClient.createAnonymousSession();
      _token = response['access_token'] as String?;
      if (_token == null || _token!.isEmpty) {
        throw ApiException('No access token returned from backend.');
      }

      await _sessionStore.writeToken(_token!);
      await _loadAuthenticatedData(connectChat: false);
    } catch (error) {
      await _resetSession();
      _setError(_describeError(error));
    } finally {
      _isCreatingSession = false;
      notifyListeners();
    }
  }

  Future<void> selectTab(AppTab tab) async {
    if (_selectedTab != tab) {
      _selectedTab = tab;
      notifyListeners();
    }

    switch (tab) {
      case AppTab.home:
        if (hasSession && _moodHistory.isEmpty) {
          await refreshHome();
        }
        break;
      case AppTab.companion:
        if (hasSession) {
          await ensureCompanionReady();
        }
        break;
      case AppTab.paths:
        if (hasSession && _paths.isEmpty) {
          await loadPaths();
        }
        break;
      case AppTab.circles:
        if (hasSession && _circles.isEmpty) {
          await loadCircles();
        }
        break;
      case AppTab.profile:
        if (hasSession && _user != null && _user!.totalMoodEntries == 0) {
          await refreshHome();
        }
        break;
    }
  }

  void setChatMode(ChatMode mode) {
    if (_chatMode == mode) {
      return;
    }
    _chatMode = mode;
    notifyListeners();
  }

  Future<void> refreshHome() async {
    if (!hasSession || _token == null) {
      return;
    }

    _isHomeLoading = true;
    _clearError();
    notifyListeners();

    try {
      final profileJson = await _apiClient.getProfile(_token!);
      final moodHistoryJson = await _apiClient.getMoodHistory(
        _token!,
        days: 30,
      );

      _user = AppUser.fromProfileJson(profileJson);
      _applyMoodHistory(moodHistoryJson);
      await _loadVerseForScore(_selectedMoodScore);
      final safetyPlanJson = await _apiClient.getSafetyPlan(_token!);
      _safetyPlan = SafetyPlanData.fromJson(safetyPlanJson);
    } catch (error) {
      _setError(_describeError(error));
    } finally {
      _isHomeLoading = false;
      notifyListeners();
    }
  }

  Future<void> selectMood(int score) async {
    if (!hasSession || _token == null) {
      return;
    }

    _selectedMoodScore = score;
    _clearError();
    notifyListeners();

    try {
      final response = await _apiClient.logMood(_token!, moodScore: score);
      _prependMoodEntry(MoodCheckin.fromJson(response));
      await _loadVerseForScore(score);
      await _refreshProfileOnly();
    } catch (error) {
      _setError(_describeError(error));
    } finally {
      notifyListeners();
    }
  }

  Future<void> addReflection(String note) async {
    if (!hasSession || _token == null || note.trim().isEmpty) {
      return;
    }

    _clearError();
    notifyListeners();

    try {
      final response = await _apiClient.logMood(
        _token!,
        moodScore: _selectedMoodScore,
        notes: note.trim(),
      );
      _prependMoodEntry(MoodCheckin.fromJson(response));
      _prependReflection(
        ReflectionEntry.fromMoodJson({...response, 'notes': note.trim()}),
      );
      await _refreshProfileOnly();
    } catch (error) {
      _setError(_describeError(error));
    } finally {
      notifyListeners();
    }
  }

  Future<void> ensureCompanionReady() async {
    if (!hasSession || _token == null || _isCompanionLoading) {
      return;
    }

    _isCompanionLoading = true;
    _clearError();
    notifyListeners();

    try {
      await _ensureConversation();
      await _connectChatSocket();
    } catch (error) {
      _setError(_describeError(error));
    } finally {
      _isCompanionLoading = false;
      notifyListeners();
    }
  }

  Future<void> sendMessage(String text) async {
    final trimmed = text.trim();
    if (trimmed.isEmpty || _token == null) {
      return;
    }

    if (!_isChatConnected || _chatSocketClient == null) {
      await ensureCompanionReady();
    }

    if (!_isChatConnected || _chatSocketClient == null) {
      _setError('Chat is not connected yet. Please try again.');
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
    _clearError();
    notifyListeners();

    try {
      _chatSocketClient!.sendMessage(text: trimmed, mode: _chatMode.name);
    } catch (error) {
      _isSendingMessage = false;
      _setError(_describeError(error));
      notifyListeners();
    }
  }

  Future<void> loadPaths() async {
    if (!hasSession || _token == null || _isPathsLoading) {
      return;
    }

    _isPathsLoading = true;
    _clearError();
    notifyListeners();

    try {
      final response = await _apiClient.getPaths(_token!);
      _paths
        ..clear()
        ..addAll(
          response.whereType<Map<String, dynamic>>().map(PathJourney.fromJson),
        );
    } catch (error) {
      _setError(_describeError(error));
    } finally {
      _isPathsLoading = false;
      notifyListeners();
    }
  }

  Future<void> enrollInPath(String pathId) async {
    if (!hasSession || _token == null) {
      return;
    }

    _clearError();
    notifyListeners();

    try {
      await _apiClient.enrollInPath(_token!, pathId);
      final index = _paths.indexWhere((item) => item.id == pathId);
      if (index != -1) {
        final path = _paths[index];
        _paths[index] = path.copyWith(
          isEnrolled: true,
          enrollmentCount: path.enrollmentCount + 1,
        );
      }
    } catch (error) {
      _setError(_describeError(error));
    } finally {
      notifyListeners();
    }
  }

  Future<void> loadCircles() async {
    if (!hasSession || _token == null || _isCirclesLoading) {
      return;
    }

    _isCirclesLoading = true;
    _clearError();
    notifyListeners();

    try {
      final response = await _apiClient.getCircles(_token!);
      _circles
        ..clear()
        ..addAll(
          response.whereType<Map<String, dynamic>>().map(CircleGroup.fromJson),
        );
    } catch (error) {
      _setError(_describeError(error));
    } finally {
      _isCirclesLoading = false;
      notifyListeners();
    }
  }

  Future<void> toggleCircleMembership(String circleId, bool join) async {
    if (!hasSession || _token == null) {
      return;
    }

    _clearError();
    notifyListeners();

    try {
      if (join) {
        await _apiClient.joinCircle(_token!, circleId);
      } else {
        await _apiClient.leaveCircle(_token!, circleId);
      }

      final index = _circles.indexWhere((item) => item.id == circleId);
      if (index != -1) {
        final circle = _circles[index];
        _circles[index] = circle.copyWith(
          isMember: join,
          members: max(0, circle.members + (join ? 1 : -1)),
        );
      }
    } catch (error) {
      _setError(_describeError(error));
    } finally {
      notifyListeners();
    }
  }

  Future<void> saveSafetyPlan(SafetyPlanData data) async {
    if (!hasSession || _token == null || _isSavingSafetyPlan) {
      return;
    }

    _isSavingSafetyPlan = true;
    _clearError();
    notifyListeners();

    try {
      final response = await _apiClient.updateSafetyPlan(
        _token!,
        data.toJson(),
      );
      _safetyPlan = SafetyPlanData.fromJson(response);
    } catch (error) {
      _setError(_describeError(error));
    } finally {
      _isSavingSafetyPlan = false;
      notifyListeners();
    }
  }

  Future<void> logout() async {
    await _resetSession();
    notifyListeners();
  }

  @override
  void dispose() {
    _chatSocketClient?.disconnect();
    super.dispose();
  }

  Future<void> _loadAuthenticatedData({required bool connectChat}) async {
    if (_token == null) {
      return;
    }

    final profileJson = await _apiClient.getProfile(_token!);
    _user = AppUser.fromProfileJson(profileJson);

    final moodHistoryJson = await _apiClient.getMoodHistory(_token!, days: 30);
    _applyMoodHistory(moodHistoryJson);

    final safetyPlanJson = await _apiClient.getSafetyPlan(_token!);
    _safetyPlan = SafetyPlanData.fromJson(safetyPlanJson);

    await Future.wait([
      loadPaths(),
      loadCircles(),
      _loadVerseForScore(_selectedMoodScore),
    ]);

    if (connectChat) {
      await ensureCompanionReady();
    }
  }

  Future<void> _refreshProfileOnly() async {
    if (_token == null) {
      return;
    }
    final profileJson = await _apiClient.getProfile(_token!);
    _user = AppUser.fromProfileJson(profileJson);
  }

  Future<void> _ensureConversation() async {
    if (_token == null) {
      return;
    }

    if (_conversationId == null) {
      final conversations = await _apiClient.getConversations(
        _token!,
        limit: 1,
      );

      Map<String, dynamic>? conversation;
      if (conversations.isNotEmpty) {
        final first = conversations.first;
        if (first is Map<String, dynamic> && first['is_active'] == true) {
          conversation = first;
        }
      }

      conversation ??= await _apiClient.createConversation(
        _token!,
        mode: _chatMode.name,
      );

      _conversationId = '${conversation['id']}';
    }

    final history = await _apiClient.getConversationMessages(
      _token!,
      _conversationId!,
      limit: 100,
    );

    _messages
      ..clear()
      ..addAll(
        history.whereType<Map<String, dynamic>>().map(ChatMessage.fromJson),
      );

    if (_messages.isEmpty) {
      _messages.add(
        ChatMessage(
          id: 'dala-welcome',
          role: 'assistant',
          text:
              'Hi, I\'m Dala. I\'m here to listen with gentleness. What feels most present for you today?',
          sentAt: DateTime.now(),
        ),
      );
    }
  }

  Future<void> _connectChatSocket() async {
    if (_token == null || _conversationId == null) {
      return;
    }

    final uri = _apiClient.webSocketUri(
      token: _token!,
      conversationId: _conversationId!,
    );

    _chatSocketClient ??= ChatSocketClient(uri: uri);
    if (_chatSocketClient!.uri != uri) {
      _chatSocketClient = ChatSocketClient(uri: uri);
    }

    await _chatSocketClient!.connect(
      onMessage: _handleSocketMessage,
      onError: (error) {
        _isChatConnected = false;
        _isTyping = false;
        _isSendingMessage = false;
        _setError(_describeError(error));
        notifyListeners();
      },
      onDone: () {
        _isChatConnected = false;
        _isTyping = false;
        _isSendingMessage = false;
        notifyListeners();
      },
    );
  }

  void _handleSocketMessage(Map<String, dynamic> message) {
    final type = message['type'] as String? ?? '';

    switch (type) {
      case 'connected':
        _isChatConnected = true;
        break;
      case 'typing':
        _isTyping = message['status'] == true;
        break;
      case 'chunk':
        final chunk = message['content'] as String? ?? '';
        if (_streamingMessageId == null) {
          _streamingMessageId =
              'stream-${DateTime.now().microsecondsSinceEpoch.toString()}';
          _messages.add(
            ChatMessage(
              id: _streamingMessageId!,
              role: 'assistant',
              text: chunk,
              sentAt: DateTime.now(),
            ),
          );
        } else {
          final index = _messages.indexWhere(
            (item) => item.id == _streamingMessageId,
          );
          if (index != -1) {
            final existing = _messages[index];
            _messages[index] = existing.copyWith(text: existing.text + chunk);
          }
        }
        break;
      case 'complete':
        _isTyping = false;
        _isSendingMessage = false;
        _streamingMessageId = null;
        break;
      case 'error':
        _isTyping = false;
        _isSendingMessage = false;
        _streamingMessageId = null;
        _setError('${message['message'] ?? 'Chat request failed.'}');
        break;
      default:
        break;
    }

    notifyListeners();
  }

  void _applyMoodHistory(Map<String, dynamic> moodHistoryJson) {
    final entries = (moodHistoryJson['entries'] as List<dynamic>? ?? [])
        .whereType<Map<String, dynamic>>()
        .map(MoodCheckin.fromJson)
        .toList();

    _moodHistory
      ..clear()
      ..addAll(entries);

    _reflections
      ..clear()
      ..addAll(
        entries
            .where((entry) => (entry.note ?? '').trim().isNotEmpty)
            .map(
              (entry) => ReflectionEntry(
                id: entry.id,
                note: entry.note!,
                moodScore: entry.score,
                createdAt: entry.createdAt,
              ),
            ),
      );

    if (_moodHistory.isNotEmpty) {
      _selectedMoodScore = _moodHistory.first.score;
    }
  }

  void _prependMoodEntry(MoodCheckin entry) {
    _moodHistory.insert(0, entry);
    _selectedMoodScore = entry.score;
  }

  void _prependReflection(ReflectionEntry reflection) {
    _reflections.insert(0, reflection);
  }

  Future<void> _loadVerseForScore(int score) async {
    try {
      final response = await _apiClient.getDailyVerse(
        _moodToVerseCategory(score),
      );
      _currentVerse = VerseMoment.fromJson(response);
    } catch (error) {
      _setError(_describeError(error));
    }
  }

  Future<void> _resetSession() async {
    await _chatSocketClient?.disconnect();
    _chatSocketClient = null;
    await _sessionStore.clear();

    _token = null;
    _conversationId = null;
    _streamingMessageId = null;
    _user = null;
    _selectedTab = AppTab.home;
    _chatMode = ChatMode.listen;
    _selectedMoodScore = 3;
    _currentVerse = null;
    _safetyPlan = const SafetyPlanData();
    _moodHistory.clear();
    _reflections.clear();
    _messages.clear();
    _paths.clear();
    _circles.clear();
    _isChatConnected = false;
    _isTyping = false;
    _isSendingMessage = false;
    _isCompanionLoading = false;
    _isPathsLoading = false;
    _isCirclesLoading = false;
    _isHomeLoading = false;
    _isSavingSafetyPlan = false;
  }

  void _setError(String message) {
    _errorMessage = message;
  }

  void _clearError() {
    _errorMessage = null;
  }

  String _describeError(Object error) {
    if (error is ApiException) {
      return error.message;
    }
    return '$error';
  }

  static int _normalizeMoodScore(int score) {
    if (score <= 5) {
      return score.clamp(1, 5);
    }
    final normalized = (score / 2).round();
    return normalized.clamp(1, 5);
  }

  static String _moodToVerseCategory(int score) {
    switch (score) {
      case 1:
        return 'sad';
      case 2:
        return 'anxious';
      case 4:
        return 'happy';
      case 5:
        return 'grateful';
      default:
        return 'default';
    }
  }
}

String _moodLabel(int score) {
  switch (score) {
    case 1:
      return 'Heavy';
    case 2:
      return 'Tender';
    case 4:
      return 'Bright';
    case 5:
      return 'Grateful';
    default:
      return 'Steady';
  }
}

List<String> _asStringList(dynamic value) {
  if (value is! List) {
    return <String>[];
  }
  return value
      .map((item) => '$item')
      .where((item) => item.trim().isNotEmpty)
      .toList();
}
