import 'package:flutter/material.dart';
import '../design/relatorio_design.dart';

class RelatorioPage extends StatelessWidget {
  const RelatorioPage({super.key});

  void _baixarPDF(String periodo) {
    debugPrint(" Baixando relatório de $periodo em PDF...");
  }

  void _enviarEmail(String periodo) {
    debugPrint("Enviando relatório de $periodo por e-mail...");
  }

  @override
  Widget build(BuildContext context) {
    return DefaultTabController(
      length: 3, 
      child: RelatorioDesign(
        onDownloadPDF: _baixarPDF,
        onSendEmail: _enviarEmail,
        logoAppBarPath: "logo.png",
      ),
    );
  }
}
