import 'package:flutter/material.dart';

class JobModel {
  final String id;
  final String status;
  final String platform;
  final String inputType;
  final DateTime createdAt;
  final DateTime updatedAt;
  final String? resultPath;
  final String? resultUrl;
  final String? mediaPath;
  final String? mediaUrl;
  final String? inputUrl;
  final String? errorMessage;

  JobModel({
    required this.id,
    required this.status,
    required this.platform,
    required this.inputType,
    required this.createdAt,
    required this.updatedAt,
    this.resultPath,
    this.resultUrl,
    this.mediaPath,
    this.mediaUrl,
    this.inputUrl,
    this.errorMessage,
  });

  factory JobModel.fromJson(Map<String, dynamic> json) {
    return JobModel(
      id: json['id'] as String,
      status: json['status'] as String,
      platform: json['platform'] as String,
      inputType: json['input_type'] as String,
      createdAt: DateTime.parse(json['created_at'] as String),
      updatedAt: DateTime.parse(json['updated_at'] as String),
      resultPath: json['result_path'] as String?,
      resultUrl: json['result_url'] as String?,
      mediaPath: json['media_path'] as String?,
      mediaUrl: json['media_url'] as String?,
      inputUrl: json['input_url'] as String?,
      errorMessage: json['error_message'] as String?,
    );
  }

  bool get isCompleted => status == 'completed';
  bool get isProcessing => status == 'processing';
  bool get isPending => status == 'pending';
  bool get isFailed => status == 'failed';

  String get statusLabel {
    switch (status) {
      case 'pending':
        return 'Ожидание';
      case 'processing':
        return 'Обработка';
      case 'completed':
        return 'Завершено';
      case 'failed':
        return 'Ошибка';
      default:
        return status;
    }
  }

  IconData get platformIcon {
    switch (platform.toLowerCase()) {
      case 'telegram':
        return Icons.telegram;
      case 'youtube':
        return Icons.play_circle;
      case 'vk':
        return Icons.people;
      case 'rutube':
        return Icons.video_library;
      case 'twitch':
        return Icons.sports_esports;
      default:
        return Icons.language;
    }
  }
}

