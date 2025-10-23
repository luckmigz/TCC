  import 'package:flutter/material.dart';
  import '../design/login_design.dart';
  import '../services/api_service.dart';
  import 'main_page.dart';

<<<<<<< HEAD
  /// Tela wrapper para o Login:
  /// - Verifica se já existe token válido e tenta obter /auth/me
  /// - Se ok, navega direto para a MainPage
  class LoginPage extends StatefulWidget {
    const LoginPage({super.key});
=======
class LoginPage extends StatefulWidget {
  const LoginPage({super.key});
>>>>>>> 0f88897e67f2b47a54c71b5203415b1eced064f7

    @override
    State<LoginPage> createState() => _LoginPageState();
  }

<<<<<<< HEAD
  class _LoginPageState extends State<LoginPage> {
    bool _checking = true;

    @override
    void initState() {
      super.initState();
      _autoLogin();
    }

    Future<void> _autoLogin() async {
      try {
        await ApiService.getMe(); // se token for inválido, lançará erro
        if (!mounted) return;
        Navigator.of(context).pushReplacement(MaterialPageRoute(builder: (_) => const MainPage()));
      } catch (_) {
        // sem token / inválido → segue para tela de login
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
=======
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
>>>>>>> 0f88897e67f2b47a54c71b5203415b1eced064f7
    }
  }
