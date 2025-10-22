import 'package:flutter/material.dart';
import 'pages/main_page.dart';
import 'services/user_service.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();

  // Verifica se já existe um usuário em memória
  final user = UserService.getUser();

  runApp(MyApp(isLoggedIn: user != null));
}

class MyApp extends StatelessWidget {
  final bool isLoggedIn;
  const MyApp({super.key, required this.isLoggedIn});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      title: 'Meu App',
      home: isLoggedIn ? const MainPage() : const MainPage(),
    );
  }
}
