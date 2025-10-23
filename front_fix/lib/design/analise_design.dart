import 'package:flutter/material.dart';
import '../services/api_service.dart';

class AnaliseDesign extends StatefulWidget {
  const AnaliseDesign({super.key});

  @override
  State<AnaliseDesign> createState() => _AnaliseDesignState();
}

class _AnaliseDesignState extends State<AnaliseDesign> {
  Map<String, dynamic>? _userData;
  bool _loading = true;

  @override
  void initState() {
    super.initState();
    _fetchData();
  }

  Future<void> _fetchData() async {
    try {
      final data = await ApiService.getMe(context as String);
      setState(() => _userData = data);
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Erro ao buscar dados: $e')),
      );
    } finally {
      setState(() => _loading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_loading) {
      return const Scaffold(
        body: Center(child: CircularProgressIndicator()),
      );
    }

    final nome = _userData?['name'] ?? 'Usuário';
    final clientesAtivos = _userData?['clientesAtivos'] ?? 42;
    final ocupacao = _userData?['ocupacaoMedia'] ?? 0.7;

    return Scaffold(
      appBar: AppBar(
        title: const Text('Análise'),
        backgroundColor: const Color(0xFF1565C0),
      ),
      body: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          children: [
            Image.asset('assets/logoazul2.png', height: 100),
            const SizedBox(height: 20),
            Text('Relatório de $nome',
                style:
                    const TextStyle(fontSize: 22, fontWeight: FontWeight.bold)),
            const SizedBox(height: 20),
            Text('Clientes ativos: $clientesAtivos'),
            const SizedBox(height: 20),
            Text('Ocupação média: ${(ocupacao * 100).toStringAsFixed(1)}%'),
            const SizedBox(height: 20),
            LinearProgressIndicator(
              value: ocupacao,
              backgroundColor: Colors.grey.shade300,
              color: const Color(0xFF42A5F5),
            ),
          ],
        ),
      ),
    );
  }
}
