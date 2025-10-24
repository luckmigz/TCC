import 'package:flutter/material.dart';
import 'package:fl_chart/fl_chart.dart';
import 'dart:math' as math;
import 'package:intl/intl.dart';

class HomeDesign extends StatelessWidget {
  final Color appBarColor;
  final Color yoloColor;
  final Color llamaColor;
  final String logoAppBarPath;

  final List<FlSpot> fluxoYolo;
  final List<FlSpot> fluxoLlama;

  final int totalYolo;
  final int picoYolo;
  final double mediaYolo;
  final int totalLlama;
  final int picoLlama;
  final double mediaLlama;

  const HomeDesign({
    super.key,
    this.appBarColor = const Color.fromRGBO(46, 133, 157, 1),
    this.yoloColor = const Color.fromRGBO(225, 105, 30, 1),
    this.llamaColor = const Color.fromRGBO(46, 133, 157, 1),
    this.logoAppBarPath = "assets/logo.png",
    required this.fluxoYolo,
    required this.fluxoLlama,
    required this.totalYolo,
    required this.picoYolo,
    required this.mediaYolo,
    required this.totalLlama,
    required this.picoLlama,
    required this.mediaLlama,
  });

  // 🔹 Calcula os limites dinâmicos
  ({double minX, double maxX, double minY, double maxY}) _calcBounds() {
  final allPoints = [...fluxoYolo, ...fluxoLlama];
  if (allPoints.isEmpty) return (minX: 0, maxX: 1, minY: 0, maxY: 1);

  double minX = allPoints.map((p) => p.x).reduce(math.min);
  double maxX = allPoints.map((p) => p.x).reduce(math.max);
  double maxY = allPoints.map((p) => p.y).reduce(math.max);

  // 🔹 Corrige o último valor do eixo Y para o próximo número redondo acima
  const double step = 2.0; // 👈 agora é double
  double maxYAdjusted = ((maxY / step).ceilToDouble() + 1) * step;

  return (
    minX: minX,
    maxX: maxX,
    minY: 0.0,
    maxY: maxYAdjusted
  );
}
  @override
  Widget build(BuildContext context) {
    final bounds = _calcBounds();

    return Scaffold(
      appBar: AppBar(
        title: const Text(
          "Fluxo de Pessoas ao Longo do Tempo",
          style: TextStyle(fontWeight: FontWeight.bold),
        ),
        backgroundColor: appBarColor,
        actions: [
          Padding(
            padding: const EdgeInsets.only(right: 16.0),
            child:
                Image.asset(logoAppBarPath, height: 45, fit: BoxFit.contain),
          ),
        ],
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          children: [
            // 🔹 Scroll horizontal apenas
            Expanded(
              child: SingleChildScrollView(
                scrollDirection: Axis.horizontal,
                child: SizedBox(
                  width: math.max(MediaQuery.of(context).size.width,
                      (fluxoYolo.length * 100).toDouble()),
                  child: LineChart(
                    LineChartData(
                      minX: bounds.minX,
                      maxX: bounds.maxX,
                      minY: bounds.minY,
                      maxY: bounds.maxY,
                      gridData: const FlGridData(show: true),
                      borderData: FlBorderData(show: true),
                      titlesData: FlTitlesData(
                        bottomTitles: AxisTitles(
                          sideTitles: SideTitles(
                            showTitles: true,
                            reservedSize: 40,
                            interval: ((bounds.maxX - bounds.minX) / 4)
                                .clamp(1, 9999999),
                            getTitlesWidget: (value, _) {
                              final date = DateTime
                                  .fromMillisecondsSinceEpoch(
                                      value.toInt() * 1000);
                              return Text(
                                DateFormat.Hm().format(date),
                                style: const TextStyle(
                                    fontSize: 10, color: Colors.black54),
                              );
                            },
                          ),
                        ),
                        leftTitles: AxisTitles(
                          sideTitles: SideTitles(
                            showTitles: true,
                            interval: ((bounds.maxY - bounds.minY) / 5)
                                .clamp(1, 10),
                            getTitlesWidget: (value, _) => Text(
                              value.toInt().toString(),
                              style: const TextStyle(
                                  fontSize: 10, color: Colors.black54),
                            ),
                          ),
                        ),
                        topTitles: const AxisTitles(
                            sideTitles: SideTitles(showTitles: false)),
                        rightTitles: const AxisTitles(
                            sideTitles: SideTitles(showTitles: false)),
                      ),
                      lineTouchData: LineTouchData(
                        enabled: true,
                        touchTooltipData: LineTouchTooltipData(
                          getTooltipItems: (touchedSpots) {
                            return touchedSpots.map((spot) {
                              final time =
                                  DateTime.fromMillisecondsSinceEpoch(
                                      spot.x.toInt() * 1000);
                              return LineTooltipItem(
                                '${DateFormat.Hm().format(time)}\nY: ${spot.y.toStringAsFixed(1)}',
                                const TextStyle(color: Colors.white),
                              );
                            }).toList();
                          },
                        ),
                      ),
                      lineBarsData: [
                        // 🟧 YOLO
                        LineChartBarData(
                          isCurved: true,
                          color: yoloColor,
                          barWidth: 3,
                          spots: fluxoYolo,
                          belowBarData: BarAreaData(
                            show: true,
                            color: yoloColor.withOpacity(0.2),
                          ),
                          dotData: const FlDotData(show: true),
                        ),
                        // 🔵 LLaMA
                        LineChartBarData(
                          isCurved: true,
                          color: llamaColor,
                          barWidth: 3,
                          spots: fluxoLlama,
                          belowBarData: BarAreaData(
                            show: true,
                            color: llamaColor.withOpacity(0.2),
                          ),
                          dotData: const FlDotData(show: true),
                        ),
                      ],
                    ),
                  ),
                ),
              ),
            ),
            const SizedBox(height: 20),

            // 🔹 Cards de resumo
            _infoSection(
              title: "YOLO - Análise Visual",
              color: yoloColor,
              total: totalYolo,
              pico: picoYolo,
              media: mediaYolo,
            ),
            const SizedBox(height: 12),
            _infoSection(
              title: "LLaMA - Análise Cognitiva",
              color: llamaColor,
              total: totalLlama,
              pico: picoLlama,
              media: mediaLlama,
            ),
          ],
        ),
      ),
    );
  }

  Widget _infoSection({
    required String title,
    required Color color,
    required int total,
    required int pico,
    required double media,
  }) {
    return Card(
      elevation: 4,
      shape:
          RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            Row(
              children: [
                Icon(Icons.analytics, size: 40, color: color),
                const SizedBox(width: 12),
                Text(title,
                    style: const TextStyle(
                        fontWeight: FontWeight.bold, fontSize: 18)),
              ],
            ),
            const SizedBox(height: 16),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceEvenly,
              children: [
                _infoCard(
                    icon: Icons.people,
                    label: "Total",
                    value: "$total",
                    color: color),
                _infoCard(
                    icon: Icons.trending_up,
                    label: "Pico",
                    value: "$pico",
                    color: Colors.redAccent),
                _infoCard(
                    icon: Icons.show_chart,
                    label: "Média",
                    value: media.toStringAsFixed(1),
                    color: Colors.blueAccent),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _infoCard({
    required IconData icon,
    required String label,
    required String value,
    required Color color,
  }) {
    return Column(
      children: [
        Icon(icon, color: color, size: 28),
        const SizedBox(height: 6),
        Text(value,
            style:
                const TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
        Text(label,
            style: const TextStyle(color: Colors.grey, fontSize: 13)),
      ],
    );
  }
}
