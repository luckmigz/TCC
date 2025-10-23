import 'package:flutter/material.dart';
import '../pages/signup_page.dart';

class SignUpRoutes {
  static void goToSignUp(BuildContext context) {
    Navigator.push(
      context,
      MaterialPageRoute(builder: (_) => const SignUpPage()),
    );
  }
}
