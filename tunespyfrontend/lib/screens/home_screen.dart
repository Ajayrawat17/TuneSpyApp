import 'package:flutter/material.dart';
import 'package:flutter_sound/flutter_sound.dart';
import 'package:permission_handler/permission_handler.dart';
import 'package:http/http.dart' as http;
import 'package:path_provider/path_provider.dart';
import 'dart:async';

import 'result_screen.dart';

class HomeScreen extends StatefulWidget {
  @override
  _HomeScreenState createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen>
    with SingleTickerProviderStateMixin {
  bool isRecording = false;
  FlutterSoundRecorder? _audioRecorder;
  String? audioFilePath;

  late AnimationController _animationController;
  late Animation<double> _animation;

  @override
  void initState() {
    super.initState();
    _audioRecorder = FlutterSoundRecorder();
    _initializeRecorder();

    _animationController = AnimationController(
      vsync: this,
      duration: Duration(milliseconds: 1000),
    );
    _animation = Tween<double>(begin: 1.0, end: 1.5).animate(
      CurvedAnimation(parent: _animationController, curve: Curves.easeInOut),
    );
    _animationController.addStatusListener((status) {
      if (status == AnimationStatus.completed) {
        _animationController.reverse();
      } else if (status == AnimationStatus.dismissed) {
        _animationController.forward();
      }
    });
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
      _animationController.forward();
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
      _animationController.stop();
      _animationController.reset();
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
    _animationController.dispose();
    super.dispose();
  }

  Widget buildMicButton() {
    return ScaleTransition(
      scale: _animation,
      child: CircleAvatar(
        radius: 40,
        backgroundColor: isRecording ? Colors.redAccent : Colors.blueAccent,
        child: IconButton(
          icon: Icon(isRecording ? Icons.stop : Icons.mic),
          color: Colors.white,
          iconSize: 40,
          onPressed: isRecording ? stopRecording : startRecording,
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('TuneSpy'),
        backgroundColor: Colors.blueAccent,
      ),
      body: Center(
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 24.0),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            mainAxisAlignment: MainAxisAlignment.center,
            crossAxisAlignment: CrossAxisAlignment.center,
            children: [
              buildMicButton(),
              SizedBox(height: 30),
              Text(
                isRecording
                    ? "Recording in progress..."
                    : "Tap the mic to start",
                style: TextStyle(fontSize: 18, fontWeight: FontWeight.w500),
                textAlign: TextAlign.center,
              ),
              SizedBox(height: 40),
              ElevatedButton.icon(
                style: ElevatedButton.styleFrom(
                  padding: EdgeInsets.symmetric(
                    horizontal: 30.0,
                    vertical: 15.0,
                  ),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(30),
                  ),
                  backgroundColor: Colors.blueAccent,
                ),
                onPressed: () => sendAudioFile(context),
                icon: Icon(Icons.music_note),
                label: Text('Identify Song', style: TextStyle(fontSize: 18)),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
