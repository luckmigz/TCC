import 'package:flutter/material.dart';

class HomeDesign extends StatelessWidget {
  final Color appBarColor;
  final Color iconColor;
  final String logoPath;
  final String logoAppBarPath;

  // 🔹 Variáveis dinâmicas
  final int mesasOcupadas;
  final int mesasTotais;
  final String mesaMaisRecente;
  final int tempoOcupacaoMin;

  const HomeDesign({
    super.key,
    this.appBarColor = const Color.fromRGBO(46, 133, 157, 1),
    this.iconColor = const Color.fromRGBO(225, 105, 30, 1),
    this.logoPath = "logo.png",
    this.logoAppBarPath = "logo.png",
    this.mesasOcupadas = 0,
    this.mesasTotais = 0,
    this.mesaMaisRecente = "",
    this.tempoOcupacaoMin = 0,
  });

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text(
          "Home",
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
            // Gráfico de fluxo de clientes
            Expanded(
              child: Container(
                color: Colors.grey[200],
                child: const Center(
                  child: Text("Gráfico de Fluxo de Clientes"),
                ),
              ),
            ),
            const SizedBox(height: 20),

            // Card: mesas ocupadas
            Card(
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
                        style: const TextStyle(fontSize: 20),
                      ),
                    ],
                  ),
                ),
              ),
            ),
            const SizedBox(height: 10),

            // Card: tempo de ocupação
            Card(
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
                      Text(
                        "Mesa $mesaMaisRecente está ocupada há $tempoOcupacaoMin min",
                        style: const TextStyle(fontSize: 20),
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
