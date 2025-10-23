import 'package:flutter/material.dart';
import '../services/api_service.dart';

class PerfilDesign extends StatefulWidget {
  const PerfilDesign({super.key});

  @override
  State<PerfilDesign> createState() => _PerfilDesignState();
}

class _PerfilDesignState extends State<PerfilDesign> {
  Map<String, dynamic>? _userData;
  bool _loading = true;

  @override
  void initState() {
    super.initState();
    _loadPerfil();
  }

  Future<void> _loadPerfil() async {
    try {
      final data = await ApiService.getMe(context as String);
      setState(() => _userData = data);
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Erro ao carregar perfil: $e')),
      );
    } finally {
      setState(() => _loading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_loading) {
      return const Scaffold(body: Center(child: CircularProgressIndicator()));
    }

    final nome = _userData?['name'] ?? 'Usuário';
    final email = _userData?['email'] ?? '---';
    final telefone = _userData?['telefone'] ?? '---';

    return Scaffold(
      appBar: AppBar(
        title: const Text('Perfil'),
        backgroundColor: const Color(0xFF1565C0),
      ),
      body: Padding(
        padding: const EdgeInsets.all(24.0),
        child: Column(
          children: [
            Image.asset('assets/logo.png', height: 120),
            const SizedBox(height: 30),
            Text('Nome: $nome', style: const TextStyle(fontSize: 20)),
            const SizedBox(height: 8),
            Text('E-mail: $email', style: const TextStyle(fontSize: 18)),
            const SizedBox(height: 8),
            Text('Telefone: $telefone', style: const TextStyle(fontSize: 18)),
            const SizedBox(height: 24),
            ElevatedButton.icon(
              onPressed: _loadPerfil,
              icon: const Icon(Icons.refresh),
              label: const Text('Atualizar'),
            ),
          ],
        ),
      ),
    );
  }
}
