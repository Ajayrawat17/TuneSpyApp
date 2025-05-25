import 'package:flutter/material.dart';
import 'package:flutter_sound/flutter_sound.dart';
import 'package:permission_handler/permission_handler.dart';
import 'package:http/http.dart' as http;
import 'package:path_provider/path_provider.dart';
import 'result_screen.dart';

class HomeScreen extends StatefulWidget {
  @override
  _HomeScreenState createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  bool isRecording = false;
  FlutterSoundRecorder? _audioRecorder;
  String? audioFilePath;

  @override
  void initState() {
    super.initState();
    _audioRecorder = FlutterSoundRecorder();
    _initializeRecorder();
  }

  Future<void> _initializeRecorder() async {
    final micStatus = await Permission.microphone.request();

    if (micStatus != PermissionStatus.granted) {
      print('Microphone permission denied');
      return;
    }

    try {
      await _audioRecorder!.openRecorder();
      await _audioRecorder!.setSubscriptionDuration(Duration(milliseconds: 50));
      print('Recorder opened successfully');
    } catch (e) {
      print('Error opening recorder: $e');
    }
  }

  Future<String> _getFilePath() async {
    final directory = await getApplicationDocumentsDirectory();
    return '${directory.path}/recorded_audio.wav';
  }

  Future<void> startRecording() async {
    if (_audioRecorder!.isRecording) {
      print("Already recording!");
      return;
    }

    String path = await _getFilePath();

    try {
      await _audioRecorder!.startRecorder(
        toFile: path,
        codec: Codec.pcm16WAV,
        sampleRate: 22050,
        audioSource: AudioSource.microphone,
      );
      setState(() {
        isRecording = true;
      });
    } catch (e) {
      print("Error starting recorder: $e");
    }
  }

  Future<void> stopRecording() async {
    if (!_audioRecorder!.isRecording) {
      print("Not recording currently!");
      return;
    }

    try {
      await _audioRecorder!.stopRecorder();
      String path = await _getFilePath();
      setState(() {
        isRecording = false;
        audioFilePath = path;
      });
    } catch (e) {
      print("Error stopping recorder: $e");
    }
  }

  Future<void> sendAudioFile(BuildContext context) async {
    if (audioFilePath == null) return;

    try {
      print('Audio file path: $audioFilePath');

      var request = http.MultipartRequest(
        'POST',
        Uri.parse('http://172.19.25.130:8000/api/recognize/'),
      );

      request.files.add(
        await http.MultipartFile.fromPath('audio_file', audioFilePath!),
      );

      var response = await request.send();

      if (response.statusCode == 200) {
        final songDetails = await response.stream.bytesToString();
        print('Song Details: $songDetails');

        Navigator.push(
          context,
          MaterialPageRoute(
            builder: (context) => ResultScreen(songDetails: songDetails),
          ),
        );
      } else {
        print('Error: ${response.statusCode} - ${response.reasonPhrase}');
        final errorResponse = await response.stream.bytesToString();
        print('Error Response: $errorResponse');

        showDialog(
          context: context,
          builder:
              (_) => AlertDialog(
                title: Text('Error'),
                content: Text(
                  'Failed to identify the song. Please try again later.',
                ),
                actions: [
                  TextButton(
                    onPressed: () => Navigator.pop(context),
                    child: Text('OK'),
                  ),
                ],
              ),
        );
      }
    } catch (e) {
      print('Exception: $e');
      showDialog(
        context: context,
        builder:
            (_) => AlertDialog(
              title: Text('Error'),
              content: Text('An error occurred. Please try again later.'),
              actions: [
                TextButton(
                  onPressed: () => Navigator.pop(context),
                  child: Text('OK'),
                ),
              ],
            ),
      );
    }
  }

  @override
  void dispose() {
    _audioRecorder?.closeRecorder();
    _audioRecorder = null;
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('TuneSpy')),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            if (isRecording)
              IconButton(
                icon: Icon(Icons.stop),
                onPressed: stopRecording,
                iconSize: 50,
              )
            else
              IconButton(
                icon: Icon(Icons.mic),
                onPressed: startRecording,
                iconSize: 50,
              ),
            SizedBox(height: 20),
            ElevatedButton(
              onPressed: () => sendAudioFile(context), // <-- yahin fix hai
              child: Text('Identify Song'),
            ),
          ],
        ),
      ),
    );
  }
}
