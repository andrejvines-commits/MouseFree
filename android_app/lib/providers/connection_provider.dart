import 'dart:async';
import 'dart:convert';

import 'package:flutter/foundation.dart';

import '../models/protocol_message.dart';
import '../services/websocket_service.dart';

class ConnectionProvider extends ChangeNotifier {
  final WebSocketService _service = WebSocketService();
  StreamSubscription<String>? _messages;
  bool connected = false;
  bool _awaitingAuthentication = false;
  String status = 'Desconectado';
  String? error;

  Future<void> connectWithConnectionCode(String connectionCode) async {
    final parts = connectionCode.trim().split('|');
    if (parts.length != 2 || parts.any((part) => part.trim().isEmpty)) {
      error = 'Cole o código gerado no aplicativo do PC.';
      notifyListeners();
      return;
    }
    await connect(parts[0].trim(), parts[1].trim());
  }

  Future<void> connect(String address, String token) async {
    error = null;
    if (address.isEmpty || token.trim().isEmpty) {
      error = 'Informe o endereço e o token de acesso.';
      notifyListeners();
      return;
    }
    await disconnect(notify: false);
    status = 'Conectando...';
    notifyListeners();
    try {
      final uri = Uri.parse(address);
      if (uri.scheme != 'ws' && uri.scheme != 'wss') {
        throw const FormatException('Use um endereço ws:// ou wss://.');
      }
      _awaitingAuthentication = true;
      _messages = _service.connect(uri, token.trim()).listen(
        _handleMessage,
        onError: (Object exception) {
          error = 'Falha na conexão: $exception';
          connected = false;
          _awaitingAuthentication = false;
          status = 'Desconectado';
          notifyListeners();
        },
        onDone: () {
          connected = false;
          _awaitingAuthentication = false;
          status = 'Desconectado';
          notifyListeners();
        },
      );
      status = 'Autenticando...';
    } catch (exception) {
      connected = false;
      _awaitingAuthentication = false;
      status = 'Desconectado';
      error = exception.toString();
    }
    notifyListeners();
  }

  void _handleMessage(String rawMessage) {
    try {
      final decoded = jsonDecode(rawMessage);
      if (decoded is! Map<String, dynamic> || decoded['type'] != 'response')
        return;
      if (_awaitingAuthentication && decoded['success'] == true) {
        _awaitingAuthentication = false;
        connected = true;
        status = 'Conectado';
      } else if (decoded['success'] != true) {
        _awaitingAuthentication = false;
        connected = false;
        error = decoded['message']?.toString() ?? 'Autenticação recusada.';
        status = 'Desconectado';
      }
      notifyListeners();
    } catch (_) {
      // Ignora mensagens fora do protocolo conhecido.
    }
  }

  void move(double x, double y) => _send(ProtocolMessage.move(x, y).encode());
  void click(String button) => _send(ProtocolMessage.click(button).encode());

  void _send(String message) {
    if (!connected) return;
    try {
      _service.send(message);
    } catch (exception) {
      error = exception.toString();
      notifyListeners();
    }
  }

  Future<void> disconnect({bool notify = true}) async {
    await _messages?.cancel();
    _messages = null;
    await _service.disconnect();
    connected = false;
    _awaitingAuthentication = false;
    status = 'Desconectado';
    if (notify) notifyListeners();
  }

  @override
  void dispose() {
    _messages?.cancel();
    _service.disconnect();
    super.dispose();
  }
}
