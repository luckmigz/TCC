import 'package:flutter/material.dart';
import 'pages/main_page.dart';
import 'pages/login_page.dart';
import 'services/user_service.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();

  final user = UserService.getUser(); // Use Future se async
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
      home: isLoggedIn ? const MainPage() : const LoginPage(),
    );
  }
}
