import 'package:dio/dio.dart';
import '../models/job_model.dart';

class ApiService {
  late final Dio _dio;
  String? _apiKey;

  ApiService({String? baseUrl, String? apiKey}) {
    _apiKey = apiKey ?? 'dev-key';
    _dio = Dio(BaseOptions(
      baseUrl: baseUrl ?? 'http://localhost:8000',
      connectTimeout: const Duration(seconds: 30),
      receiveTimeout: const Duration(seconds: 60),
      headers: {
        'X-API-Key': _apiKey,
      },
    ));
  }

  void setApiKey(String apiKey) {
    _apiKey = apiKey;
    _dio.options.headers['X-API-Key'] = apiKey;
  }

  String? get apiKey => _apiKey;

  Future<JobModel> createJob({
    required String platform,
    required String url,
  }) async {
    try {
      final formData = FormData.fromMap({
        'platform': platform,
        'url': url,
      });

      final response = await _dio.post('/jobs', data: formData);
      return JobModel.fromJson(response.data);
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  Future<JobModel> getJob(String jobId) async {
    try {
      final response = await _dio.get('/jobs/$jobId');
      return JobModel.fromJson(response.data);
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  Future<Map<String, dynamic>> getJobMetadata(String resultPath) async {
    // Если есть result_url, можно загрузить оттуда
    // Пока возвращаем путь для локального чтения
    return {'path': resultPath};
  }

  String _handleError(DioException e) {
    if (e.response != null) {
      final data = e.response!.data;
      if (data is Map && data.containsKey('detail')) {
        return data['detail'] as String;
      }
      return 'Ошибка сервера: ${e.response!.statusCode}';
    } else if (e.type == DioExceptionType.connectionTimeout) {
      return 'Таймаут подключения';
    } else if (e.type == DioExceptionType.receiveTimeout) {
      return 'Таймаут получения данных';
    } else {
      return e.message ?? 'Неизвестная ошибка';
    }
  }
}

