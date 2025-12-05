import 'package:flutter/material.dart';
import '../services/api_service.dart';
import '../theme/app_theme.dart';
import '../widgets/platform_selector.dart';

class CreateJobScreen extends StatefulWidget {
  final ApiService apiService;

  const CreateJobScreen({super.key, required this.apiService});

  @override
  State<CreateJobScreen> createState() => _CreateJobScreenState();
}

class _CreateJobScreenState extends State<CreateJobScreen> {
  final _formKey = GlobalKey<FormState>();
  final _urlController = TextEditingController();
  String _selectedPlatform = 'youtube';
  bool _isLoading = false;

  final List<Map<String, dynamic>> _platforms = [
    {'value': 'telegram', 'label': 'Telegram', 'icon': Icons.telegram},
    {'value': 'youtube', 'label': 'YouTube', 'icon': Icons.play_circle},
    {'value': 'vk', 'label': 'VK', 'icon': Icons.people},
    {'value': 'rutube', 'label': 'RuTube', 'icon': Icons.video_library},
    {'value': 'twitch', 'label': 'Twitch', 'icon': Icons.sports_esports},
  ];

  @override
  void dispose() {
    _urlController.dispose();
    super.dispose();
  }

  Future<void> _createJob() async {
    if (!_formKey.currentState!.validate()) {
      return;
    }

    setState(() => _isLoading = true);

    try {
      final job = await widget.apiService.createJob(
        platform: _selectedPlatform,
        url: _urlController.text.trim(),
      );

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Row(
              children: [
                const Icon(Icons.check_circle, color: Colors.white),
                const SizedBox(width: 12),
                Expanded(
                  child: Text('Задача создана: ${job.id}'),
                ),
              ],
            ),
            backgroundColor: AppTheme.successColor,
            behavior: SnackBarBehavior.floating,
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(12),
            ),
            action: SnackBarAction(
              label: 'Открыть',
              textColor: Colors.white,
              onPressed: () {
                Navigator.pop(context, true);
              },
            ),
          ),
        );

        // Wait a bit before navigating to show the success message
        await Future.delayed(const Duration(milliseconds: 500));

        if (mounted) {
          Navigator.pop(context, true);
        }
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Row(
              children: [
                const Icon(Icons.error_outline, color: Colors.white),
                const SizedBox(width: 12),
                Expanded(
                  child: Text('Ошибка: $e'),
                ),
              ],
            ),
            backgroundColor: AppTheme.errorColor,
            behavior: SnackBarBehavior.floating,
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(12),
            ),
          ),
        );
      }
    } finally {
      if (mounted) {
        setState(() => _isLoading = false);
      }
    }
  }

  String? _validateUrl(String? value) {
    if (value == null || value.trim().isEmpty) {
      return 'Введите ссылку';
    }
    final uri = Uri.tryParse(value.trim());
    if (uri == null || !uri.hasScheme) {
      return 'Введите корректную ссылку (например: https://...)';
    }
    return null;
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Создать задачу'),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(24),
        child: Form(
          key: _formKey,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              _buildHeader(),
              const SizedBox(height: 32),
              _buildPlatformSelector(),
              const SizedBox(height: 32),
              _buildUrlInput(),
              const SizedBox(height: 32),
              _buildCreateButton(),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildHeader() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Container(
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: AppTheme.primaryColor.withValues(alpha: 0.1),
            borderRadius: BorderRadius.circular(12),
          ),
          child: Row(
            children: [
              const Icon(
                Icons.info_outline,
                color: AppTheme.primaryColor,
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Text(
                  'Выберите платформу и вставьте ссылку на контент для анализа',
                  style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                        color: AppTheme.primaryColor,
                      ),
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildPlatformSelector() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'Платформа',
          style: Theme.of(context).textTheme.titleMedium?.copyWith(
                fontWeight: FontWeight.bold,
              ),
        ),
        const SizedBox(height: 12),
        PlatformSelector(
          selectedPlatform: _selectedPlatform,
          onPlatformChanged: (platform) {
            setState(() {
              _selectedPlatform = platform;
            });
          },
          platforms: _platforms,
        ),
      ],
    );
  }

  Widget _buildUrlInput() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'Ссылка на контент',
          style: Theme.of(context).textTheme.titleMedium?.copyWith(
                fontWeight: FontWeight.bold,
              ),
        ),
        const SizedBox(height: 12),
        TextFormField(
          controller: _urlController,
          decoration: InputDecoration(
            labelText: 'URL',
            hintText: 'https://youtube.com/watch?v=...',
            prefixIcon: const Icon(Icons.link),
            suffixIcon: _urlController.text.isNotEmpty
                ? IconButton(
                    icon: const Icon(Icons.clear),
                    onPressed: () {
                      _urlController.clear();
                      setState(() {});
                    },
                  )
                : null,
          ),
          keyboardType: TextInputType.url,
          textInputAction: TextInputAction.done,
          validator: _validateUrl,
          onFieldSubmitted: (_) => _createJob(),
          enabled: !_isLoading,
          onChanged: (_) => setState(() {}),
        ),
      ],
    );
  }

  Widget _buildCreateButton() {
    return SizedBox(
      height: 56,
      child: ElevatedButton.icon(
        onPressed: _isLoading ? null : _createJob,
        icon: _isLoading
            ? const SizedBox(
                width: 20,
                height: 20,
                child: CircularProgressIndicator(
                  strokeWidth: 2,
                  valueColor: AlwaysStoppedAnimation<Color>(Colors.white),
                ),
              )
            : const Icon(Icons.analytics),
        label: Text(_isLoading ? 'Создание задачи...' : 'Создать задачу'),
        style: ElevatedButton.styleFrom(
          backgroundColor: AppTheme.primaryColor,
          foregroundColor: Colors.white,
          elevation: 0,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(12),
          ),
        ),
      ),
    );
  }
}
