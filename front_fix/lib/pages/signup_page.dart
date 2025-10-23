import 'package:flutter/material.dart';
import '../design/signup_design.dart';
import '../services/user_service.dart';
import '../routes/login_routes.dart';

class SignUpPage extends StatefulWidget {
  const SignUpPage({super.key});

  @override
  State<SignUpPage> createState() => _SignUpPageState();
}

class _SignUpPageState extends State<SignUpPage> {
  final _formKey = GlobalKey<FormState>();

  final TextEditingController _nameController = TextEditingController();
  final TextEditingController _emailController = TextEditingController();
  final TextEditingController _confirmEmailController = TextEditingController();
  final TextEditingController _passwordController = TextEditingController();
  final TextEditingController _companyController = TextEditingController();
  final TextEditingController _tables2Controller = TextEditingController();
  final TextEditingController _tables4Controller = TextEditingController();
  final TextEditingController _tables8Controller = TextEditingController();

  @override
  Widget build(BuildContext context) {
    return SignUpDesign(
      formKey: _formKey,
      nameController: _nameController,
      emailController: _emailController,
      confirmEmailController: _confirmEmailController,
      passwordController: _passwordController,
      companyController: _companyController,
      tables2Controller: _tables2Controller,
      tables4Controller: _tables4Controller,
      tables8Controller: _tables8Controller,
      onSignUp: (name, email, password) async {
        // Salva o usuário em memória
        final user = User(name: name, email: email, cnpj: '');
        await UserService.saveUser(user);

        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text("Cadastro realizado!")),
        );

        // Vai para a tela de login
        LoginRoutes.replaceWithLogin(context);
      },
    );
  }
}
