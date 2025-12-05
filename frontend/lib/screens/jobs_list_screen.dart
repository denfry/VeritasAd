import 'package:flutter/material.dart';
import '../models/job_model.dart';
import '../services/api_service.dart';
import '../theme/app_theme.dart';
import '../widgets/job_card.dart';
import '../widgets/empty_state.dart';
import 'job_detail_screen.dart';
import 'create_job_screen.dart';

enum SortOption {
  newest,
  oldest,
  status,
  platform,
}

enum FilterOption {
  all,
  pending,
  processing,
  completed,
  failed,
}

class JobsListScreen extends StatefulWidget {
  final ApiService apiService;

  const JobsListScreen({super.key, required this.apiService});

  @override
  State<JobsListScreen> createState() => _JobsListScreenState();
}

class _JobsListScreenState extends State<JobsListScreen> {
  List<JobModel> _allJobs = [];
  List<JobModel> _filteredJobs = [];
  bool _isLoading = true;
  String? _error;
  SortOption _sortOption = SortOption.newest;
  FilterOption _filterOption = FilterOption.all;
  String _searchQuery = '';

  @override
  void initState() {
    super.initState();
    _loadJobs();
  }

  Future<void> _loadJobs() async {
    setState(() {
      _isLoading = true;
      _error = null;
    });

    try {
      // TODO: Replace with actual API call when backend is ready
      // final jobs = await widget.apiService.getJobs();
      // setState(() {
      //   _allJobs = jobs;
      //   _applyFilters();
      // });

      // Temporary: Simulate loading
      await Future.delayed(const Duration(milliseconds: 500));

      setState(() {
        _allJobs = [];
        _applyFilters();
      });
    } catch (e) {
      setState(() {
        _error = e.toString();
      });
    } finally {
      setState(() {
        _isLoading = false;
      });
    }
  }

  void _applyFilters() {
    var filtered = List<JobModel>.from(_allJobs);

    // Apply search filter
    if (_searchQuery.isNotEmpty) {
      filtered = filtered.where((job) {
        return job.platform.toLowerCase().contains(_searchQuery.toLowerCase()) ||
            job.id.toLowerCase().contains(_searchQuery.toLowerCase()) ||
            (job.inputUrl?.toLowerCase().contains(_searchQuery.toLowerCase()) ?? false);
      }).toList();
    }

    // Apply status filter
    if (_filterOption != FilterOption.all) {
      filtered = filtered.where((job) {
        switch (_filterOption) {
          case FilterOption.pending:
            return job.status == 'pending';
          case FilterOption.processing:
            return job.status == 'processing';
          case FilterOption.completed:
            return job.status == 'completed';
          case FilterOption.failed:
            return job.status == 'failed';
          default:
            return true;
        }
      }).toList();
    }

    // Apply sorting
    filtered.sort((a, b) {
      switch (_sortOption) {
        case SortOption.newest:
          return b.createdAt.compareTo(a.createdAt);
        case SortOption.oldest:
          return a.createdAt.compareTo(b.createdAt);
        case SortOption.status:
          return a.status.compareTo(b.status);
        case SortOption.platform:
          return a.platform.compareTo(b.platform);
      }
    });

    setState(() {
      _filteredJobs = filtered;
    });
  }

  Future<void> _refreshJob(String jobId) async {
    try {
      final job = await widget.apiService.getJob(jobId);
      setState(() {
        final index = _allJobs.indexWhere((j) => j.id == jobId);
        if (index != -1) {
          _allJobs[index] = job;
          _applyFilters();
        }
      });
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Ошибка обновления: $e'),
            backgroundColor: AppTheme.errorColor,
          ),
        );
      }
    }
  }

  void _navigateToCreate() async {
    final result = await Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => CreateJobScreen(apiService: widget.apiService),
      ),
    );
    if (result == true) {
      _loadJobs();
    }
  }

  void _navigateToDetail(JobModel job) async {
    await Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => JobDetailScreen(
          job: job,
          apiService: widget.apiService,
        ),
      ),
    );
    _refreshJob(job.id);
  }

  void _showFilterDialog() {
    showModalBottomSheet(
      context: context,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (context) => _FilterBottomSheet(
        currentFilter: _filterOption,
        currentSort: _sortOption,
        onFilterChanged: (filter) {
          setState(() {
            _filterOption = filter;
            _applyFilters();
          });
          Navigator.pop(context);
        },
        onSortChanged: (sort) {
          setState(() {
            _sortOption = sort;
            _applyFilters();
          });
          Navigator.pop(context);
        },
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: SafeArea(
        child: Column(
          children: [
            _buildHeader(),
            if (_searchQuery.isNotEmpty || _filterOption != FilterOption.all)
              _buildActiveFilters(),
            Expanded(
              child: _isLoading
                  ? _buildLoadingState()
                  : _error != null
                      ? _buildErrorState()
                      : _filteredJobs.isEmpty
                          ? _buildEmptyState()
                          : _buildJobsList(),
            ),
          ],
        ),
      ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: _navigateToCreate,
        icon: const Icon(Icons.add),
        label: const Text('Новая задача'),
        backgroundColor: AppTheme.primaryColor,
      ),
    );
  }

  Widget _buildHeader() {
    return Container(
      padding: const EdgeInsets.fromLTRB(16, 12, 16, 8),
      decoration: BoxDecoration(
        color: Theme.of(context).scaffoldBackgroundColor,
        boxShadow: [
          BoxShadow(
            color: Colors.black.withValues(alpha: 0.05),
            blurRadius: 4,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Column(
        children: [
          Row(
            children: [
              Expanded(
                child: Text(
                  'Задачи анализа',
                  style: Theme.of(context).textTheme.displaySmall?.copyWith(
                        fontWeight: FontWeight.bold,
                      ),
                ),
              ),
              IconButton(
                icon: const Icon(Icons.filter_list),
                onPressed: _showFilterDialog,
                tooltip: 'Фильтры и сортировка',
              ),
            ],
          ),
          const SizedBox(height: 8),
          _buildSearchBar(),
        ],
      ),
    );
  }

  Widget _buildSearchBar() {
    return TextField(
      onChanged: (value) {
        setState(() {
          _searchQuery = value;
          _applyFilters();
        });
      },
      decoration: InputDecoration(
        hintText: 'Поиск по платформе, ID или URL...',
        prefixIcon: const Icon(Icons.search),
        suffixIcon: _searchQuery.isNotEmpty
            ? IconButton(
                icon: const Icon(Icons.clear),
                onPressed: () {
                  setState(() {
                    _searchQuery = '';
                    _applyFilters();
                  });
                },
              )
            : null,
        filled: true,
        fillColor: Colors.grey.shade50,
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: BorderSide.none,
        ),
        contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
      ),
    );
  }

  Widget _buildActiveFilters() {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      color: AppTheme.primaryColor.withValues(alpha: 0.05),
      child: Row(
        children: [
          if (_filterOption != FilterOption.all) ...[
            Chip(
              label: Text(_getFilterLabel(_filterOption)),
              onDeleted: () {
                setState(() {
                  _filterOption = FilterOption.all;
                  _applyFilters();
                });
              },
              backgroundColor: AppTheme.primaryColor.withValues(alpha: 0.1),
              deleteIconColor: AppTheme.primaryColor,
            ),
            const SizedBox(width: 8),
          ],
          Expanded(
            child: Text(
              'Найдено: ${_filteredJobs.length}',
              style: Theme.of(context).textTheme.bodySmall,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildLoadingState() {
    return const Center(
      child: CircularProgressIndicator(),
    );
  }

  Widget _buildErrorState() {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(
              Icons.error_outline,
              size: 64,
              color: AppTheme.errorColor,
            ),
            const SizedBox(height: 16),
            Text(
              'Ошибка загрузки',
              style: Theme.of(context).textTheme.titleLarge,
            ),
            const SizedBox(height: 8),
            Text(
              _error!,
              style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                    color: AppTheme.textSecondary,
                  ),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 24),
            ElevatedButton.icon(
              onPressed: _loadJobs,
              icon: const Icon(Icons.refresh),
              label: const Text('Повторить'),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildEmptyState() {
    return EmptyState(
      icon: Icons.inbox_outlined,
      title: _allJobs.isEmpty
          ? 'Нет задач'
          : 'Задачи не найдены',
      subtitle: _allJobs.isEmpty
          ? 'Создайте новую задачу для анализа контента'
          : 'Попробуйте изменить фильтры поиска',
      actionLabel: 'Создать задачу',
      onAction: _navigateToCreate,
    );
  }

  Widget _buildJobsList() {
    return RefreshIndicator(
      onRefresh: _loadJobs,
      child: ListView.builder(
        padding: const EdgeInsets.symmetric(vertical: 8),
        itemCount: _filteredJobs.length,
        itemBuilder: (context, index) {
          final job = _filteredJobs[index];
          return JobCard(
            job: job,
            onTap: () => _navigateToDetail(job),
            onRefresh: () => _refreshJob(job.id),
            isProcessing: job.isProcessing,
          );
        },
      ),
    );
  }

  String _getFilterLabel(FilterOption filter) {
    switch (filter) {
      case FilterOption.pending:
        return 'Ожидание';
      case FilterOption.processing:
        return 'Обработка';
      case FilterOption.completed:
        return 'Завершено';
      case FilterOption.failed:
        return 'Ошибка';
      default:
        return 'Все';
    }
  }
}

class _FilterBottomSheet extends StatelessWidget {
  final FilterOption currentFilter;
  final SortOption currentSort;
  final ValueChanged<FilterOption> onFilterChanged;
  final ValueChanged<SortOption> onSortChanged;

  const _FilterBottomSheet({
    required this.currentFilter,
    required this.currentSort,
    required this.onFilterChanged,
    required this.onSortChanged,
  });

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.all(24),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Фильтры и сортировка',
            style: Theme.of(context).textTheme.titleLarge?.copyWith(
                  fontWeight: FontWeight.bold,
                ),
          ),
          const SizedBox(height: 24),
          Text(
            'Статус',
            style: Theme.of(context).textTheme.titleMedium,
          ),
          const SizedBox(height: 12),
          Wrap(
            spacing: 8,
            children: FilterOption.values.map((filter) {
              return FilterChip(
                selected: currentFilter == filter,
                label: Text(_getFilterLabel(filter)),
                onSelected: (selected) {
                  if (selected) onFilterChanged(filter);
                },
              );
            }).toList(),
          ),
          const SizedBox(height: 24),
          Text(
            'Сортировка',
            style: Theme.of(context).textTheme.titleMedium,
          ),
          const SizedBox(height: 12),
          Wrap(
            spacing: 8,
            children: SortOption.values.map((sort) {
              return FilterChip(
                selected: currentSort == sort,
                label: Text(_getSortLabel(sort)),
                onSelected: (selected) {
                  if (selected) onSortChanged(sort);
                },
              );
            }).toList(),
          ),
          const SizedBox(height: 24),
        ],
      ),
    );
  }

  String _getFilterLabel(FilterOption filter) {
    switch (filter) {
      case FilterOption.all:
        return 'Все';
      case FilterOption.pending:
        return 'Ожидание';
      case FilterOption.processing:
        return 'Обработка';
      case FilterOption.completed:
        return 'Завершено';
      case FilterOption.failed:
        return 'Ошибка';
    }
  }

  String _getSortLabel(SortOption sort) {
    switch (sort) {
      case SortOption.newest:
        return 'Сначала новые';
      case SortOption.oldest:
        return 'Сначала старые';
      case SortOption.status:
        return 'По статусу';
      case SortOption.platform:
        return 'По платформе';
    }
  }
}
