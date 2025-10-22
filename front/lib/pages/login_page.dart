import 'package:flutter/material.dart';
// Importar storage seguro

import '../design/login_design.dart';
import '../routes/signup_routes.dart';
import 'main_page.dart';
// Removido: import '../services/user_service.dart'; // Não vamos mais usar o user local para checar login
import '../services/api_service.dart'; // Importar ApiService

class LoginPage extends StatefulWidget {
  const LoginPage({super.key});

  @override
  State<LoginPage> createState() => _LoginPageState();
}

class _LoginPageState extends State<LoginPage> {
  bool _isLoading = false; // Estado para controlar o loading
  String _loginAs = 'user'; // Estado para controlar user/restaurant, default 'user'
  

  @override
  void initState() {
    super.initState();
    _checkTokenAndLogin(); // Verifica se já existe um token válido ao iniciar
  }

  // Verifica se existe um token e tenta buscar os dados do usuário/restaurante
  void _checkTokenAndLogin() async {
    setState(() {
      _isLoading = true; // Inicia loading para verificação do token
    });
    try {
      // Tenta pegar o token do storage (agora gerenciado internamente pelo ApiService)
      // e validar chamando getMe()
      final userData = await ApiService.getMe(); // getMe busca o token internamente

      // Se getMe funcionou, temos um token válido e dados do usuário/restaurante
      print("Token válido encontrado. Dados: $userData");

      // Opcional: Salvar dados do usuário localmente se necessário
      // Ex: final user = User.fromJson(userData); await UserService.saveUser(user);

      // Navega para a página principal
      if (mounted) { // Verifica se o widget ainda está na árvore
          Navigator.pushReplacement(
            context,
            MaterialPageRoute(builder: (_) => const MainPage()),
          );
      }
    } catch (e) {
      // Se getMe falhou (token inválido, expirado ou não existe), permanece na LoginPage
      print("Nenhum token válido encontrado ou erro ao buscar dados: $e");
      // O token inválido já foi limpo pelo ApiService.getMe em caso de 401
    } finally {
       if (mounted) {
           setState(() {
              _isLoading = false; // Termina o loading da verificação inicial
           });
       }
    }
  }

  // Função chamada ao pressionar o botão de login
  Future<void> _handleLogin(String email, String password) async {
    setState(() {
      _isLoading = true; // Inicia o loading
    });

    try {
      // Chama a API de login
      final response = await ApiService.login(
        email: email,
        password: password,
        loginAs: _loginAs, // Usa o valor selecionado
      );

      print("Login bem-sucedido: $response");
      // Token já foi salvo pelo ApiService.login

      // Opcional: Chamar getMe aqui se quiser os dados imediatamente após login
      // final userData = await ApiService.getMe();
      // Salvar dados localmente...

      // Navega para a página principal
      if (mounted) {
        Navigator.pushReplacement(
          context,
          MaterialPageRoute(builder: (_) => const MainPage()),
        );
      }
    } catch (e) {
      // Mostra erro em caso de falha no login
      print("Erro no login: $e");
       if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(content: Text("Falha no login: ${e.toString()}")),
          );
       }
    } finally {
       if (mounted) {
         setState(() {
           _isLoading = false; // Termina o loading
         });
       }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      // Stack para mostrar o loading sobre a tela
      body: Stack(
        children: [
          // Conteúdo principal da tela de login
          Padding(
            padding: const EdgeInsets.all(16.0), // Adiciona padding geral
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center, // Centraliza verticalmente
              children: [
                // === Exemplo de Seleção User/Restaurant ===
                // Você PRECISA integrar isso melhor ao seu LoginDesign
                const Text("Logar como:"),
                Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: <Widget>[
                    Expanded( // Para que ocupem espaço disponível
                      child: RadioListTile<String>(
                        title: const Text('Usuário'),
                        value: 'user',
                        groupValue: _loginAs,
                        onChanged: (value) {
                          setState(() {
                            _loginAs = value!;
                          });
                        },
                      ),
                    ),
                    Expanded( // Para que ocupem espaço disponível
                      child: RadioListTile<String>(
                        title: const Text('Restaurante'),
                        value: 'restaurant',
                        groupValue: _loginAs,
                        onChanged: (value) {
                          setState(() {
                            _loginAs = value!;
                          });
                        },
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 20), // Espaçamento
                // === Fim Exemplo Seleção ===

                // Seu design de login
                LoginDesign(
                  // Passa a função _handleLogin para ser chamada pelo LoginDesign
                  onLogin: _handleLogin,
                  // Mantém a navegação para signup
                  onSignUpTap: () => SignUpRoutes.goToSignUp(context),
                ),
              ],
            ),
          ),

          // Indicador de carregamento (mostrado se _isLoading for true)
          if (_isLoading)
            const Center(
              child: CircularProgressIndicator(),
            ),
        ],
      ),
    );
  }
}