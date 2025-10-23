import 'package:flutter/material.dart';
import '../pages/login_page.dart';
import '../pages/main_page.dart';

class LoginRoutes {
  static const loginPage = LoginPage();

  static void goToMain(BuildContext context) {
    Navigator.pushReplacement(
      context,
      MaterialPageRoute(builder: (_) => const MainPage()),
    );
  }

  static void replaceWithLogin(BuildContext context) {
    Navigator.pushReplacement(
      context,
      MaterialPageRoute(builder: (_) => const LoginPage()),
    );
  }
}
