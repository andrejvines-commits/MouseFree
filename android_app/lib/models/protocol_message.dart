import 'dart:convert';

class ProtocolMessage {
  const ProtocolMessage({required this.type, this.x, this.y, this.button});
  final String type;
  final double? x;
  final double? y;
  final String? button;

  Map<String, dynamic> toJson() => {
        'type': type,
        if (x != null) 'x': x,
        if (y != null) 'y': y,
        if (button != null) 'button': button,
      };

  String encode() => jsonEncode(toJson());
  factory ProtocolMessage.move(double x, double y) =>
      ProtocolMessage(type: 'mouse_move', x: x, y: y);
  factory ProtocolMessage.click(String button) =>
      ProtocolMessage(type: 'mouse_click', button: button);
}
