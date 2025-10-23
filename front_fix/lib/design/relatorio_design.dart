import 'package:flutter/material.dart';
import '../services/api_service.dart';

class RelatorioDesign extends StatefulWidget {
  const RelatorioDesign({super.key});

  @override
  State<RelatorioDesign> createState() => _RelatorioDesignState();
}

class _RelatorioDesignState extends State<RelatorioDesign> {
  Map<String, dynamic>? _relatorio;
  bool _loading = true;

  @override
  void initState() {
    super.initState();
    _fetchRelatorio();
  }

  Future<void> _fetchRelatorio() async {
    try {
      final data = await ApiService.getMe(context as String);
      setState(() => _relatorio = data);
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Erro ao buscar relatório: $e')),
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

    final nome = _relatorio?['name'] ?? 'Usuário';
    final vendas = _relatorio?['vendas'] ?? 150;
    final receita = _relatorio?['receita'] ?? 12500.50;
    final clientes = _relatorio?['clientes'] ?? 32;

    return Scaffold(
      appBar: AppBar(
        title: const Text('Relatórios'),
        backgroundColor: const Color(0xFF1565C0),
      ),
      body: Padding(
        padding: const EdgeInsets.all(24.0),
        child: Column(
          children: [
            Image.asset('assets/logoazul1.png', height: 100),
            const SizedBox(height: 20),
            Text('Relatório de $nome',
                style:
                    const TextStyle(fontSize: 22, fontWeight: FontWeight.bold)),
            const SizedBox(height: 20),
            Text('Vendas realizadas: $vendas'),
            Text('Clientes atendidos: $clientes'),
            Text('Receita total: R\$ ${receita.toStringAsFixed(2)}'),
          ],
        ),
      ),
    );
  }
}
