import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:url_launcher/url_launcher.dart';

import '../providers/connection_provider.dart';
import 'qr_scanner_screen.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  final _connectionCode = TextEditingController();

  Future<void> _scanQrCode(ConnectionProvider connection) async {
    final code = await Navigator.of(context).push<String>(
      MaterialPageRoute(builder: (_) => const QrScannerScreen()),
    );
    if (!mounted || code == null) return;

    setState(() => _connectionCode.text = code);
    await connection.connectWithConnectionCode(code);
  }

  Future<void> _checkForUpdate(ConnectionProvider connection) async {
    final update = await connection.checkForUpdate();
    if (!mounted || update == null) return;

    if (!update.updateAvailable) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('App atualizado.')),
      );
      return;
    }

    final downloadUri = update.downloadUri;
    final download = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Atualização disponível'),
        content: Text('A versão ${update.latestVersion} está disponível.'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context, false),
            child: const Text('Agora não'),
          ),
          FilledButton(
            onPressed: downloadUri == null
                ? null
                : () => Navigator.pop(context, true),
            child: const Text('Baixar'),
          ),
        ],
      ),
    );
    if (!mounted || download != true || downloadUri == null) return;

    final opened = await launchUrl(
      downloadUri,
      mode: LaunchMode.externalApplication,
    );
    if (!mounted || opened) return;
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Não foi possível abrir o download.')),
    );
  }

  @override
  void dispose() {
    _connectionCode.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final connection = context.watch<ConnectionProvider>();
    return Scaffold(
      appBar: AppBar(title: const Text('MouseFree')),
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(20),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Row(
                children: [
                  Icon(
                    connection.connected
                        ? Icons.check_circle
                        : Icons.circle_outlined,
                    color: connection.connected ? Colors.green : Colors.grey,
                  ),
                  const SizedBox(width: 8),
                  Text(connection.status),
                ],
              ),
              const SizedBox(height: 12),
              TextField(
                controller: _connectionCode,
                autocorrect: false,
                enableSuggestions: false,
                decoration: const InputDecoration(
                  labelText: 'Código de conexão',
                  hintText: 'Leia o QR Code ou cole o código do PC',
                  helperText: 'No PC, abra o MouseFree e mostre o QR Code.',
                ),
              ),
              const SizedBox(height: 8),
              OutlinedButton.icon(
                onPressed: connection.connected
                    ? null
                    : () => _scanQrCode(connection),
                icon: const Icon(Icons.qr_code_scanner),
                label: const Text('Ler QR Code'),
              ),
              const SizedBox(height: 8),
              FilledButton(
                onPressed: connection.connected
                    ? connection.disconnect
                    : () => connection.connectWithConnectionCode(
                          _connectionCode.text,
                        ),
                child: Text(connection.connected ? 'Desconectar' : 'Conectar'),
              ),
              const SizedBox(height: 8),
              OutlinedButton.icon(
                onPressed: connection.checkingForUpdate
                    ? null
                    : () => _checkForUpdate(connection),
                icon: connection.checkingForUpdate
                    ? const SizedBox(
                        width: 18,
                        height: 18,
                        child: CircularProgressIndicator(strokeWidth: 2),
                      )
                    : const Icon(Icons.system_update),
                label: Text(
                  connection.checkingForUpdate
                      ? 'Procurando atualizações...'
                      : 'Atualizar aplicativo',
                ),
              ),
              if (connection.error != null) ...[
                const SizedBox(height: 8),
                Text(
                  connection.error!,
                  style: TextStyle(color: Theme.of(context).colorScheme.error),
                ),
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
                  onTap: connection.connected
                      ? () => connection.click('left')
                      : null,
                  child: DecoratedBox(
                    decoration: BoxDecoration(
                      color: Theme.of(context).colorScheme.surfaceContainerHighest,
                      borderRadius: BorderRadius.circular(16),
                    ),
                    child: const Center(
                      child: Text(
                        'Deslize para mover\nToque para clicar',
                        textAlign: TextAlign.center,
                      ),
                    ),
                  ),
                ),
              ),
              const SizedBox(height: 12),
              Row(
                children: [
                  Expanded(
                    child: OutlinedButton(
                      onPressed: connection.connected
                          ? () => connection.click('left')
                          : null,
                      child: const Text('Clique esquerdo'),
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: OutlinedButton(
                      onPressed: connection.connected
                          ? () => connection.click('right')
                          : null,
                      child: const Text('Clique direito'),
                    ),
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }
}
