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

  // 🔹 Histórico de pontos para o gráfico (x = horário local em segundos, y = pessoas)
  final List<FlSpot> _fluxoYolo = [];
  final List<FlSpot> _fluxoLlama = [];

  @override
  void initState() {
    super.initState();
    _carregarDados(); // 🔹 Chamada imediata
    _iniciarAtualizacaoPeriodica(); // 🔹 Atualização automática
  }

  void _iniciarAtualizacaoPeriodica() {
    _timer?.cancel();
    // Atualiza a cada 2 minutos
    _timer = Timer.periodic(const Duration(minutes: 2), (_) {
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

      // ====== PEGA YOLO / LLaMA E O HORÁRIO CORRETO ======
      final yolo = data['yolo_analysis'] ?? {};
      final llama = data['llama_analysis'] ?? {};

      final ultimaStrYolo = yolo['ultima_atualizacao']?.toString();
      final ultimaStrLlama = llama['ultima_atualizacao']?.toString();

      // Preferimos o horário do YOLO; se não tiver, usamos o do LLaMA; se não, agora.
      String? ultimaStr;
      if (ultimaStrYolo != null && ultimaStrYolo.isNotEmpty) {
        ultimaStr = ultimaStrYolo;
      } else if (ultimaStrLlama != null && ultimaStrLlama.isNotEmpty) {
        ultimaStr = ultimaStrLlama;
      } else {
        ultimaStr = null;
      }

      // ====== CONVERSÃO PARA HORÁRIO LOCAL ======
      DateTime timestamp;
      if (ultimaStr != null && ultimaStr.trim().isNotEmpty) {
        // Ex.: "2025-12-02 20:07:22" → "2025-12-02T20:07:22Z" (força UTC) → toLocal()
        final isoUtc = ultimaStr.replaceFirst(' ', 'T') + 'Z';
        final utc = DateTime.tryParse(isoUtc);
        timestamp = (utc ?? DateTime.now()).toLocal();
      } else {
        timestamp = DateTime.now();
      }

      // Eixo X = segundos desde epoch, já em horário local
      final double x = timestamp.millisecondsSinceEpoch / 1000.0;

      // Ocupação atual (pessoas) de cada modelo (Y do gráfico)
      final totalYolo =
          (yolo['quantidade_atual']?['person'] ?? 0).toDouble();
      final totalLlama =
          (llama['quantidade_atual']?['person'] ?? 0).toDouble();

      // Debug opcional
      // ignore: avoid_print
      print('Novo ponto YOLO (LOCAL): x=$x, y=$totalYolo, ts=$timestamp');
      // ignore: avoid_print
      print('Novo ponto LLaMA (LOCAL): x=$x, y=$totalLlama, ts=$timestamp');

      if (!mounted) return;

      setState(() {
        analyticsData = data;

        // ====== ATUALIZA HISTÓRICO DO GRÁFICO ======
        _fluxoYolo.add(FlSpot(x, totalYolo));
        _fluxoLlama.add(FlSpot(x, totalLlama));

        // opcional: limita o histórico aos últimos N pontos
        const maxPontos = 50;
        if (_fluxoYolo.length > maxPontos) {
          _fluxoYolo.removeAt(0);
        }
        if (_fluxoLlama.length > maxPontos) {
          _fluxoLlama.removeAt(0);
        }
      });
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

    // Se não há dados de fluxo ainda, mostra mensagem amigável
    if (_fluxoYolo.isEmpty && _fluxoLlama.isEmpty) {
      return Scaffold(
        appBar: AppBar(
          title: const Text('Análises de Fluxo'),
          backgroundColor: const Color.fromRGBO(46, 133, 157, 1),
        ),
        body: const Center(
          child: Text(
            'Sem dados de fluxo no momento.\nAguarde a próxima análise.',
            textAlign: TextAlign.center,
            style: TextStyle(fontSize: 16, color: Colors.black54),
          ),
        ),
      );
    }

    final yolo = analyticsData?['yolo_analysis'] ?? {};
    final llama = analyticsData?['llama_analysis'] ?? {};

    // === YOLO ===
    final totalYolo =
        (yolo['quantidade_atual']?['person'] ?? 0).toDouble();
    final mediaYolo = (yolo['media_total'] ?? 0).toDouble();
    final picoYolo = (yolo['pico_total'] ?? 0).toDouble();

    // === LLaMA === (media_total e pico_total podem ser DOUBLE ou MAP)
    final totalLlama =
        (llama['quantidade_atual']?['person'] ?? 0).toDouble();

    final mediaLlamaRaw = llama['media_total'];
    double mediaLlama;
    if (mediaLlamaRaw is Map) {
      mediaLlama = (mediaLlamaRaw['person'] ?? 0).toDouble();
    } else {
      mediaLlama = (mediaLlamaRaw ?? 0).toDouble();
    }

    final picoLlamaRaw = llama['pico_total'];
    double picoLlama;
    if (picoLlamaRaw is Map) {
      picoLlama = (picoLlamaRaw['person'] ?? 0).toDouble();
    } else {
      picoLlama = (picoLlamaRaw ?? 0).toDouble();
    }

    return HomeDesign(
      logoAppBarPath: 'assets/logo.png',
      fluxoYolo: _fluxoYolo,
      fluxoLlama: _fluxoLlama,
      totalYolo: totalYolo.toInt(),
      picoYolo: picoYolo.toInt(),
      mediaYolo: mediaYolo,
      totalLlama: totalLlama.toInt(),
      picoLlama: picoLlama.toInt(),
      mediaLlama: mediaLlama,
    );
  }
}
