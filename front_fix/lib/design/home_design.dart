import 'package:flutter/material.dart';
import 'package:fl_chart/fl_chart.dart';

class HomeDesign extends StatelessWidget {
  final Color appBarColor;
  final Color iconColor;
  final String logoPath;
  final String logoAppBarPath;

  // 🔹 Dados do gráfico e estatísticas
  final List<FlSpot> fluxoPessoas;
  final int totalPessoas;
  final int picoPessoas;
  final double mediaPessoas;

  const HomeDesign({
    super.key,
    this.appBarColor = const Color.fromRGBO(46, 133, 157, 1),
    this.iconColor = const Color.fromRGBO(225, 105, 30, 1),
    this.logoPath = "logo.png",
    this.logoAppBarPath = "logo.png",
    required this.fluxoPessoas,
    required this.totalPessoas,
    required this.picoPessoas,
    required this.mediaPessoas,
  });

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text(
          "Análises de Fluxo de Pessoas",
          style: TextStyle(fontWeight: FontWeight.bold),
        ),
        backgroundColor: appBarColor,
        actions: [
          Padding(
            padding: const EdgeInsets.only(right: 16.0),
            child: Image.asset(
              logoAppBarPath,
              height: 50,
              fit: BoxFit.contain,
            ),
          ),
        ],
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          children: [
            // 🔸 Gráfico principal
            Expanded(
              child: Container(
                decoration: BoxDecoration(
                  color: Colors.grey[100],
                  borderRadius: BorderRadius.circular(12),
                  boxShadow: [
                    BoxShadow(
                      color: Colors.black12,
                      blurRadius: 6,
                      offset: const Offset(0, 2),
                    ),
                  ],
                ),
                padding: const EdgeInsets.all(12),
                child: fluxoPessoas.isEmpty
                    ? const Center(child: Text("Sem dados de fluxo disponíveis"))
                    : LineChart(
                        LineChartData(
                          titlesData: FlTitlesData(
                            leftTitles: AxisTitles(
                              sideTitles: SideTitles(showTitles: true),
                            ),
                            bottomTitles: AxisTitles(
                              sideTitles: SideTitles(showTitles: false),
                            ),
                          ),
                          gridData: FlGridData(show: true),
                          borderData: FlBorderData(show: true),
                          lineBarsData: [
                            LineChartBarData(
                              isCurved: true,
                              color: iconColor,
                              spots: fluxoPessoas,
                              belowBarData: BarAreaData(
                                show: true,
                                color: iconColor.withOpacity(0.2),
                              ),
                              dotData: FlDotData(show: false),
                            ),
                          ],
                        ),
                      ),
              ),
            ),
            const SizedBox(height: 20),

            // 🔹 Cards informativos
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceEvenly,
              children: [
                _infoCard(
                  icon: Icons.people,
                  label: "Total",
                  value: "$totalPessoas",
                  color: iconColor,
                ),
                _infoCard(
                  icon: Icons.trending_up,
                  label: "Pico",
                  value: "$picoPessoas",
                  color: Colors.redAccent,
                ),
                _infoCard(
                  icon: Icons.show_chart,
                  label: "Média",
                  value: mediaPessoas.toStringAsFixed(1),
                  color: Colors.blueAccent,
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  // 🔹 Widget auxiliar para cards de informação
  Widget _infoCard({
    required IconData icon,
    required String label,
    required String value,
    required Color color,
  }) {
    return Card(
      elevation: 3,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: Container(
        width: 100,
        height: 90,
        padding: const EdgeInsets.all(8),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(icon, color: color, size: 30),
            const SizedBox(height: 8),
            Text(value, style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
            Text(label, style: const TextStyle(fontSize: 14, color: Colors.grey)),
          ],
        ),
      ),
    );
  }
}
