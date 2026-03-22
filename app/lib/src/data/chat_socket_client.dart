import 'dart:async';
import 'dart:convert';

import 'package:web_socket_channel/web_socket_channel.dart';

class ChatSocketClient {
  ChatSocketClient({required this.uri});

  final Uri uri;
  WebSocketChannel? _channel;
  StreamSubscription<dynamic>? _subscription;

  bool get isConnected => _channel != null;

  Future<void> connect({
    required void Function(Map<String, dynamic> message) onMessage,
    required void Function(Object error) onError,
    void Function()? onDone,
  }) async {
    await disconnect();

    final channel = WebSocketChannel.connect(uri);
    _channel = channel;
    _subscription = channel.stream.listen(
      (event) {
        if (event is String && event.isNotEmpty) {
          onMessage(jsonDecode(event) as Map<String, dynamic>);
        }
      },
      onError: onError,
      onDone: onDone,
      cancelOnError: true,
    );
  }

  void sendMessage({required String text, required String mode}) {
    _channel?.sink.add(
      jsonEncode({'type': 'message', 'message': text, 'mode': mode}),
    );
  }

  Future<void> disconnect() async {
    await _subscription?.cancel();
    _subscription = null;
    await _channel?.sink.close();
    _channel = null;
  }
}
