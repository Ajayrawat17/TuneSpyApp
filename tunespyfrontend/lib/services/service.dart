import 'dart:convert';
import 'dart:io' as io;
import 'package:flutter/foundation.dart' show kIsWeb;
import 'package:flutter_sound/flutter_sound.dart';
import 'package:http/http.dart' as http;
import 'package:path_provider/path_provider.dart';
import 'package:permission_handler/permission_handler.dart';

final FlutterSoundRecorder _recorder = FlutterSoundRecorder();
bool _isRecorderInitialized = false;

Future<void> initRecorder() async {
  if (kIsWeb) return;

  final status = await Permission.microphone.request();
  if (status != PermissionStatus.granted) {
    throw Exception("Microphone permission not granted");
  }

  await _recorder.openRecorder();
  _isRecorderInitialized = true;
}

Future<String> recognizeAudio() async {
  if (kIsWeb) return "Audio recognition not supported on Web yet";

  if (!_isRecorderInitialized) {
    await initRecorder();
  }

  final dir = await getApplicationDocumentsDirectory();
  final filePath = '${dir.path}/recorded.wav';

  try {
    await _recorder.startRecorder(toFile: filePath, codec: Codec.pcm16WAV);
    await Future.delayed(const Duration(seconds: 10));
    await _recorder.stopRecorder();
  } catch (e) {
    return "Recording failed: $e";
  }

  final file = io.File(filePath);
  if (!file.existsSync()) return 'Recording file not found.';

  try {
    final request = http.MultipartRequest(
      'POST',
      Uri.parse('https://tunespy-backend.onrender.com/recognize/'),
    )..files.add(await http.MultipartFile.fromPath('audio', file.path));

    final response = await http.Response.fromStream(await request.send());

    if (response.statusCode == 200) {
      final result = jsonDecode(response.body);
      return result['result'] is String
          ? result['result']
          : "🎵 ${result['result']['title']} by ${result['result']['artist']}";
    } else {
      return 'Recognition failed.';
    }
  } catch (e) {
    return 'Recognition error: $e';
  }
}
