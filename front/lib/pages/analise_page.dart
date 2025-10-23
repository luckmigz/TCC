import 'package:flutter/material.dart';
import '../design/analise_design.dart';
import '../services/user_service.dart';

class AnalisePage extends StatelessWidget {
  const AnalisePage({super.key});

  @override
  Widget build(BuildContext context) {
    return DefaultTabController(
      length: 3,
      child: Scaffold(
        appBar: AppBar(
          backgroundColor: const Color.fromRGBO(46, 133, 157, 1),
          elevation: 5,
          shape: const RoundedRectangleBorder(
            borderRadius: BorderRadius.vertical(bottom: Radius.circular(20)),
          ),
          title: const Text(
            "Análise",
            style: TextStyle(
              fontWeight: FontWeight.bold,
              fontSize: 22,
              color: Colors.white,
            ),
          ),
          actions: [
            Padding(
              padding: const EdgeInsets.only(right: 16.0),
              child: Image.asset(
                'logo.png',
                height: 40,
              ),
            ),
          ],
          bottom: const TabBar(
            indicatorColor: Colors.white,
            labelColor: Colors.white,
            unselectedLabelColor: Colors.white70,
            tabs: [
              Tab(text: "Dia"),
              Tab(text: "Semana"),
              Tab(text: "Mês"),
            ],
          ),
        ),
        body: TabBarView(
          children: [
            _buildAnalise("Dia"),
            _buildAnalise("Semana"),
            _buildAnalise("Mês"),
          ],
        ),
      ),
    );
  }

  AnaliseDesign _buildAnalise(String label) {
    // Aqui podemos pegar dados diferentes dependendo do label, se quiser
    int clientes;
    int mesa;
    List<String> testes = ["Manhã", "Tarde", "Noite"];

    switch (label) {
      case "Dia":
        clientes = UserService.numeroClientes;
        mesa = UserService.mesasDisponiveis; // exemplo
        break;
      case "Semana":
        clientes = UserService.numeroClientes * 3; // exemplo
        mesa = UserService.totalMesas; // exemplo
        break;
      case "Mês":
        clientes = UserService.numeroClientes * 15; // exemplo
        mesa = UserService.valorMesaMaisUsada.toInt(); // exemplo
        break;
      default:
        clientes = 0;
        mesa = 0;
    }

    return AnaliseDesign(
      label: label,
      numberOfClients: clientes,
      mostUsedTable: mesa,
      testsList: testes,
      logoPath: "logoazul1.png",
      logoAppBarPath: "logoazul1.png",
    );
  }
}
