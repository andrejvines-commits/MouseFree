// This is a basic Flutter widget test.
//
// To perform an interaction with a widget in your test, use the WidgetTester
// utility in the flutter_test package. For example, you can send tap and scroll
// gestures. You can also use WidgetTester to find child widgets in the widget
// tree, read text, and verify that the values of widget properties are correct.

import 'package:flutter_test/flutter_test.dart';

import 'package:mouse_controller/main.dart';

void main() {
  testWidgets('shows the connection form', (WidgetTester tester) async {
    await tester.pumpWidget(const MouseControllerApp());

    expect(find.text('MouseFree'), findsOneWidget);
    expect(find.text('Código de conexão'), findsOneWidget);
    expect(find.text('Conectar'), findsOneWidget);
    expect(find.text('Ler QR Code'), findsOneWidget);
    expect(find.text('Atualizar aplicativo'), findsOneWidget);
  });
}
