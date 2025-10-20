import 'package:flutter/material.dart';
import '../design/login_design.dart';
import '../routes/signup_routes.dart';
import '../pages/main_page.dart';
import '../services/user_service.dart';

class LoginPage extends StatefulWidget {
  const LoginPage({super.key});

  @override
  State<LoginPage> createState() => _LoginPageState();
}

class _LoginPageState extends State<LoginPage> {
  @override
  void initState() {
    super.initState();
    _checkUser();
  }

  void _checkUser() {
    final user = UserService.getUser();
    if (user != null) {
      Navigator.pushReplacement(
        context,
        MaterialPageRoute(builder: (_) => const MainPage()),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return LoginDesign(
      onLogin: (email, password) async {
        final user = UserService.getUser();
        if (user != null && user.email == email) {
          Navigator.pushReplacement(
            context,
            MaterialPageRoute(builder: (_) => const MainPage()),
          );
        } else {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text("Usuário não encontrado")),
          );
        }
      },
      onSignUpTap: () => SignUpRoutes.goToSignUp(context),
    );
  }
}
