import 'package:flutter/material.dart';
import '../services/api_service.dart';

class HomeDesign extends StatefulWidget {
  const HomeDesign({super.key});

  @override
  State<HomeDesign> createState() => _HomeDesignState();
}

class _HomeDesignState extends State<HomeDesign> {
  Map<String, dynamic>? _data;
  bool _loading = true;

  // 🔹 Cores padrão (podem ser alteradas)
  final Color appBarColor = const Color.fromRGBO(46, 133, 157, 1);
  final Color iconColor = const Color.fromRGBO(225, 105, 30, 1);

  @override
  void initState() {
    super.initState();
    _fetchData();
  }

  Future<void> _fetchData() async {
    try {
      final data = await ApiService.getMe();
      setState(() => _data = data);
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Erro ao buscar dados da API: $e')),
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

    // 🔹 Dados recebidos da API (com fallback)
    final int mesasOcupadas = _data?['mesas_ocupadas'] ?? 6;
    final int mesasTotais = _data?['total_mesas'] ?? 10;
    final String mesaMaisRecente = _data?['mesa_atual']?.toString() ?? "4";
    final int tempoOcupacaoMin = _data?['tempo_mesa_min'] ?? 30;

    return Scaffold(
      appBar: AppBar(
        title: const Text(
          "Home",
          style: TextStyle(fontWeight: FontWeight.bold, color: Colors.white),
        ),
        backgroundColor: appBarColor,
        elevation: 4,
        actions: [
          Padding(
            padding: const EdgeInsets.only(right: 16.0),
            child: Image.asset(
              "assets/logoazul1.png",
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
            // Gráfico (placeholder)
            Expanded(
              child: Container(
                width: double.infinity,
                decoration: BoxDecoration(
                  color: Colors.grey[200],
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(color: Colors.grey.shade300),
                ),
                child: const Center(
                  child: Text(
                    "Gráfico de Fluxo de Clientes",
                    style: TextStyle(
                      fontSize: 16,
                      color: Colors.black54,
                      fontWeight: FontWeight.w500,
                    ),
                  ),
                ),
              ),
            ),

            const SizedBox(height: 20),

            // Card: Mesas ocupadas
            Card(
              elevation: 2,
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(12),
              ),
              child: SizedBox(
                width: double.infinity,
                height: 80,
                child: Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 16.0),
                  child: Row(
                    crossAxisAlignment: CrossAxisAlignment.center,
                    children: [
                      Icon(Icons.event_seat, size: 40, color: iconColor),
                      const SizedBox(width: 12),
                      Text(
                        "$mesasOcupadas/$mesasTotais Mesas Ocupadas",
                        style: const TextStyle(
                          fontSize: 20,
                          fontWeight: FontWeight.w500,
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ),

            const SizedBox(height: 10),

            // Card: Tempo de ocupação
            Card(
              elevation: 2,
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(12),
              ),
              child: SizedBox(
                width: double.infinity,
                height: 80,
                child: Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 16.0),
                  child: Row(
                    crossAxisAlignment: CrossAxisAlignment.center,
                    children: [
                      Icon(Icons.timer, size: 40, color: iconColor),
                      const SizedBox(width: 12),
                      Expanded(
                        child: Text(
                          "Mesa $mesaMaisRecente está ocupada há $tempoOcupacaoMin min",
                          style: const TextStyle(
                            fontSize: 18,
                            fontWeight: FontWeight.w500,
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ),
          ],
        ),
      ),

    );
  }
}
