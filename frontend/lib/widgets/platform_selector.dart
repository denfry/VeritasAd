import 'package:flutter/material.dart';
import '../theme/app_theme.dart';

class PlatformSelector extends StatelessWidget {
  final String selectedPlatform;
  final ValueChanged<String> onPlatformChanged;
  final List<Map<String, dynamic>> platforms;

  const PlatformSelector({
    super.key,
    required this.selectedPlatform,
    required this.onPlatformChanged,
    required this.platforms,
  });

  @override
  Widget build(BuildContext context) {
    return Wrap(
      spacing: 12,
      runSpacing: 12,
      children: platforms.map((platform) {
        final isSelected = selectedPlatform == platform['value'];
        final platformColor = _getPlatformColor(platform['value'] as String);

        return FilterChip(
          selected: isSelected,
          label: Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              Icon(
                platform['icon'] as IconData,
                size: 18,
                color: isSelected ? Colors.white : platformColor,
              ),
              const SizedBox(width: 6),
              Text(
                platform['label'] as String,
                style: TextStyle(
                  fontWeight: isSelected ? FontWeight.w600 : FontWeight.normal,
                  color: isSelected ? Colors.white : AppTheme.textPrimary,
                ),
              ),
            ],
          ),
          onSelected: (selected) {
            if (selected) {
              onPlatformChanged(platform['value'] as String);
            }
          },
          selectedColor: platformColor,
          checkmarkColor: Colors.white,
          side: BorderSide(
            color: isSelected ? platformColor : Colors.grey.shade300,
            width: isSelected ? 2 : 1,
          ),
          padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(12),
          ),
        );
      }).toList(),
    );
  }

  Color _getPlatformColor(String platform) {
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
}

