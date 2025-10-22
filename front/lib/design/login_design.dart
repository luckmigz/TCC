import 'package:flutter/material.dart';

class LoginDesign extends StatefulWidget {
  final Future<void> Function(String email, String password) onLogin;
  final VoidCallback onSignUpTap;

  const LoginDesign({
    super.key,
    required this.onLogin,
    required this.onSignUpTap,
  });

  @override
  _LoginDesignState createState() => _LoginDesignState();
}

class _LoginDesignState extends State<LoginDesign> {
  final _formKey = GlobalKey<FormState>();
  final TextEditingController _emailController = TextEditingController();
  final TextEditingController _passwordController = TextEditingController();

  @override
  Widget build(BuildContext context) {
    final screenWidth = MediaQuery.of(context).size.width;
    final isWeb = screenWidth > 600;

    return Scaffold(
      backgroundColor: const Color.fromRGBO(46, 133, 157, 1),
      body: Center(
        child: SingleChildScrollView(
          child: Container(
            constraints: BoxConstraints(
              maxWidth: isWeb ? 500 : double.infinity,
            ),
            margin: EdgeInsets.symmetric(
              horizontal: isWeb ? 50 : 20,
              vertical: 50,
            ),
            padding: EdgeInsets.all(isWeb ? 30 : 20),
            decoration: BoxDecoration(
              color: const Color.fromRGBO(239, 251, 252, 1),
              borderRadius: BorderRadius.circular(12),
            ),
            child: Form(
              key: _formKey,
              child: Column(
                children: [
                  Image.asset(
                    "assets/logoazul1.png",
                    height: isWeb ? 150 : 120,
                    fit: BoxFit.contain,
                    errorBuilder: (context, error, stackTrace) {
                      return Icon(
                        Icons.restaurant,
                        size: isWeb ? 150 : 120,
                        color: const Color.fromRGBO(46, 133, 157, 1),
                      );
                    },
                  ),
                  const SizedBox(height: 20),
                  const Text(
                    "Sign In",
                    style: TextStyle(fontSize: 32, fontWeight: FontWeight.bold),
                  ),
                  const SizedBox(height: 30),
                  TextFormField(
                    controller: _emailController,
                    decoration: const InputDecoration(labelText: "Email"),
                    validator: (value) =>
                        (value == null || value.isEmpty) ? "Email obrigatório" : null,
                  ),
                  const SizedBox(height: 15),
                  TextFormField(
                    controller: _passwordController,
                    obscureText: true,
                    decoration: const InputDecoration(labelText: "Senha"),
                    validator: (value) =>
                        (value == null || value.isEmpty) ? "Senha obrigatória" : null,
                  ),
                  const SizedBox(height: 30),
                  SizedBox(
                    width: double.infinity,
                    child: ElevatedButton(
                      onPressed: () {
                        if (_formKey.currentState!.validate()) {
                          widget.onLogin(
                            _emailController.text,
                            _passwordController.text,
                          );
                        }
                      },
                      style: ElevatedButton.styleFrom(
                        backgroundColor: const Color.fromRGBO(29, 75, 100, 1),
                        minimumSize: const Size(double.infinity, 48),
                      ),
                      child: const Text(
                        "LOG IN",
                        style: TextStyle(color: Colors.white),
                      ),
                    ),
                  ),
                  const SizedBox(height: 15),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      const Text(
                        "Não tem uma conta?",
                        style: TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      TextButton(
                        onPressed: widget.onSignUpTap,
                        child: const Text(
                          " SIGN UP",
                          style: TextStyle(
                            color: Color.fromRGBO(225, 105, 30, 1),
                            fontSize: 15,
                            fontWeight: FontWeight.bold,
                            decoration: TextDecoration.underline,
                          ),
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}
