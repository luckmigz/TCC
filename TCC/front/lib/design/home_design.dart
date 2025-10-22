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
    final screenWidth = MediaQuery.of(context).size.width;
    final isWeb = screenWidth > 600;

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
              "assets/$logoAppBarPath",
              height: 50,
              fit: BoxFit.contain,
              errorBuilder: (context, error, stackTrace) {
                return const Icon(Icons.restaurant, color: Colors.white);
              },
            ),
          ),
        ],
      ),
      body: Center(
        child: Container(
          constraints: BoxConstraints(
            maxWidth: isWeb ? 800 : double.infinity,
          ),
          child: Padding(
            padding: EdgeInsets.all(isWeb ? 32.0 : 16.0),
            child: Column(
              children: [
                Expanded(
                  child: Container(
                    color: Colors.grey[200],
                    child: const Center(
                      child: Text("Gráfico de Fluxo de Clientes"),
                    ),
                  ),
                ),
                const SizedBox(height: 20),

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
                          Expanded(
                            child: Text(
                              "$mesasOcupadas/$mesasTotais Mesas Ocupadas",
                              style: TextStyle(fontSize: isWeb ? 20 : 18),
                              overflow: TextOverflow.ellipsis,
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),
                ),
                const SizedBox(height: 10),

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
                          Expanded(
                            child: Text(
                              "Mesa $mesaMaisRecente está ocupada há $tempoOcupacaoMin min",
                              style: TextStyle(fontSize: isWeb ? 20 : 16),
                              overflow: TextOverflow.ellipsis,
                              maxLines: 2,
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
        ),
      ),
    );
  }
}
