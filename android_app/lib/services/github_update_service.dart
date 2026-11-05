import 'dart:convert';
import 'dart:io';

class UpdateCheck {
  const UpdateCheck({
    required this.latestVersion,
    required this.updateAvailable,
    required this.downloadUri,
  });

  final String latestVersion;
  final bool updateAvailable;
  final Uri? downloadUri;
}

class GithubUpdateService {
  static final _latestReleaseUri = Uri.parse(
    'https://api.github.com/repos/andrejvines-commits/MouseFree/releases/latest',
  );

  Future<UpdateCheck> check(String currentVersion) async {
    final client = HttpClient()..userAgent = 'MouseFree Android';
    try {
      final response = await (await client.getUrl(_latestReleaseUri)).close();
      if (response.statusCode != HttpStatus.ok) {
        throw HttpException('Não foi possível consultar a atualização.');
      }
      final data =
          jsonDecode(await utf8.decodeStream(response)) as Map<String, dynamic>;
      final latest =
          data['tag_name'].toString().replaceFirst(RegExp(r'^v'), '');
      final assets = data['assets'] as List<dynamic>? ?? [];
      final asset = assets.cast<Map<String, dynamic>>().where(
        (item) => item['name'] == 'app-debug.apk',
      );
      final download = asset.isEmpty
          ? null
          : Uri.tryParse(asset.first['browser_download_url'].toString());
      return UpdateCheck(
        latestVersion: latest,
        updateAvailable: _isNewer(latest, currentVersion),
        downloadUri: download,
      );
    } finally {
      client.close(force: true);
    }
  }

  bool _isNewer(String latest, String current) {
    List<int> parse(String value) =>
        value.split('.').map(int.tryParse).map((v) => v ?? 0).toList();
    final left = parse(latest);
    final right = parse(current);
    for (var index = 0; index < 3; index++) {
      final a = index < left.length ? left[index] : 0;
      final b = index < right.length ? right[index] : 0;
      if (a != b) return a > b;
    }
    return false;
  }
}
