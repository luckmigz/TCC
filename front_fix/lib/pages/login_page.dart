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
    }
  }
