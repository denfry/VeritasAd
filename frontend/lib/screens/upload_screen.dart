import 'package:dio/dio.dart';
import 'package:file_picker/file_picker.dart';
import 'package:flutter/foundation.dart' show kIsWeb;
import 'package:flutter/material.dart';

class UploadScreen extends StatefulWidget {
  const UploadScreen({super.key});

  @override
  State<UploadScreen> createState() => _UploadScreenState();
}

class _UploadScreenState extends State<UploadScreen> {
  final _urlController = TextEditingController();
  bool _isLoading = false;

  final dio = Dio(BaseOptions(
    baseUrl: 'http://localhost:8000',
    connectTimeout: const Duration(seconds: 30),
    receiveTimeout: const Duration(seconds: 60),
  ));

  Future<void> _uploadFile() async {
    FilePickerResult? result = await FilePicker.platform.pickFiles(
      type: FileType.video,
      allowCompression: true,
    );

    if (result == null || result.files.isEmpty) {
      _showSnackBar('Файл не выбран', isError: true);
      return;
    }

    setState(() => _isLoading = true);
    final file = result.files.first;

    try {
      final formData = FormData.fromMap({
        'file': kIsWeb
            ? (file.bytes != null
                ? MultipartFile.fromBytes(file.bytes!, filename: file.name)
                : throw Exception('Нет данных файла (web)'))
            : (file.path != null
                ? await MultipartFile.fromFile(file.path!, filename: file.name)
                : throw Exception('Нет пути к файлу (native)')),
      });

      final response = await dio.post('/api/v1/upload/video', data: formData);
      final message = response.data['message'] ?? 'Видео загружено';
      _showSuccess(message);
    } on DioException catch (e) {
      final error = e.response?.data['detail'] ?? e.message;
      _showSnackBar('Ошибка: $error', isError: true);
    } catch (e) {
      _showSnackBar('Ошибка: $e', isError: true);
    } finally {
      setState(() => _isLoading = false);
    }
  }

  Future<void> _uploadUrl() async {
    final url = _urlController.text.trim();
    if (url.isEmpty || !Uri.tryParse(url)!.hasScheme) {
      _showSnackBar('Введите корректную ссылку', isError: true);
      return;
    }

    setState(() => _isLoading = true);

    try {
      final response = await dio.post('/api/v1/upload/video', data: {'url': url});
      final message = response.data['message'] ?? 'Видео обработано';
      _showSuccess(message);
      _urlController.clear();
    } on DioException catch (e) {
      final error = e.response?.data['detail'] ?? e.message;
      _showSnackBar('Ошибка: $error', isError: true);
    } catch (e) {
      _showSnackBar('Ошибка: $e', isError: true);
    } finally {
      setState(() => _isLoading = false);
    }
  }

  void _showSuccess(String message) {
    _showSnackBar(message, isError: false);
  }

  void _showSnackBar(String message, {required bool isError}) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
        backgroundColor: isError ? Colors.red.shade600 : Colors.green.shade600,
        behavior: SnackBarBehavior.floating,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
        duration: const Duration(seconds: 4),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Center(
      child: ConstrainedBox(
        constraints: const BoxConstraints(maxWidth: 600),
        child: Padding(
          padding: const EdgeInsets.all(24.0),
          child: Card(
            elevation: 8,
            shape:
                RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
            child: Padding(
              padding: const EdgeInsets.all(32.0),
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  SizedBox(
                    width: double.infinity,
                    child: ElevatedButton.icon(
                      onPressed: _isLoading ? null : _uploadFile,
                      icon: const Icon(Icons.video_library),
                      label: const Text("Загрузить видео"),
                      style: ElevatedButton.styleFrom(
                        padding: const EdgeInsets.symmetric(vertical: 16),
                        textStyle: const TextStyle(
                            fontSize: 16, fontWeight: FontWeight.w600),
                      ),
                    ),
                  ),
                  const SizedBox(height: 24),
                  const Divider(height: 1),
                  const SizedBox(height: 24),
                  TextField(
                    controller: _urlController,
                    decoration: InputDecoration(
                      labelText: "Или вставьте ссылку",
                      hintText: "https://youtube.com/... или t.me/...",
                      prefixIcon: const Icon(Icons.link),
                      border: OutlineInputBorder(
                          borderRadius: BorderRadius.circular(12)),
                      enabled: !_isLoading,
                    ),
                    keyboardType: TextInputType.url,
                    textInputAction: TextInputAction.go,
                    onSubmitted: (_) => _uploadUrl(),
                  ),
                  const SizedBox(height: 16),
                  SizedBox(
                    width: double.infinity,
                    child: OutlinedButton.icon(
                      onPressed: _isLoading ? null : _uploadUrl,
                      icon: const Icon(Icons.cloud_download),
                      label: const Text("Обработать ссылку"),
                      style: OutlinedButton.styleFrom(
                        padding: const EdgeInsets.symmetric(vertical: 16),
                        side: BorderSide(color: Colors.indigo.shade700),
                      ),
                    ),
                  ),
                  const SizedBox(height: 24),
                  if (_isLoading)
                    const Column(
                      children: [
                        CircularProgressIndicator(strokeWidth: 3),
                        SizedBox(height: 12),
                        Text("Обработка видео...",
                            style: TextStyle(color: Colors.grey)),
                      ],
                    ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }

  @override
  void dispose() {
    _urlController.dispose();
    super.dispose();
  }
}
