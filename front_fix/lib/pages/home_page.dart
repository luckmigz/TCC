import 'dart:async';
import 'package:flutter/material.dart';
import 'package:fl_chart/fl_chart.dart';
import '../services/api_service.dart';
import '../design/home_design.dart';
import 'login_page.dart';

class HomePage extends StatefulWidget {
  const HomePage({super.key});

  @override
  State<HomePage> createState() => _HomePageState();
}

class _HomePageState extends State<HomePage> {
  bool carregando = true;
  String erro = '';
  Map<String, dynamic>? analyticsData;
  Timer? _timer; // 🔁 Timer de atualização automática

  @override
  void initState() {
    super.initState();
    _carregarDados(); // 🔹 Chamada imediata
    _iniciarAtualizacaoPeriodica(); // 🔹 Atualização automática
  }

  void _iniciarAtualizacaoPeriodica() {
    _timer?.cancel();
    // Atualiza a cada 5 minutos (300 segundos)
    _timer = Timer.periodic(const Duration(minutes: 5), (_) {
      _carregarDados();
    });
  }

  @override
  void dispose() {
    _timer?.cancel(); // 🔹 Cancela o timer ao sair da tela
    super.dispose();
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

      // 🔹 Atualiza o estado apenas se o widget ainda estiver montado
      if (mounted) {
        setState(() => analyticsData = data);
      }
    } catch (e) {
      if (!mounted) return;
      // Se o token expirou, volta para a tela de login
      if (e is AuthExpiredException) {
        Navigator.of(context, rootNavigator: true).pushAndRemoveUntil(
          MaterialPageRoute(builder: (_) => const LoginPage()),
          (route) => false,
        );
        return;
      }
      setState(() {
        erro = 'Erro ao carregar dados: $e';
      });
    } finally {
      if (mounted) {
        setState(() => carregando = false);
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    if (carregando && analyticsData == null) {
      // primeira carga
      return const Scaffold(
        body: Center(child: CircularProgressIndicator()),
      );
    }

    if (erro.isNotEmpty && analyticsData == null) {
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
    final timestampData =
        analyticsData?['timestamp']?['\$date']?['\$numberLong'];

  // Normaliza timestamp vindo da API: aceita segundos ou milissegundos
  final nowMs = DateTime.now().millisecondsSinceEpoch;
  final parsedTs = timestampData != null
    ? int.tryParse(timestampData.toString())
    : null;
  final int timestampMs = parsedTs == null
    ? nowMs
    : (parsedTs < 1000000000000 ? parsedTs * 1000 : parsedTs); // se vier em segundos, converte para ms
  final double baseX = timestampMs / 1000.0; // segundos como double

    // === YOLO ===
    final totalYolo = (yolo['quantidade_atual']?['person'] ?? 0).toDouble();
    final mediaYolo = (yolo['media_total'] ?? 0).toDouble();
    final picoYolo = (yolo['pico_total'] ?? 0).toDouble();

    // === LLaMA ===
    final totalLlama = (llama['quantidade_atual']?['person'] ?? 0).toDouble();
    final mediaLlama = (llama['media_total']?['person'] ?? 0).toDouble();
    final picoLlama = (llama['pico_total']?['person'] ?? 0).toDouble();

    // === PONTOS DO GRÁFICO ===
    final fluxoYolo = [
      FlSpot(baseX - 3600.0, mediaYolo),
      FlSpot(baseX - 1800.0, picoYolo),
      FlSpot(baseX, totalYolo),
    ];

    final fluxoLlama = [
      FlSpot(baseX - 3600.0, mediaLlama),
      FlSpot(baseX - 1800.0, picoLlama),
      FlSpot(baseX, totalLlama),
    ];

    return HomeDesign(
      logoAppBarPath: 'assets/logo.png',
      fluxoYolo: fluxoYolo,
      fluxoLlama: fluxoLlama,
      totalYolo: totalYolo.toInt(),
      picoYolo: picoYolo.toInt(),
      mediaYolo: mediaYolo,
      totalLlama: totalLlama.toInt(),
      picoLlama: picoLlama.toInt(),
      mediaLlama: mediaLlama,
    );
  }
}