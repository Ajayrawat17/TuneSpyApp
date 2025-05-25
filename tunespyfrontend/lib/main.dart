import 'package:flutter/material.dart';
import 'screens/home_screen.dart';

void main() {
  runApp(TuneSpyApp());
}

class TuneSpyApp extends StatelessWidget {
  const TuneSpyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'TuneSpy',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        primarySwatch: Colors.deepPurple,
        scaffoldBackgroundColor: Colors.white,
      ),
      home: HomeScreen(),
    );
  }
}
