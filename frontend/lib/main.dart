import 'package:flutter/material.dart';
import 'screens/upload_screen.dart';

void main() {
  runApp(MyApp());
}

class MyApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(title: 'VeritasAD', home: UploadScreen());
  }
}
