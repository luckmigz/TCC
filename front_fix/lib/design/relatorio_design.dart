import 'dart:async';
import 'package:flutter/material.dart';
import 'package:fl_chart/fl_chart.dart';

import '../services/api_service.dart';
import '../pages/login_page.dart';

class RelatorioDesign extends StatefulWidget {
  const RelatorioDesign({super.key});

  @override
  State<RelatorioDesign> createState() => _RelatorioDesignState();
}

class _RelatorioDesignState extends State<RelatorioDesign> {
  bool carregando = true;
  String erro = '';
  Map<String, dynamic>? reportData;

  @override
  void initState() {
    super.initState();
    _carregarDados();
  }

  Future<void> _carregarDados() async {
    setState(() {
      carregando = true;
      erro = '';
    });

    try {
      // pega usuário logado e CNPJ igual na HomePage
      final user = await ApiService.getMe();
      final cnpj = user['cnpj'] ?? '';

      if (cnpj.isEmpty) {
        throw Exception("CNPJ não encontrado no perfil do restaurante");
      }

      final data = await ApiService.getReportsData(cnpj);

      if (!mounted) return;
      setState(() => reportData = data);
    } catch (e) {
      if (!mounted) return;

      if (e is AuthExpiredException) {
        Navigator.of(context, rootNavigator: true).pushAndRemoveUntil(
          MaterialPageRoute(builder: (_) => const LoginPage()),
          (route) => false,
        );
        return;
      }

      setState(() {
        erro = 'Erro ao carregar relatório: $e';
      });
    } finally {
      if (mounted) {
        setState(() => carregando = false);
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    if (carregando && reportData == null) {
      return const Scaffold(
        body: Center(child: CircularProgressIndicator()),
      );
    }

    if (erro.isNotEmpty && reportData == null) {
      return Scaffold(
        appBar: AppBar(
          title: const Text('Relatórios'),
          backgroundColor: const Color(0xFF1565C0),
        ),
        body: Center(
          child: Text(
            erro,
            style: const TextStyle(color: Colors.red, fontSize: 16),
            textAlign: TextAlign.center,
          ),
        ),
      );
    }

    final data = reportData!;
    final message = data['message'] ?? '';
    final cnpj = data['cnpj'] ?? '';
    final mongoId = data['mongo_id'] ?? '';

    final yolo = data['yolo_report'] as Map<String, dynamic>? ?? {};
    final llama = data['llama_report'] as Map<String, dynamic>? ?? {};

    final yoloTotal = yolo['total'] as Map<String, dynamic>? ?? {};
    final llamaTotal = llama['total'] as Map<String, dynamic>? ?? {};

    final yoloDaily = (yolo['daily'] as List<dynamic>?) ?? [];
    final llamaDaily = (llama['daily'] as List<dynamic>?) ?? [];

    // ===== prepara dados de gráfico: pessoas por dia =====
    final dailyYoloPersons = <String, int>{};
    for (final item in yoloDaily) {
      final m = Map<String, dynamic>.from(item as Map);
      final date = m['date']?.toString() ?? '';
      if (date.isEmpty) continue;

      // Formato antigo: {date, label, total_dia}
      if (m.containsKey('label') && m.containsKey('total_dia')) {
        if (m['label'] == 'person') {
          dailyYoloPersons[date] =
              (m['total_dia'] as num?)?.toInt() ?? 0;
        }
      } else {
        // Formato novo: {date, chair, dining_table, person}
        dailyYoloPersons[date] =
            (m['person'] as num?)?.toInt() ?? 0;
      }
    }

    final dailyLlamaPersons = <String, int>{};
    for (final item in llamaDaily) {
      final m = Map<String, dynamic>.from(item as Map);
      final date = m['date']?.toString() ?? '';
      if (date.isEmpty) continue;

      if (m.containsKey('label') && m.containsKey('total_dia')) {
        if (m['label'] == 'person') {
          dailyLlamaPersons[date] =
              (m['total_dia'] as num?)?.toInt() ?? 0;
        }
      } else {
        dailyLlamaPersons[date] =
            (m['person'] as num?)?.toInt() ?? 0;
      }
    }

    final allDates = <String>{
      ...dailyYoloPersons.keys,
      ...dailyLlamaPersons.keys,
    }.toList()
      ..sort();

    return Scaffold(
      appBar: AppBar(
        title: const Text('Relatório de Ocupação'),
        backgroundColor: const Color(0xFF1565C0),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(24.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // Logo
            Center(
              child: Image.asset('assets/logoazul1.png', height: 80),
            ),
            const SizedBox(height: 16),

            // Cabeçalho
            Center(
              child: Text(
                'Relatório consolidado\nCNPJ: $cnpj',
                textAlign: TextAlign.center,
                style: const TextStyle(
                  fontSize: 20,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ),
            const SizedBox(height: 8),
            Center(
              child: Text(
                message,
                style: const TextStyle(
                  fontSize: 14,
                  color: Colors.black54,
                ),
              ),
            ),
            if (mongoId.toString().isNotEmpty) ...[
              const SizedBox(height: 4),
              Center(
                child: Text(
                  'ID no banco: $mongoId',
                  style: const TextStyle(fontSize: 12, color: Colors.black45),
                ),
              ),
            ],

            const SizedBox(height: 24),

            // ===== Resumo por modelo =====
            Text(
              'Resumo por modelo',
              style: Theme.of(context).textTheme.titleLarge,
            ),
            const SizedBox(height: 12),

            Row(
              children: [
                Expanded(
                  child: _buildModeloResumoCard(
                    titulo: 'YOLO',
                    fonte: yolo['fonte'] ?? 'YOLO',
                    total: yoloTotal,
                    cor: Colors.indigo,
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: _buildModeloResumoCard(
                    titulo: 'LLaMA',
                    fonte: llama['fonte'] ?? 'LLaMA',
                    total: llamaTotal,
                    cor: Colors.deepOrange,
                  ),
                ),
              ],
            ),

            const SizedBox(height: 32),

            // ===== Gráfico diário de pessoas (BARRAS) =====
            if (allDates.isNotEmpty) ...[
              Text(
                'Pessoas detectadas por dia',
                style: Theme.of(context).textTheme.titleMedium,
              ),
              const SizedBox(height: 8),
              SizedBox(
                height: 260,
                child: Card(
                  elevation: 3,
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Padding(
                    padding: const EdgeInsets.fromLTRB(16, 16, 24, 24),
                    child: BarChart(
                      _buildBarChartData(
                        yoloDailyPersons: dailyYoloPersons,
                        llamaDailyPersons: dailyLlamaPersons,
                        dates: allDates,
                      ),
                    ),
                  ),
                ),
              ),
              const SizedBox(height: 8),
              Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  _buildLegendaCor(Colors.indigo, 'YOLO'),
                  const SizedBox(width: 16),
                  _buildLegendaCor(Colors.deepOrange, 'LLaMA'),
                ],
              ),
              const SizedBox(height: 24),
            ],

            // ===== Tabelinhas diárias =====
            Text(
              'Detalhamento diário – YOLO',
              style: Theme.of(context).textTheme.titleMedium,
            ),
            const SizedBox(height: 8),
            _buildDailySection(yoloDaily, Colors.indigo),

            const SizedBox(height: 24),

            Text(
              'Detalhamento diário – LLaMA',
              style: Theme.of(context).textTheme.titleMedium,
            ),
            const SizedBox(height: 8),
            _buildDailySection(llamaDaily, Colors.deepOrange),
          ],
        ),
      ),
    );
  }

  // ========= WIDGETS AUXILIARES =========

  Widget _buildModeloResumoCard({
    required String titulo,
    required String fonte,
    required Map<String, dynamic> total,
    required Color cor,
  }) {
    final chairs = total['chair'] ?? 0;
    final tables = total['dining_table'] ?? 0;
    final persons = total['person'] ?? 0;

    return Card(
      elevation: 3,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: Padding(
        padding: const EdgeInsets.all(12.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                CircleAvatar(
                  backgroundColor: cor.withOpacity(0.12),
                  child: Icon(Icons.analytics_outlined, color: cor),
                ),
                const SizedBox(width: 8),
                Text(
                  titulo,
                  style: const TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const Spacer(),
                Container(
                  padding:
                      const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                  decoration: BoxDecoration(
                    color: cor.withOpacity(0.08),
                    borderRadius: BorderRadius.circular(16),
                  ),
                  child: Text(
                    fonte,
                    style: TextStyle(
                      fontSize: 11,
                      color: cor,
                      fontWeight: FontWeight.w500,
                    ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 8),
            const Divider(height: 1),
            const SizedBox(height: 8),
            _buildResumoLinha('Pessoas detectadas', persons.toString()),
            const SizedBox(height: 4),
            _buildResumoLinha('Cadeiras detectadas', chairs.toString()),
            const SizedBox(height: 4),
            _buildResumoLinha('Mesas detectadas', tables.toString()),
          ],
        ),
      ),
    );
  }

  Widget _buildResumoLinha(String label, String value) {
    return Row(
      children: [
        Text(
          label,
          style: const TextStyle(fontSize: 13, color: Colors.black87),
        ),
        const Spacer(),
        Text(
          value,
          style: const TextStyle(
            fontSize: 15,
            fontWeight: FontWeight.bold,
          ),
        ),
      ],
    );
  }

  /// daily vem do JSON:
  /// - Formato novo: {date, chair, dining_table, person}
  /// - Formato antigo: {date, label, total_dia}
  Widget _buildDailySection(List<dynamic> daily, Color cor) {
    if (daily.isEmpty) {
      return const Text(
        'Sem dados diários para este modelo.',
        style: TextStyle(color: Colors.black54, fontSize: 13),
      );
    }

    // agrega por data: { data: {label: total_dia, ...}, ... }
    final Map<String, Map<String, int>> agregadoPorDia = {};

    for (final item in daily) {
      final map = Map<String, dynamic>.from(item as Map);
      final date = map['date']?.toString() ?? '';
      if (date.isEmpty) continue;

      agregadoPorDia.putIfAbsent(date, () => {
            'person': 0,
            'chair': 0,
            'dining_table': 0,
          });

      // Formato antigo
      if (map.containsKey('label') && map.containsKey('total_dia')) {
        final label = map['label'] as String? ?? '';
        final totalDia = (map['total_dia'] as num?)?.toInt() ?? 0;
        agregadoPorDia[date]![label] = totalDia;
      } else {
        // Formato novo
        agregadoPorDia[date]!['person'] =
            (map['person'] as num?)?.toInt() ?? 0;
        agregadoPorDia[date]!['chair'] =
            (map['chair'] as num?)?.toInt() ?? 0;
        agregadoPorDia[date]!['dining_table'] =
            (map['dining_table'] as num?)?.toInt() ?? 0;
      }
    }

    final diasOrdenados = agregadoPorDia.keys.toList()..sort();

    return Column(
      children: diasOrdenados.map((data) {
        final info = agregadoPorDia[data]!;
        final persons = info['person'] ?? 0;
        final chairs = info['chair'] ?? 0;
        final tables = info['dining_table'] ?? 0;

        return Card(
          elevation: 2,
          margin: const EdgeInsets.only(bottom: 8),
          shape:
              RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
          child: Padding(
            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
            child: Row(
              children: [
                Container(
                  width: 4,
                  height: 48,
                  decoration: BoxDecoration(
                    color: cor,
                    borderRadius: BorderRadius.circular(4),
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        data,
                        style: const TextStyle(
                          fontSize: 14,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      const SizedBox(height: 4),
                      Row(
                        children: [
                          _buildDailyTag(
                            icon: Icons.person_outline,
                            label: 'Pessoas',
                            value: persons.toString(),
                          ),
                          const SizedBox(width: 8),
                          _buildDailyTag(
                            icon: Icons.chair_outlined,
                            label: 'Cadeiras',
                            value: chairs.toString(),
                          ),
                          const SizedBox(width: 8),
                          _buildDailyTag(
                            icon: Icons.table_bar_outlined,
                            label: 'Mesas',
                            value: tables.toString(),
                          ),
                        ],
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
        );
      }).toList(),
    );
  }

  Widget _buildDailyTag({
    required IconData icon,
    required String label,
    required String value,
  }) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      decoration: BoxDecoration(
        color: Colors.grey.shade100,
        borderRadius: BorderRadius.circular(16),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, size: 14, color: Colors.black54),
          const SizedBox(width: 4),
          Text(
            '$label: $value',
            style: const TextStyle(fontSize: 12),
          ),
        ],
      ),
    );
  }

  BarChartData _buildBarChartData({
    required Map<String, int> yoloDailyPersons,
    required Map<String, int> llamaDailyPersons,
    required List<String> dates,
  }) {
    final allValues = [
      ...yoloDailyPersons.values,
      ...llamaDailyPersons.values,
    ];

    final maxY = allValues.isEmpty
        ? 1.0
        : allValues.reduce((a, b) => a > b ? a : b).toDouble();

    return BarChartData(
      alignment: BarChartAlignment.spaceAround,
      maxY: maxY * 1.2,
      minY: 0,
      groupsSpace: 24,
      barGroups: List.generate(dates.length, (i) {
        final date = dates[i];
        final yolo = (yoloDailyPersons[date] ?? 0).toDouble();
        final llama = (llamaDailyPersons[date] ?? 0).toDouble();

        return BarChartGroupData(
          x: i,
          barsSpace: 12,
          barRods: [
            BarChartRodData(
              toY: yolo,
              width: 12,
              borderRadius: BorderRadius.circular(4),
              color: Colors.indigo,
            ),
            BarChartRodData(
              toY: llama,
              width: 12,
              borderRadius: BorderRadius.circular(4),
              color: Colors.deepOrange,
            ),
          ],
        );
      }),
      titlesData: FlTitlesData(
        leftTitles: AxisTitles(
          sideTitles: SideTitles(showTitles: true, reservedSize: 36),
        ),
        bottomTitles: AxisTitles(
          sideTitles: SideTitles(
            showTitles: true,
            getTitlesWidget: (value, meta) {
              final index = value.toInt();
              if (index < 0 || index >= dates.length) {
                return const SizedBox.shrink();
              }

              final raw = dates[index];
              final pretty = raw.length >= 10 ? raw.substring(5) : raw;

              return Padding(
                padding: const EdgeInsets.only(top: 6),
                child: Text(
                  pretty,
                  style: const TextStyle(fontSize: 11),
                ),
              );
            },
          ),
        ),
        rightTitles: const AxisTitles(
          sideTitles: SideTitles(showTitles: false),
        ),
        topTitles: const AxisTitles(
          sideTitles: SideTitles(showTitles: false),
        ),
      ),
      gridData: FlGridData(show: true),
      borderData: FlBorderData(show: false),
    );
  }

  Widget _buildLegendaCor(Color cor, String label) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        Container(
          width: 12,
          height: 12,
          decoration: BoxDecoration(
            color: cor,
            borderRadius: BorderRadius.circular(4),
          ),
        ),
        const SizedBox(width: 4),
        Text(
          label,
          style: const TextStyle(fontSize: 12),
        ),
      ],
    );
  }
}
