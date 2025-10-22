import 'package:flutter/material.dart';

class AnaliseDesign extends StatelessWidget {
  final String label;
  final int numberOfClients;
  final int mostUsedTable;
  final List<String> testsList;
  final Color appBarColor;
  final String logoPath;
  final String logoAppBarPath;
  // 🔹 novos parâmetros de estilo
  final double cardHeight;
  final double cardWidthClientes;
  final double cardWidthMesa;
  final double titleFontSize;
  final double valueFontSize;

  

  const AnaliseDesign({
    super.key,
    required this.label,
    required this.numberOfClients,
    required this.mostUsedTable,
    required this.testsList,
    this.appBarColor =  const Color.fromRGBO(29, 75, 100, 1),
    this.cardHeight = 100, // altura padrão
    this.cardWidthClientes = 250, // largura padrão do card clientes
    this.cardWidthMesa = 250,     // largura padrão do card mesa
    this.titleFontSize = 16,      // fonte padrão título
    this.valueFontSize = 20,  
    this.logoPath = "logo.png",
    this.logoAppBarPath = "logo.png",    // fonte padrão valor
  });

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.all(16.0),
      child: Column(
        children: [
          // Retângulo do gráfico
          SizedBox(
            height: 300,
            child: Container(
              color: Colors.grey[200],
              child: const Center(
                child: Text("Gráfico de Fluxo de Clientes"),
              ),
            ),
          ),

          const SizedBox(height: 10),

          // 🔹 Cards resumo
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceEvenly,
            children: [
              // Card de clientes
              SizedBox(
                width: cardWidthClientes,
                height: cardHeight,
                child: Card(
                  child: Padding(
                    padding: const EdgeInsets.all(12),
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Text(
                          "Nº de Clientes",
                          style: TextStyle(
                            fontSize: 20,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                        Text(
                          numberOfClients.toString(),
                          style: TextStyle(
                            fontSize: valueFontSize,
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
              ),

              // Card de mesa
              SizedBox(
                width: cardWidthMesa,
                height: cardHeight,
                child: Card(
                  child: Padding(
                    padding: const EdgeInsets.all(12),
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Text(
                          "Mesa Mais Usada",
                          style: TextStyle(
                            fontSize: titleFontSize,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                        Text(
                          mostUsedTable.toString(),
                          style: TextStyle(
                            fontSize: valueFontSize,
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
              ),
            ],
          ),

          const SizedBox(height: 20),

          // Lista expandível de testes
          Expanded(
            child: ListView.builder(
              itemCount: testsList.length,
              itemBuilder: (context, index) {
                return ExpansionTile(
                  title: Text(testsList[index]),
                  trailing: const Icon(Icons.chevron_right),
                  children: [
                    Padding(
                      padding: const EdgeInsets.all(12.0),
                      child: Text(
                        "Aqui você pode colocar informações detalhadas sobre ${testsList[index]}",
                        style: const TextStyle(fontSize: 14, color: Colors.black54),
                      ),
                    ),
                  ],
                );
              },
            ),
          ),
        ],
      ),
    );
  }
}
