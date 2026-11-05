import 'package:flutter/material.dart';
import 'package:mobile_scanner/mobile_scanner.dart';

class QrScannerScreen extends StatefulWidget {
  const QrScannerScreen({super.key});

  @override
  State<QrScannerScreen> createState() => _QrScannerScreenState();
}

class _QrScannerScreenState extends State<QrScannerScreen> {
  bool _completed = false;

  void _onDetect(BarcodeCapture capture) {
    if (_completed || capture.barcodes.isEmpty) return;
    final value = capture.barcodes.first.rawValue;
    if (value == null || !value.contains('|')) return;
    _completed = true;
    Navigator.of(context).pop(value);
  }

  @override
  Widget build(BuildContext context) => Scaffold(
        appBar: AppBar(title: const Text('Ler QR Code do PC')),
        body: Stack(
          fit: StackFit.expand,
          children: [
            MobileScanner(onDetect: _onDetect),
            const Center(
              child: Icon(Icons.qr_code_scanner, size: 240, color: Colors.white70),
            ),
          ],
        ),
      );
}
