import 'package:dio/dio.dart';
import 'package:flutter/material.dart';

class PostUploadScreen extends StatefulWidget {
  const PostUploadScreen({super.key});

  @override
  State<PostUploadScreen> createState() => _PostUploadScreenState();
}

class _PostUploadScreenState extends State<PostUploadScreen> {
  final _urlController = TextEditingController();
  bool _isLoading = false;

  final dio = Dio(BaseOptions(
    baseUrl: 'http://localhost:8000',
    connectTimeout: const Duration(seconds: 30),
    receiveTimeout: const Duration(seconds: 60),
  ));

  Future<void> _analyzePost() async {
    final url = _urlController.text.trim();
    if (url.isEmpty || !Uri.tryParse(url)!.hasScheme) {
      _showSnackBar('Введите корректную ссылку', isError: true);
      return;
    }

    setState(() => _isLoading = true);

    try {
      final response = await dio.post('/api/v1/analyze/post', data: {'url': url});
      final data = response.data;
      final message = data['message'] ?? 'Пост проанализирован';

      _showSuccess(message);
      _urlController.clear();

      // Показать превью
      _showPostPreview(data);
    } on DioException catch (e) {
      final error = e.response?.data['detail'] ?? e.message;
      _showSnackBar('Ошибка: $error', isError: true);
    } catch (e) {
      _showSnackBar('Ошибка: $e', isError: true);
    } finally {
      setState(() => _isLoading = false);
    }
  }

  void _showPostPreview(Map<String, dynamic> data) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text("Пост проанализирован"),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            if (data['title'] != null) ...[
              const Text("Заголовок:",
                  style: TextStyle(fontWeight: FontWeight.bold)),
              Text(data['title'], maxLines: 2, overflow: TextOverflow.ellipsis),
              const SizedBox(height: 8),
            ],
            if (data['uploader'] != null) ...[
              const Text("Автор:",
                  style: TextStyle(fontWeight: FontWeight.bold)),
              Text(data['uploader']),
              const SizedBox(height: 8),
            ],
            if (data['view_count'] != null)
              Text("Просмотры: ${data['view_count']}"),
          ],
        ),
        actions: [
          TextButton(
              onPressed: () => Navigator.pop(context), child: const Text("OK")),
        ],
      ),
    );
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
                  const Text(
                    "Анализ постов из соцсетей",
                    style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                  ),
                  const SizedBox(height: 24),
                  TextField(
                    controller: _urlController,
                    decoration: InputDecoration(
                      labelText: "Ссылка на пост",
                      hintText: "t.me/... или instagram.com/p/...",
                      prefixIcon: const Icon(Icons.link),
                      border: OutlineInputBorder(
                          borderRadius: BorderRadius.circular(12)),
                      enabled: !_isLoading,
                    ),
                    keyboardType: TextInputType.url,
                    textInputAction: TextInputAction.go,
                    onSubmitted: (_) => _analyzePost(),
                  ),
                  const SizedBox(height: 16),
                  SizedBox(
                    width: double.infinity,
                    child: ElevatedButton.icon(
                      onPressed: _isLoading ? null : _analyzePost,
                      icon: const Icon(Icons.analytics),
                      label: const Text("Анализировать пост"),
                      style: ElevatedButton.styleFrom(
                        padding: const EdgeInsets.symmetric(vertical: 16),
                        textStyle: const TextStyle(
                            fontSize: 16, fontWeight: FontWeight.w600),
                      ),
                    ),
                  ),
                  const SizedBox(height: 24),
                  if (_isLoading)
                    const Column(
                      children: [
                        CircularProgressIndicator(strokeWidth: 3),
                        SizedBox(height: 12),
                        Text("Анализ поста...",
                            style: TextStyle(color: Colors.grey)),
                      ],
                    ),
                  const SizedBox(height: 16),
                  const Text(
                    "Поддерживаются: Telegram, YouTube, Instagram, TikTok",
                    style: TextStyle(fontSize: 12, color: Colors.grey),
                    textAlign: TextAlign.center,
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
