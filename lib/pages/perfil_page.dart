import 'package:flutter/material.dart';
import '../design/perfil_design.dart';
import '../services/user_service.dart';
import '../pages/login_page.dart';

class PerfilPage extends StatefulWidget {
  const PerfilPage({super.key});

  @override
  State<PerfilPage> createState() => _PerfilPageState();
}

class _PerfilPageState extends State<PerfilPage> {
  String userName = "Usuário";
  String userEmail = "email@email.com";

  @override
  void initState() {
    super.initState();
    _loadUser();
  }

  void _loadUser() {
    final user = UserService.getUser();
    if (user != null) {
      setState(() {
        userName = user.name;
        userEmail = user.email;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return PerfilDesign(
      userName: userName,
      userEmail: userEmail,
      onSignOut: () {
        UserService.saveUser(null); // desloga limpando o usuário
        Navigator.pushReplacement(
          context,
          MaterialPageRoute(builder: (_) => const LoginPage()),
        );
      },
      onDeleteAccount: () {
        UserService.saveUser(null); // remove usuário
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text("Conta excluída.")),
        );
        Navigator.pushReplacement(
          context,
          MaterialPageRoute(builder: (_) => const LoginPage()),
        );
      },
    );
  }
}
