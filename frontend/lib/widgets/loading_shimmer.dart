import 'package:flutter/material.dart';

class LoadingShimmer extends StatefulWidget {
  final double width;
  final double height;
  final BorderRadius? borderRadius;

  const LoadingShimmer({
    super.key,
    required this.width,
    required this.height,
    this.borderRadius,
  });

  @override
  State<LoadingShimmer> createState() => _LoadingShimmerState();
}

class _LoadingShimmerState extends State<LoadingShimmer>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      duration: const Duration(milliseconds: 1500),
      vsync: this,
    )..repeat();
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: _controller,
      builder: (context, child) {
        return CustomPaint(
          painter: ShimmerPainter(
            animationValue: _controller.value,
            borderRadius: widget.borderRadius,
          ),
          child: SizedBox(
            width: widget.width,
            height: widget.height,
          ),
        );
      },
    );
  }
}

class ShimmerPainter extends CustomPainter {
  final double animationValue;
  final BorderRadius? borderRadius;

  ShimmerPainter({
    required this.animationValue,
    this.borderRadius,
  });

  @override
  void paint(Canvas canvas, Size size) {
    final gradient = LinearGradient(
      begin: Alignment(-1.0 - 2 * animationValue, 0.0),
      end: Alignment(1.0 - 2 * animationValue, 0.0),
      colors: const [
        Color(0xFFEBEBF4),
        Color(0xFFF4F4F4),
        Color(0xFFEBEBF4),
      ],
      stops: const [0.0, 0.5, 1.0],
    );

    final paint = Paint()
      ..shader = gradient.createShader(
        Rect.fromLTWH(0, 0, size.width, size.height),
      );

    final rect = Rect.fromLTWH(0, 0, size.width, size.height);
    final radius = borderRadius ?? BorderRadius.circular(8);

    final path = Path()
      ..addRRect(radius.resolve(TextDirection.ltr).toRRect(rect));

    canvas.drawPath(path, paint);
  }

  @override
  bool shouldRepaint(ShimmerPainter oldDelegate) {
    return oldDelegate.animationValue != animationValue;
  }
}

