import 'package:flutter/material.dart';
import 'package:fl_chart/fl_chart.dart';
import '../services/user_service.dart';
import '../services/api_service.dart';

class HomePage extends StatefulWidget {
  const HomePage({super.key});

  @override
  State<HomePage> createState() => _HomePageState();
}

class _HomePageState extends State<HomePage> {
  List<FlSpot> fluxoPessoas = [];
  bool carregando = true;
  String erro = '';

  @override
  void initState() {
    super.initState();
    _carregarFluxoPessoas();
  }

  Future<void> _carregarFluxoPessoas() async {
    try {
      final String cnpj = UserService.cnpj;
      final data = await ApiService.getAnalyticsData(cnpj);

      // Espera-se algo como: { "fluxo": [ {"timestamp": "...", "pessoas": 10}, ... ] }
      final List<dynamic> fluxo = data['fluxo'] ?? [];

      setState(() {
        fluxoPessoas = List<FlSpot>.generate(
          fluxo.length,
          (i) => FlSpot(
            i.toDouble(),
            (fluxo[i]['pessoas'] as num).toDouble(),
          ),
        );
        carregando = false;
      });
    } catch (e) {
      setState(() {
        erro = 'Erro: $e';
        carregando = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text(
          'Fluxo de Pessoas',
          style: TextStyle(fontWeight: FontWeight.bold),
        ),
        backgroundColor: const Color.fromRGBO(225, 105, 30, 1),
      ),
      body: Center(
        child: carregando
            ? const CircularProgressIndicator()
            : erro.isNotEmpty
                ? Text(erro, style: const TextStyle(color: Colors.red))
                : Padding(
                    padding: const EdgeInsets.all(16.0),
                    child: LineChart(
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
                            color: const Color.fromRGBO(225, 105, 30, 1),
                            spots: fluxoPessoas,
                            belowBarData: BarAreaData(show: false),
                          ),
                        ],
                      ),
                    ),
                  ),
      ),
    );
  }
}
