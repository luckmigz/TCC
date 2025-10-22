import 'package:flutter/material.dart';

class RelatorioDesign extends StatelessWidget {
  final void Function(String periodo) onDownloadPDF;
  final void Function(String periodo) onSendEmail;
  final Color appBarColor;
  final Color iconColor;
  final String logoAppBarPath;

  const RelatorioDesign({
    super.key,
    required this.onDownloadPDF,
    required this.onSendEmail,
    this.appBarColor = const Color.fromRGBO(46, 133, 157, 1),
    this.iconColor = Colors.blueGrey,
    this.logoAppBarPath = "assets/logo.png",
  });

  @override
  Widget build(BuildContext context) {
    final tabs = ["Dia", "Semana", "Mês"];

    return Scaffold(
      appBar: AppBar(
        title: const Text(
          "Relatório ",
          style: TextStyle(fontWeight: FontWeight.bold),
        ),
        backgroundColor: appBarColor,
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
        actions: [
          Padding(
            padding: const EdgeInsets.only(right: 16.0),
            child: Image.asset(
              "assets/logo.png",
              height: 45,
              fit: BoxFit.contain,
              errorBuilder: (context, error, stackTrace) {
                return const Icon(Icons.restaurant, color: Colors.white);
              },
            ),
          ),
        ],
      ),
      body: TabBarView(
        children: tabs
            .map(
              (periodo) => _relatorioContent(context, periodo),
            )
            .toList(),
      ),
    );
  }

  Widget _relatorioContent(BuildContext context, String periodo) {
    final screenWidth = MediaQuery.of(context).size.width;
    final isWeb = screenWidth > 600;

    return Center(
      child: Container(
        constraints: BoxConstraints(
          maxWidth: isWeb ? 600 : double.infinity,
        ),
        child: Padding(
          padding: EdgeInsets.all(isWeb ? 32.0 : 20.0),
          child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              Icons.description_outlined,
              size: 90,
              color: iconColor,
            ),
            const SizedBox(height: 25),
            Text(
              "Relatório $periodo\n\nVocê pode visualizar, baixar o PDF\nou enviar por e-mail.",
              textAlign: TextAlign.center,
              style: const TextStyle(fontSize: 16, color: Colors.black87),
            ),
            const SizedBox(height: 40),
            ElevatedButton.icon(
              onPressed: () => onDownloadPDF(periodo),
              icon: const Icon(Icons.download),
              label: const Text("Baixar PDF"),
              style: ElevatedButton.styleFrom(
                backgroundColor: const Color.fromRGBO(29, 75, 100, 1),
                foregroundColor: Colors.white,
                padding:
                    const EdgeInsets.symmetric(horizontal: 20, vertical: 12),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(12),
                ),
              ),
            ),
            const SizedBox(height: 15),
            ElevatedButton.icon(
              onPressed: () => onSendEmail(periodo),
              icon: const Icon(Icons.email_outlined),
              label: const Text("Mandar por Email"),
              style: ElevatedButton.styleFrom(
                backgroundColor: Color.fromRGBO(225, 105, 30, 1),
                foregroundColor: Colors.white,
                padding:
                    const EdgeInsets.symmetric(horizontal: 20, vertical: 12),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(12),
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
