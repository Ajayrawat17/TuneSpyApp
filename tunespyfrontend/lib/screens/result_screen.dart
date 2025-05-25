import 'package:flutter/material.dart';

class ResultScreen extends StatelessWidget {
  final String songDetails;

  const ResultScreen({super.key, required this.songDetails});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Song Details')),
      body: Center(
        child: Text(songDetails, style: const TextStyle(fontSize: 18)),
      ),
    );
  }
}
