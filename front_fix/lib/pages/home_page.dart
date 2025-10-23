import 'package:flutter/material.dart';
import 'package:fl_chart/fl_chart.dart';
import '../services/api_service.dart';
import '../design/home_design.dart';

class HomePage extends StatefulWidget {
  const HomePage({super.key});

  @override
  State<HomePage> createState() => _HomePageState();
}

class _HomePageState extends State<HomePage> {
  bool carregando = true;
  String erro = '';
  Map<String, dynamic>? analyticsData;

  @override
  void initState() {
    super.initState();
    _carregarDados();
  }

  Future<void> _carregarDados() async {
    setState(() {
      carregando = true;
      erro = '';
    });

    try {
      final user = await ApiService.getMe();
      final cnpj = user['cnpj'] ?? '';

      if (cnpj.isEmpty) {
        throw Exception("CNPJ não encontrado no perfil do restaurante");
      }

      final data = await ApiService.getAnalyticsData(cnpj);
      setState(() => analyticsData = data);
    } catch (e) {
      setState(() {
        erro = 'Erro ao carregar dados: $e';
      });
    } finally {
      setState(() => carregando = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    if (carregando) {
      return const Scaffold(
        body: Center(child: CircularProgressIndicator()),
      );
    }

    if (erro.isNotEmpty) {
      return Scaffold(
        appBar: AppBar(
          title: const Text('Análises de Fluxo'),
          backgroundColor: const Color.fromRGBO(46, 133, 157, 1),
        ),
        body: Center(
          child: Text(
            erro,
            style: const TextStyle(color: Colors.red, fontSize: 16),
            textAlign: TextAlign.center,
          ),
        ),
      );
    }

    final yolo = analyticsData?['yolo_analysis'] ?? {};
    final llama = analyticsData?['llama_analysis'] ?? {};

    // === YOLO MÉTRICAS ===
    final mediaYolo = (yolo['media_total'] ?? 0).toDouble();
    final picoYolo = (yolo['pico_total'] ?? 0).toInt();
    final totalYolo = (yolo['quantidade_atual']?['person'] ?? 0).toInt();

    // === LLAMA MÉTRICAS ===
    final mediaLlama = (llama['media_total']?['person'] ?? 0).toDouble();
    final picoLlama = (llama['pico_total']?['person'] ?? 0).toInt();
    final totalLlama = (llama['quantidade_atual']?['person'] ?? 0).toInt();

    // === MOCK DE GRÁFICO (substituir pelo histórico do backend quando disponível) ===
    final fluxoPessoas = List.generate(
      10,
      (i) => FlSpot(i.toDouble(), (i * 0.8 + 1.5)),
    );

    return HomeDesign(
      fluxoPessoas: fluxoPessoas,
      totalYolo: totalYolo,
      picoYolo: picoYolo,
      mediaYolo: mediaYolo,
      totalLlama: totalLlama,
      picoLlama: picoLlama,
      mediaLlama: mediaLlama,
    );
  }
}
