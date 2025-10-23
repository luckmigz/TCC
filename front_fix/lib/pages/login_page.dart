import 'package:flutter/material.dart';
import '../design/login_design.dart';
import '../services/api_service.dart';
import 'main_page.dart';

class LoginPage extends StatefulWidget {
  const LoginPage({super.key});

  @override
  State<LoginPage> createState() => _LoginPageState();
}

class _LoginPageState extends State<LoginPage> {
  bool _checking = true;

  @override
  void initState() {
    super.initState();
    _autoLogin();
  }

  /// Verifica se há token salvo e se é válido.
  Future<void> _autoLogin() async {
    try {
      final userData = await ApiService.getMe(); // sem "context as String"
      if (userData != null && mounted) {
        // Se o token for válido e a API responder com sucesso, navega pra MainPage
        Navigator.of(context).pushReplacement(
          MaterialPageRoute(builder: (_) => const MainPage()),
        );
      }
    } catch (e) {
      debugPrint("Erro ao verificar login automático: $e");
      // Se não houver token ou ele for inválido, continua na tela de login
    } finally {
      if (mounted) setState(() => _checking = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_checking) {
      return const Scaffold(
        body: Center(child: CircularProgressIndicator()),
      );
    }
    return const LoginDesign();
  }
}
