import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import 'providers/connection_provider.dart';
import 'screens/home_screen.dart';

void main() {
  runApp(
    ChangeNotifierProvider(
      create: (_) => ConnectionProvider(),
      child: const MouseControllerApp(),
    ),
  );
}

class MouseControllerApp extends StatelessWidget {
  const MouseControllerApp({super.key});

  @override
  Widget build(BuildContext context) => MaterialApp(
        title: 'Mouse Controller',
        theme: ThemeData(colorSchemeSeed: Colors.indigo, useMaterial3: true),
        home: const HomeScreen(),
      );
}
