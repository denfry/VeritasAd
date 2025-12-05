import 'package:flutter/material.dart';
import '../models/job_model.dart';
import '../theme/app_theme.dart';
import 'platform_icon.dart';
import 'status_chip.dart';

class JobCard extends StatelessWidget {
  final JobModel job;
  final VoidCallback onTap;
  final VoidCallback? onRefresh;
  final bool isProcessing;

  const JobCard({
    super.key,
    required this.job,
    required this.onTap,
    this.onRefresh,
    this.isProcessing = false,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Card(
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 6),
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(16),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Row(
            children: [
              PlatformIcon(
                platform: job.platform,
                size: 56,
              ),
              const SizedBox(width: 16),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Expanded(
                          child: Text(
                            job.platform.toUpperCase(),
                            style: theme.textTheme.titleMedium?.copyWith(
                              fontWeight: FontWeight.bold,
                              letterSpacing: 0.5,
                            ),
                          ),
                        ),
                        StatusChip(
                          status: job.status,
                          label: job.statusLabel,
                          compact: true,
                        ),
                      ],
                    ),
                    const SizedBox(height: 8),
                    Row(
                      children: [
                        const Icon(
                          Icons.access_time,
                          size: 14,
                          color: AppTheme.textTertiary,
                        ),
                        const SizedBox(width: 4),
                        Text(
                          _formatDate(job.createdAt),
                          style: theme.textTheme.bodySmall?.copyWith(
                            color: AppTheme.textTertiary,
                          ),
                        ),
                      ],
                    ),
                    if (job.errorMessage != null) ...[
                      const SizedBox(height: 6),
                      Row(
                        children: [
                          const Icon(
                            Icons.error_outline,
                            size: 14,
                            color: AppTheme.errorColor,
                          ),
                          const SizedBox(width: 4),
                          Expanded(
                            child: Text(
                              job.errorMessage!,
                              style: theme.textTheme.bodySmall?.copyWith(
                                color: AppTheme.errorColor,
                              ),
                              maxLines: 1,
                              overflow: TextOverflow.ellipsis,
                            ),
                          ),
                        ],
                      ),
                    ],
                  ],
                ),
              ),
              const SizedBox(width: 8),
              if (isProcessing && onRefresh != null)
                IconButton(
                  icon: const SizedBox(
                    width: 20,
                    height: 20,
                    child: CircularProgressIndicator(strokeWidth: 2),
                  ),
                  onPressed: onRefresh,
                  tooltip: 'Обновить',
                )
              else
                const Icon(
                  Icons.chevron_right,
                  color: AppTheme.textTertiary,
                ),
            ],
          ),
        ),
      ),
    );
  }

  String _formatDate(DateTime date) {
    final now = DateTime.now();
    final diff = now.difference(date);

    if (diff.inDays > 0) {
      return '${diff.inDays} дн. назад';
    } else if (diff.inHours > 0) {
      return '${diff.inHours} ч. назад';
    } else if (diff.inMinutes > 0) {
      return '${diff.inMinutes} мин. назад';
    } else {
      return 'Только что';
    }
  }
}

