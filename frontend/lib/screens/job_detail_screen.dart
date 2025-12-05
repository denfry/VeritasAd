import 'package:flutter/material.dart';
import '../models/job_model.dart';
import '../services/api_service.dart';
import '../theme/app_theme.dart';
import '../widgets/platform_icon.dart';
import '../widgets/status_chip.dart';

class JobDetailScreen extends StatefulWidget {
  final JobModel job;
  final ApiService apiService;

  const JobDetailScreen({
    super.key,
    required this.job,
    required this.apiService,
  });

  @override
  State<JobDetailScreen> createState() => _JobDetailScreenState();
}

class _JobDetailScreenState extends State<JobDetailScreen> {
  JobModel? _currentJob;
  bool _isLoading = true;
  bool _isRefreshing = false;

  @override
  void initState() {
    super.initState();
    _currentJob = widget.job;
    _loadJobDetails();
  }

  Future<void> _loadJobDetails() async {
    setState(() => _isRefreshing = true);
    try {
      final job = await widget.apiService.getJob(_currentJob!.id);
      setState(() {
        _currentJob = job;
        _isLoading = false;
      });
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Row(
              children: [
                const Icon(Icons.error_outline, color: Colors.white),
                const SizedBox(width: 12),
                Expanded(child: Text('Ошибка загрузки: $e')),
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
      setState(() => _isRefreshing = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_isLoading) {
      return Scaffold(
        appBar: AppBar(title: const Text('Детали задачи')),
        body: const Center(child: CircularProgressIndicator()),
      );
    }

    return Scaffold(
      appBar: AppBar(
        title: const Text('Детали задачи'),
        actions: [
          IconButton(
            icon: _isRefreshing
                ? const SizedBox(
                    width: 20,
                    height: 20,
                    child: CircularProgressIndicator(strokeWidth: 2),
                  )
                : const Icon(Icons.refresh),
            onPressed: _isRefreshing ? null : _loadJobDetails,
            tooltip: 'Обновить',
          ),
        ],
      ),
      body: RefreshIndicator(
        onRefresh: _loadJobDetails,
        child: SingleChildScrollView(
          physics: const AlwaysScrollableScrollPhysics(),
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              _buildStatusCard(),
              const SizedBox(height: 16),
              _buildInfoCard(),
              if (_currentJob!.isCompleted) ...[
                const SizedBox(height: 16),
                _buildResultsCard(),
              ],
              if (_currentJob!.isFailed && _currentJob!.errorMessage != null) ...[
                const SizedBox(height: 16),
                _buildErrorCard(),
              ],
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildStatusCard() {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Row(
          children: [
            PlatformIcon(
              platform: _currentJob!.platform,
              size: 64,
            ),
            const SizedBox(width: 20),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    _currentJob!.platform.toUpperCase(),
                    style: Theme.of(context).textTheme.titleLarge?.copyWith(
                          fontWeight: FontWeight.bold,
                          letterSpacing: 0.5,
                        ),
                  ),
                  const SizedBox(height: 12),
                  StatusChip(
                    status: _currentJob!.status,
                    label: _currentJob!.statusLabel,
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildInfoCard() {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                const Icon(Icons.info_outline, color: AppTheme.primaryColor),
                const SizedBox(width: 8),
                Text(
                  'Информация',
                  style: Theme.of(context).textTheme.titleLarge?.copyWith(
                        fontWeight: FontWeight.bold,
                      ),
                ),
              ],
            ),
            const Divider(height: 24),
            _buildInfoRow(
              Icons.tag,
              'ID задачи',
              _currentJob!.id,
            ),
            _buildInfoRow(
              Icons.calendar_today,
              'Создано',
              _formatDateTime(_currentJob!.createdAt),
            ),
            _buildInfoRow(
              Icons.update,
              'Обновлено',
              _formatDateTime(_currentJob!.updatedAt),
            ),
            if (_currentJob!.inputUrl != null)
              _buildInfoRow(
                Icons.link,
                'Исходный URL',
                _currentJob!.inputUrl!,
                isUrl: true,
              ),
          ],
        ),
      ),
    );
  }

  Widget _buildResultsCard() {
    return Card(
      color: AppTheme.successColor.withValues(alpha: 0.05),
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                const Icon(Icons.check_circle, color: AppTheme.successColor),
                const SizedBox(width: 8),
                Text(
                  'Результаты анализа',
                  style: Theme.of(context).textTheme.titleLarge?.copyWith(
                        fontWeight: FontWeight.bold,
                        color: AppTheme.successColor,
                      ),
                ),
              ],
            ),
            const Divider(height: 24),
            if (_currentJob!.mediaUrl != null)
              _buildLinkRow(
                Icons.video_library,
                'Медиа файл',
                _currentJob!.mediaUrl!,
              ),
            if (_currentJob!.resultUrl != null)
              _buildLinkRow(
                Icons.analytics,
                'Метаданные',
                _currentJob!.resultUrl!,
              ),
            if (_currentJob!.mediaPath != null)
              _buildInfoRow(
                Icons.folder,
                'Путь к медиа',
                _currentJob!.mediaPath!,
              ),
            if (_currentJob!.resultPath != null)
              _buildInfoRow(
                Icons.description,
                'Путь к результатам',
                _currentJob!.resultPath!,
              ),
          ],
        ),
      ),
    );
  }

  Widget _buildErrorCard() {
    return Card(
      color: AppTheme.errorColor.withValues(alpha: 0.1),
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                const Icon(Icons.error_outline, color: AppTheme.errorColor),
                const SizedBox(width: 8),
                Text(
                  'Ошибка',
                  style: Theme.of(context).textTheme.titleLarge?.copyWith(
                        fontWeight: FontWeight.bold,
                        color: AppTheme.errorColor,
                      ),
                ),
              ],
            ),
            const SizedBox(height: 12),
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: AppTheme.errorColor.withValues(alpha: 0.1),
                borderRadius: BorderRadius.circular(12),
                border: Border.all(
                  color: AppTheme.errorColor.withValues(alpha: 0.3),
                ),
              ),
              child: Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Expanded(
                    child: Text(
                      _currentJob!.errorMessage!,
                      style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                            color: AppTheme.errorColor,
                          ),
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildInfoRow(IconData icon, String label, String value, {bool isUrl = false}) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 16),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Icon(icon, size: 20, color: AppTheme.textSecondary),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  label,
                  style: Theme.of(context).textTheme.bodySmall?.copyWith(
                        color: AppTheme.textSecondary,
                        fontWeight: FontWeight.w500,
                      ),
                ),
                const SizedBox(height: 4),
                isUrl
                    ? InkWell(
                        onTap: () {
                          // TODO: Open URL in browser
                        },
                        child: Text(
                          value,
                          style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                                color: AppTheme.primaryColor,
                                decoration: TextDecoration.underline,
                              ),
                        ),
                      )
                    : Text(
                        value,
                        style: Theme.of(context).textTheme.bodyMedium,
                      ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildLinkRow(IconData icon, String label, String url) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 16),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Icon(icon, size: 20, color: AppTheme.textSecondary),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  label,
                  style: Theme.of(context).textTheme.bodySmall?.copyWith(
                        color: AppTheme.textSecondary,
                        fontWeight: FontWeight.w500,
                      ),
                ),
                const SizedBox(height: 4),
                InkWell(
                  onTap: () {
                    // TODO: Open URL in browser
                  },
                  child: Row(
                    children: [
                      Expanded(
                        child: Text(
                          url,
                          style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                                color: AppTheme.primaryColor,
                                decoration: TextDecoration.underline,
                              ),
                          maxLines: 2,
                          overflow: TextOverflow.ellipsis,
                        ),
                      ),
                      const SizedBox(width: 8),
                      const Icon(
                        Icons.open_in_new,
                        size: 16,
                        color: AppTheme.primaryColor,
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  String _formatDateTime(DateTime date) {
    return '${date.day.toString().padLeft(2, '0')}.${date.month.toString().padLeft(2, '0')}.${date.year} '
        '${date.hour.toString().padLeft(2, '0')}:${date.minute.toString().padLeft(2, '0')}';
  }
}
