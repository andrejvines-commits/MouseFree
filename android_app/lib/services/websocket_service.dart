import 'dart:convert';

import 'package:web_socket_channel/web_socket_channel.dart';

class WebSocketService {
  WebSocketChannel? _channel;

  Stream<String> connect(Uri uri, String token) {
    disconnect();
    final channel = WebSocketChannel.connect(uri);
    _channel = channel;
    channel.sink.add(jsonEncode({'type': 'authenticate', 'token': token}));
    return channel.stream.map((event) => event.toString());
  }

  void send(String message) {
    final channel = _channel;
    if (channel == null) throw StateError('Não há conexão ativa.');
    channel.sink.add(message);
  }

  Future<void> disconnect() async {
    await _channel?.sink.close();
    _channel = null;
  }
}
