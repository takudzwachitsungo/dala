import 'dart:async';
import 'dart:convert';

import 'package:http/http.dart' as http;

import 'app_config.dart';

class ApiException implements Exception {
  ApiException(this.message, {this.statusCode});

  final String message;
  final int? statusCode;

  @override
  String toString() =>
      'ApiException(statusCode: $statusCode, message: $message)';
}

class DalaApiClient {
  DalaApiClient({http.Client? client}) : _client = client ?? http.Client();

  static const Duration _requestTimeout = Duration(seconds: 12);

  final http.Client _client;

  String get apiBaseUrl => AppConfig.apiBaseUrl;
  String get webSocketBaseUrl => AppConfig.webSocketBaseUrl;

  Future<Map<String, dynamic>> createAnonymousSession() async {
    final response = await _request(
      method: 'POST',
      path: '/auth/anonymous-session',
      body: {'privacy_consent': true},
    );
    return _decodeObject(response);
  }

  Future<Map<String, dynamic>> getProfile(String token) async {
    final response = await _request(
      method: 'GET',
      path: '/profile',
      token: token,
    );
    return _decodeObject(response);
  }

  Future<Map<String, dynamic>> getMoodHistory(
    String token, {
    int days = 30,
  }) async {
    final response = await _request(
      method: 'GET',
      path: '/mood/history',
      token: token,
      queryParameters: {'days': '$days'},
    );
    return _decodeObject(response);
  }

  Future<Map<String, dynamic>> logMood(
    String token, {
    required int moodScore,
    List<String> emotions = const [],
    List<String> activities = const [],
    String? notes,
    String? conversationId,
  }) async {
    final response = await _request(
      method: 'POST',
      path: '/mood',
      token: token,
      body: {
        'mood_score': moodScore,
        'emotions': emotions,
        'activities': activities,
        'notes': notes,
        'conversation_id': conversationId,
      }..removeWhere((key, value) => value == null),
    );
    return _decodeObject(response);
  }

  Future<Map<String, dynamic>> getDailyVerse(String mood) async {
    final response = await _request(
      method: 'GET',
      path: '/verses/daily-verse',
      queryParameters: {'mood': mood},
    );
    return _decodeObject(response);
  }

  Future<List<dynamic>> getConversations(
    String token, {
    int limit = 20,
    int offset = 0,
  }) async {
    final response = await _request(
      method: 'GET',
      path: '/conversations',
      token: token,
      queryParameters: {'limit': '$limit', 'offset': '$offset'},
    );
    return _decodeList(response);
  }

  Future<Map<String, dynamic>> createConversation(
    String token, {
    required String mode,
    String? title,
  }) async {
    final response = await _request(
      method: 'POST',
      path: '/conversations',
      token: token,
      body: {'mode': mode, 'title': title}
        ..removeWhere((key, value) => value == null),
    );
    return _decodeObject(response);
  }

  Future<List<dynamic>> getConversationMessages(
    String token,
    String conversationId, {
    int limit = 100,
    int offset = 0,
  }) async {
    final response = await _request(
      method: 'GET',
      path: '/conversations/$conversationId/messages',
      token: token,
      queryParameters: {'limit': '$limit', 'offset': '$offset'},
    );
    return _decodeList(response);
  }

  Future<Map<String, dynamic>> getSafetyPlan(String token) async {
    final response = await _request(
      method: 'GET',
      path: '/safety-plan',
      token: token,
    );
    return _decodeObject(response);
  }

  Future<Map<String, dynamic>> updateSafetyPlan(
    String token,
    Map<String, dynamic> payload,
  ) async {
    final response = await _request(
      method: 'PUT',
      path: '/safety-plan',
      token: token,
      body: payload,
    );
    return _decodeObject(response);
  }

  Future<List<dynamic>> getPaths(
    String token, {
    int limit = 20,
    int offset = 0,
  }) async {
    final response = await _request(
      method: 'GET',
      path: '/paths',
      token: token,
      queryParameters: {'limit': '$limit', 'skip': '$offset'},
    );
    return _decodeList(response);
  }

  Future<Map<String, dynamic>> enrollInPath(String token, String pathId) async {
    final response = await _request(
      method: 'POST',
      path: '/paths/$pathId/enroll',
      token: token,
    );
    return _decodeObject(response);
  }

  Future<List<dynamic>> getCircles(
    String token, {
    int limit = 20,
    int offset = 0,
  }) async {
    final response = await _request(
      method: 'GET',
      path: '/circles',
      token: token,
      queryParameters: {'limit': '$limit', 'skip': '$offset'},
    );
    return _decodeList(response);
  }

  Future<void> joinCircle(String token, String circleId) async {
    await _request(
      method: 'POST',
      path: '/circles/$circleId/join',
      token: token,
    );
  }

  Future<void> leaveCircle(String token, String circleId) async {
    await _request(
      method: 'DELETE',
      path: '/circles/$circleId/leave',
      token: token,
    );
  }

  Uri webSocketUri({required String token, required String conversationId}) {
    final baseUri = Uri.parse(webSocketBaseUrl);
    final path = baseUri.path.endsWith('/')
        ? '${baseUri.path}ws/chat'
        : '${baseUri.path}/ws/chat';

    return baseUri.replace(
      path: path,
      queryParameters: {'token': token, 'conversation_id': conversationId},
    );
  }

  Future<http.Response> _request({
    required String method,
    required String path,
    String? token,
    Map<String, String>? queryParameters,
    Map<String, dynamic>? body,
  }) async {
    final uri = Uri.parse(
      '$apiBaseUrl$path',
    ).replace(queryParameters: queryParameters);

    final headers = <String, String>{
      'Accept': 'application/json',
      if (body != null) 'Content-Type': 'application/json',
      if (token != null) 'Authorization': 'Bearer $token',
    };

    try {
      late http.Response response;
      switch (method) {
        case 'GET':
          response = await _client
              .get(uri, headers: headers)
              .timeout(_requestTimeout);
          break;
        case 'POST':
          response = await _client
              .post(
                uri,
                headers: headers,
                body: body == null ? null : jsonEncode(body),
              )
              .timeout(_requestTimeout);
          break;
        case 'PUT':
          response = await _client
              .put(
                uri,
                headers: headers,
                body: body == null ? null : jsonEncode(body),
              )
              .timeout(_requestTimeout);
          break;
        case 'PATCH':
          response = await _client
              .patch(
                uri,
                headers: headers,
                body: body == null ? null : jsonEncode(body),
              )
              .timeout(_requestTimeout);
          break;
        case 'DELETE':
          response = await _client
              .delete(uri, headers: headers)
              .timeout(_requestTimeout);
          break;
        default:
          throw UnsupportedError('Unsupported method: $method');
      }

      if (response.statusCode >= 200 && response.statusCode < 300) {
        return response;
      }

      throw ApiException(
        _extractErrorMessage(response),
        statusCode: response.statusCode,
      );
    } on TimeoutException {
      throw ApiException(
        'Dala could not reach $apiBaseUrl in time. '
        'If you are running on a physical phone, start Flutter with '
        '--dart-define=DALA_API_URL=http://<your-computer-ip>:8000/api/v1 '
        'and --dart-define=DALA_WS_URL=ws://<your-computer-ip>:8000/api/v1.',
      );
    } on http.ClientException catch (error) {
      throw ApiException(
        'Dala could not connect to $apiBaseUrl. ${error.message} '
        'If you are running on a physical phone, use your computer LAN IP instead of localhost.',
      );
    }
  }

  Map<String, dynamic> _decodeObject(http.Response response) {
    if (response.body.isEmpty) {
      return <String, dynamic>{};
    }
    return jsonDecode(response.body) as Map<String, dynamic>;
  }

  List<dynamic> _decodeList(http.Response response) {
    if (response.body.isEmpty) {
      return <dynamic>[];
    }
    return jsonDecode(response.body) as List<dynamic>;
  }

  String _extractErrorMessage(http.Response response) {
    if (response.body.isEmpty) {
      return 'Request failed with status ${response.statusCode}.';
    }

    try {
      final decoded = jsonDecode(response.body);
      if (decoded is Map<String, dynamic>) {
        final detail = decoded['detail'];
        if (detail is String) {
          return detail;
        }
        final message = decoded['message'];
        if (message is String) {
          return message;
        }
      }
    } catch (_) {
      return response.body;
    }

    return response.body;
  }
}
