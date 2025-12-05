import 'package:flutter/material.dart';
import '../theme/app_theme.dart';

class PlatformIcon extends StatelessWidget {
  final String platform;
  final double size;
  final Color? backgroundColor;
  final Color? iconColor;

  const PlatformIcon({
    super.key,
    required this.platform,
    this.size = 48,
    this.backgroundColor,
    this.iconColor,
  });

  IconData _getPlatformIcon() {
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

  Color _getPlatformColor() {
    switch (platform.toLowerCase()) {
      case 'telegram':
        return const Color(0xFF0088CC);
      case 'youtube':
        return const Color(0xFFFF0000);
      case 'vk':
        return const Color(0xFF0077FF);
      case 'rutube':
        return const Color(0xFFFF6B00);
      case 'twitch':
        return const Color(0xFF9146FF);
      default:
        return AppTheme.primaryColor;
    }
  }

  @override
  Widget build(BuildContext context) {
    final platformColor = _getPlatformColor();
    final bgColor = backgroundColor ?? platformColor.withValues(alpha: 0.1);
    final icColor = iconColor ?? platformColor;

    return Container(
      width: size,
      height: size,
      decoration: BoxDecoration(
        color: bgColor,
        shape: BoxShape.circle,
        border: Border.all(
          color: platformColor.withValues(alpha: 0.2),
          width: 2,
        ),
      ),
      child: Icon(
        _getPlatformIcon(),
        size: size * 0.6,
        color: icColor,
      ),
    );
  }
}

