import 'package:flutter/material.dart';
import 'package:file_picker/file_picker.dart';
import 'package:dio/dio.dart';
import 'package:flutter/foundation.dart' show kIsWeb; // ← ВАЖНО!

class UploadScreen extends StatefulWidget {
  @override
  _UploadScreenState createState() => _UploadScreenState();
}

class _UploadScreenState extends State<UploadScreen> {
  final _urlController = TextEditingController();
  String _status = '';
  bool _isLoading = false;
  final dio = Dio(BaseOptions(baseUrl: 'http://localhost:8000'));

  Future<void> _uploadFile() async {
    FilePickerResult? result = await FilePicker.platform.pickFiles(
      type: FileType.video,
    );
    if (result == null) return;

    setState(() => _isLoading = true);
    var file = result.files.first;

    try {
      FormData formData;

      if (kIsWeb) {
        // === ДЛЯ ВЕБА: используем bytes ===
        if (file.bytes == null) {
          setState(() => _status = 'Ошибка: файл не загружен (bytes пустые)');
          return;
        }
        formData = FormData.fromMap({
          'file': MultipartFile.fromBytes(
            file.bytes!,
            filename: file.name,
          ),
        });
      } else {
        // === ДЛЯ МОБИЛЬНЫХ/ДЕСКТОП ===
        if (file.path == null) {
          setState(() => _status = 'Ошибка: путь к файлу недоступен');
          return;
        }
        formData = FormData.fromMap({
          'file': await MultipartFile.fromFile(
            file.path!,
            filename: file.name,
          ),
        });
      }

      var response = await dio.post('/upload/video', data: formData);
      setState(() => _status = 'Успех: ${response.data['message']}');
    } catch (e) {
      if (e is DioException && e.response != null) {
        setState(() =>
            _status = 'Ошибка: ${e.response?.data['detail'] ?? e.message}');
      } else {
        setState(() => _status = 'Ошибка: $e');
      }
    } finally {
      setState(() => _isLoading = false);
    }
  }

  Future<void> _uploadUrl() async {
    if (_urlController.text.isEmpty) return;
    setState(() => _isLoading = true);
    try {
      var response = await dio.post(
        '/upload/video',
        data: {'url': _urlController.text},
      );
      setState(() => _status = 'Успех: ${response.data['message']}');
    } catch (e) {
      setState(() => _status = 'Ошибка: $e');
    } finally {
      setState(() => _isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text("VeritasAD — Загрузка")),
      body: Padding(
        padding: EdgeInsets.all(20),
        child: Column(
          children: [
            ElevatedButton(
              onPressed: _isLoading ? null : _uploadFile,
              child: Text("Загрузить видео"),
            ),
            SizedBox(height: 20),
            TextField(
              controller: _urlController,
              decoration: InputDecoration(labelText: "Или ссылка"),
            ),
            ElevatedButton(
              onPressed: _isLoading ? null : _uploadUrl,
              child: Text("Обработать"),
            ),
            SizedBox(height: 20),
            if (_isLoading) CircularProgressIndicator(),
            Text(
              _status,
              style: TextStyle(
                color: _status.contains("Успех") ? Colors.green : Colors.red,
              ),
            ),
          ],
        ),
      ),
    );
  }
}
