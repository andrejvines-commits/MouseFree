import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:url_launcher/url_launcher.dart';

import '../providers/connection_provider.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});
  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  static final _latestApkUri = Uri.parse(
    'https://github.com/andrejvines-commits/MouseFree/'
    'releases/latest/download/app-debug.apk',
  );

  final _address = TextEditingController();
  final _token = TextEditingController();

  Future<void> _downloadLatestVersion() async {
    final opened = await launchUrl(
      _latestApkUri,
      mode: LaunchMode.externalApplication,
    );
    if (!mounted || opened) return;
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Não foi possível abrir o download.')),
    );
  }

  @override
  void dispose() {
    _address.dispose();
    _token.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final connection = context.watch<ConnectionProvider>();
    return Scaffold(
      appBar: AppBar(title: const Text('Mouse Controller')),
      body: SafeArea(
          child: Padding(
        padding: const EdgeInsets.all(20),
        child:
            Column(crossAxisAlignment: CrossAxisAlignment.stretch, children: [
          Row(children: [
            Icon(
                connection.connected
                    ? Icons.check_circle
                    : Icons.circle_outlined,
                color: connection.connected ? Colors.green : Colors.grey),
            const SizedBox(width: 8),
            Text(connection.status),
          ]),
          const SizedBox(height: 12),
          TextField(
              controller: _address,
              keyboardType: TextInputType.url,
              autocorrect: false,
              decoration: const InputDecoration(
                  labelText: 'Endereço WebSocket',
                  hintText: 'ws://192.168.1.25:8765/ws')),
          const SizedBox(height: 12),
          TextField(
              controller: _token,
              obscureText: true,
              autocorrect: false,
              enableSuggestions: false,
              decoration: const InputDecoration(labelText: 'Token de acesso')),
          const SizedBox(height: 12),
          FilledButton(
              onPressed: connection.connected
                  ? connection.disconnect
                  : () => connection.connect(_address.text.trim(), _token.text),
              child: Text(connection.connected ? 'Desconectar' : 'Conectar')),
          const SizedBox(height: 8),
          OutlinedButton.icon(
            onPressed: _downloadLatestVersion,
            icon: const Icon(Icons.system_update),
            label: const Text('Atualizar aplicativo'),
          ),
          if (connection.error != null) ...[
            const SizedBox(height: 8),
            Text(connection.error!,
                style: TextStyle(color: Theme.of(context).colorScheme.error))
          ],
          const Divider(height: 32),
          const Text('Touchpad', style: TextStyle(fontWeight: FontWeight.bold)),
          const SizedBox(height: 12),
          Expanded(
              child: GestureDetector(
            onPanUpdate: connection.connected
                ? (details) =>
                    connection.move(details.delta.dx, details.delta.dy)
                : null,
            onTap: connection.connected ? () => connection.click('left') : null,
            child: DecoratedBox(
                decoration: BoxDecoration(
                    color:
                        Theme.of(context).colorScheme.surfaceContainerHighest,
                    borderRadius: BorderRadius.circular(16)),
                child: const Center(
                    child: Text('Deslize para mover\nToque para clicar',
                        textAlign: TextAlign.center))),
          )),
          const SizedBox(height: 12),
          Row(children: [
            Expanded(
                child: OutlinedButton(
                    onPressed: connection.connected
                        ? () => connection.click('left')
                        : null,
                    child: const Text('Clique esquerdo'))),
            const SizedBox(width: 12),
            Expanded(
                child: OutlinedButton(
                    onPressed: connection.connected
                        ? () => connection.click('right')
                        : null,
                    child: const Text('Clique direito'))),
          ]),
        ]),
      )),
    );
  }
}
