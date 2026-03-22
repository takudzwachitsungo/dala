import 'dart:io';

import 'package:flutter/foundation.dart';

class AppConfig {
  static const String _apiOverride = String.fromEnvironment(
    'DALA_API_URL',
    defaultValue: '',
  );
  static const String _webSocketOverride = String.fromEnvironment(
    'DALA_WS_URL',
    defaultValue: '',
  );

  static String get apiBaseUrl {
    if (_apiOverride.isNotEmpty) {
      return _apiOverride;
    }

    if (kIsWeb) {
      return 'http://localhost:8000/api/v1';
    }

    if (Platform.isAndroid) {
      return 'http://10.0.2.2:8000/api/v1';
    }

    return 'http://localhost:8000/api/v1';
  }

  static String get webSocketBaseUrl {
    if (_webSocketOverride.isNotEmpty) {
      return _webSocketOverride;
    }

    final apiUri = Uri.parse(apiBaseUrl);
    final wsScheme = apiUri.scheme == 'https' ? 'wss' : 'ws';

    return apiUri.replace(scheme: wsScheme).toString();
  }
}
