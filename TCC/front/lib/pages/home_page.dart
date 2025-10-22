import 'package:flutter/material.dart';
import '../design/home_design.dart';
import '../services/user_service.dart';

class HomePage extends StatelessWidget {
  const HomePage({super.key});

  @override
  Widget build(BuildContext context) {
    // Pega os dados do UserService
    final int mesasOcupadas = UserService.mesasDisponiveis;
    final int mesasTotais = UserService.totalMesas;
    final String mesaAtual = UserService.mesaAtual;

    // Converte tempoMesa de String para int (ex: "30 min" -> 30)
    final int tempoMesa = int.tryParse(
          UserService.tempoMesa.replaceAll(RegExp(r'[^0-9]'), ''),
        ) ??
        0;

    return HomeDesign(
      mesasOcupadas: mesasOcupadas,
      mesasTotais: mesasTotais,
      mesaMaisRecente: mesaAtual,
      tempoOcupacaoMin: tempoMesa,
      logoPath: "logo.png",
      logoAppBarPath: "logo.png",
      iconColor: const Color.fromRGBO(225, 105, 30, 1),
    );
  }
}
