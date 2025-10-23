import 'package:flutter/material.dart';
import 'package:fl_chart/fl_chart.dart';
import 'dart:math' as math;

class HomeDesign extends StatelessWidget {
  final Color appBarColor;
  final Color iconColor;
  final String logoAppBarPath;

  final List<FlSpot> fluxoPessoas;
  final int totalYolo;
  final int picoYolo;
  final double mediaYolo;
  final int totalLlama;
  final int picoLlama;
  final double mediaLlama;

  const HomeDesign({
    super.key,
    this.appBarColor = const Color.fromRGBO(46, 133, 157, 1),
    this.iconColor = const Color.fromRGBO(225, 105, 30, 1),
    this.logoAppBarPath = "assets/logo.png",
    required this.fluxoPessoas,
    required this.totalYolo,
    required this.picoYolo,
    required this.mediaYolo,
    required this.totalLlama,
    required this.picoLlama,
    required this.mediaLlama,
  });

  ({double minX, double maxX, double minY, double maxY}) _calcBounds(List<FlSpot> pts) {
    if (pts.isEmpty) return (minX: 0, maxX: 1, minY: 0, maxY: 1);

    double minX = pts.map((p) => p.x).reduce(math.min);
    double maxX = pts.map((p) => p.x).reduce(math.max);
    double minY = pts.map((p) => p.y).reduce(math.min);
    double maxY = pts.map((p) => p.y).reduce(math.max);

    // Se o gráfico estiver "achatado", aumentar o range do eixo Y
    if (maxY == minY) {
      maxY += 1;
    }

    // margem extra para não colar nas bordas
    final padY = (maxY - minY) * 0.15;
    return (
      minX: minX,
      maxX: maxX,
      minY: math.max(0, minY - padY),
      maxY: maxY + padY
    );
  }

  double _chooseInterval(double min, double max) {
    final range = (max - min).abs();
    if (range <= 5) return 1;
    if (range <= 10) return 2;
    if (range <= 25) return 5;
    if (range <= 50) return 10;
    return range / 10;
  }

  @override
  Widget build(BuildContext context) {
    final bounds = _calcBounds(fluxoPessoas);

    debugPrint('📊 Dados recebidos para gráfico: $fluxoPessoas');
    debugPrint('📉 Bounds calculados: $bounds');

    return Scaffold(
      appBar: AppBar(
        title: const Text("Análises de Fluxo de Pessoas", style: TextStyle(fontWeight: FontWeight.bold)),
        backgroundColor: appBarColor,
        actions: [
          Padding(
            padding: const EdgeInsets.only(right: 16.0),
            child: Image.asset(logoAppBarPath, height: 45, fit: BoxFit.contain),
          ),
        ],
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          children: [
            Expanded(
              child: Container(
                decoration: BoxDecoration(
                  color: Colors.grey[100],
                  borderRadius: BorderRadius.circular(12),
                  boxShadow: const [BoxShadow(color: Colors.black12, blurRadius: 6, offset: Offset(0, 2))],
                ),
                padding: const EdgeInsets.all(12),
                child: fluxoPessoas.isEmpty
                    ? const Center(child: Text("Sem dados de fluxo disponíveis"))
                    : LineChart(
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
                                interval: 1,
                                getTitlesWidget: (value, _) => Text(
                                  value.toInt().toString(),
                                  style: const TextStyle(fontSize: 10, color: Colors.black54),
                                ),
                              ),
                            ),
                            leftTitles: AxisTitles(
                              sideTitles: SideTitles(
                                showTitles: true,
                                interval: _chooseInterval(bounds.minY, bounds.maxY),
                                getTitlesWidget: (value, _) => Text(
                                  value.toInt().toString(),
                                  style: const TextStyle(fontSize: 10, color: Colors.black54),
                                ),
                              ),
                            ),
                            topTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
                            rightTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
                          ),
                          lineBarsData: [
                            LineChartBarData(
                              isCurved: true,
                              color: iconColor,
                              barWidth: 3,
                              spots: fluxoPessoas,
                              belowBarData: BarAreaData(
                                show: true,
                                color: iconColor.withValues(alpha: 0.18),
                              ),
                              dotData: const FlDotData(show: true),
                            ),
                          ],
                        ),
                      ),
              ),
            ),
            const SizedBox(height: 20),
            _infoSection(
              title: "YOLO - Análise Visual",
              color: iconColor,
              total: totalYolo,
              pico: picoYolo,
              media: mediaYolo,
            ),
            const SizedBox(height: 12),
            _infoSection(
              title: "LLaMA - Análise Cognitiva",
              color: appBarColor,
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
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            Row(
              children: [
                Icon(Icons.analytics, size: 40, color: color),
                const SizedBox(width: 12),
                Text(title, style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 18)),
              ],
            ),
            const SizedBox(height: 16),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceEvenly,
              children: [
                _infoCard(icon: Icons.people, label: "Quantidade atual", value: "$total", color: color),
                _infoCard(icon: Icons.trending_up, label: "Pico", value: "$pico", color: Colors.redAccent),
                _infoCard(icon: Icons.show_chart, label: "Média", value: media.toStringAsFixed(1), color: Colors.blueAccent),
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
        Text(value, style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
        Text(label, style: const TextStyle(color: Colors.grey, fontSize: 13)),
      ],
    );
  }
}
