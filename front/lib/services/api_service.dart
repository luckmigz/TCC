import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

// 🔧 Coloque aqui a URL base do seu backend no Heroku
const String authURL = "https://tcc-user-auth-dbaeb4cec5d9.herokuapp.com";
const String baseUrl = "https://tcc-user-db-530d29de8ef0.herokuapp.com";

class ApiService {
  // Instância para armazenamento seguro do token
  static const _storage = FlutterSecureStorage();

  // Método privado para obter o token armazenado
  static Future<String?> _getToken() async {
    return await _storage.read(key: 'auth_token');
  }

  // Método privado para gerar os cabeçalhos da requisição
  static Future<Map<String, String>> _getHeaders({bool includeAuth = false}) async {
    Map<String, String> headers = {'Content-Type': 'application/json'};
    if (includeAuth) {
      String? token = await _getToken();
      if (token != null) {
        headers['Authorization'] = 'Bearer $token'; // Adiciona o cabeçalho de autorização
      } else {
        // Opcional: Lançar exceção ou tratar caso o token não seja encontrado quando esperado
        print("Aviso: Tentando adicionar cabeçalho de autenticação sem token.");
      }
    }
    return headers;
  }

  // ===============================
  // 🔐 LOGIN E PERFIL
  // ===============================
  static Future<Map<String, dynamic>> login({
    required String email,
    required String password,
    required String loginAs,
  }) async {
    // URL corrigida para incluir o prefixo /auth
    final url = Uri.parse("$authURL/auth/login");
    final response = await http.post(
      url,
      headers: await _getHeaders(), // Usa _getHeaders sem autenticação para login
      body: jsonEncode({
        "email": email,
        "password": password,
        "login_as": loginAs, // "restaurant" ou "user"
      }),
    );

    if (response.statusCode == 200) {
      final responseBody = jsonDecode(response.body);
      // Salva o token após o login bem-sucedido
      if (responseBody.containsKey('access_token')) {
         await _storage.write(key: 'auth_token', value: responseBody['access_token']);
      }
      return responseBody;
    } else {
      // Tenta decodificar a resposta de erro para obter mais detalhes
      String errorMessage = response.body;
      try {
        final errorBody = jsonDecode(response.body);
        if (errorBody is Map && errorBody.containsKey('detail')) {
          errorMessage = errorBody['detail'];
        }
      } catch (_) {
        // Se não for JSON válido, usa o corpo da resposta como está
      }
      throw Exception("Erro ao fazer login: $errorMessage (Status: ${response.statusCode})");
    }
  }

  // Modificado para buscar o token internamente
  static Future<Map<String, dynamic>> getMe() async {
    final url = Uri.parse("$authURL/auth/me"); //
    final response = await http.get(
      url,
      // Usa _getHeaders com autenticação
      headers: await _getHeaders(includeAuth: true),
    );

    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else if (response.statusCode == 401) {
       // Possível token inválido ou expirado. Limpa o token local.
       await _storage.delete(key: 'auth_token');
       throw Exception("Token inválido ou expirado. Faça login novamente.");
    } else {
      throw Exception("Erro ao buscar dados do usuário/restaurante: ${response.body} (Status: ${response.statusCode})");
    }
  }

  // ===============================
  // 👤 USUÁRIOS
  // ===============================
  static Future<Map<String, dynamic>> createUser(Map<String, dynamic> user) async {
    final response = await http.post(
      Uri.parse("$baseUrl/user/create"), //
      headers: await _getHeaders(), // Geralmente cadastro não requer token
      body: jsonEncode(user),
    );

    if (response.statusCode == 201) {
      return jsonDecode(response.body);
    } else {
      throw Exception("Erro ao criar usuário: ${response.body} (Status: ${response.statusCode})");
    }
  }

  static Future<Map<String, dynamic>> getUserByEmail(String email) async {
    final response = await http.get(
      Uri.parse("$baseUrl/user/email/$email"), //
      // Assume-se que esta rota pode precisar de autenticação dependendo da regra de negócio
      headers: await _getHeaders(includeAuth: true),
    );
    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else if (response.statusCode == 404) {
      throw Exception("Usuário não encontrado");
    } else {
      throw Exception("Erro ao buscar usuário por email: ${response.body} (Status: ${response.statusCode})");
    }
  }

  static Future<Map<String, dynamic>> updateUser(Map<String, dynamic> user) async {
    final response = await http.put(
      Uri.parse("$baseUrl/user/update"), //
      headers: await _getHeaders(includeAuth: true), // Atualização requer autenticação
      body: jsonEncode(user),
    );

    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else {
      throw Exception("Erro ao atualizar usuário: ${response.body} (Status: ${response.statusCode})");
    }
  }

  static Future<Map<String, dynamic>> deleteUser(String email) async {
    final response = await http.delete(
      Uri.parse("$baseUrl/user/delete/$email"), //
      headers: await _getHeaders(includeAuth: true), // Deleção requer autenticação
    );
    if (response.statusCode == 200) {
       return jsonDecode(response.body);
    } else {
      throw Exception("Erro ao deletar usuário: ${response.body} (Status: ${response.statusCode})");
    }
  }

  // ===============================
  // 🍽️ RESTAURANTES
  // ===============================
  static Future<Map<String, dynamic>> createRestaurant(Map<String, dynamic> restaurant) async {
    final response = await http.post(
      Uri.parse("$baseUrl/restaurant/create"), //
      headers: await _getHeaders(), // Cadastro geralmente não requer token
      body: jsonEncode(restaurant),
    );

    if (response.statusCode == 201) {
      return jsonDecode(response.body);
    } else {
      throw Exception("Erro ao criar restaurante: ${response.body} (Status: ${response.statusCode})");
    }
  }

  static Future<Map<String, dynamic>> getRestaurantByCnpj(String cnpj) async {
    final response = await http.get(
      Uri.parse("$baseUrl/restaurant/$cnpj"), //
      // Pode ou não precisar de auth, dependendo se a info é pública
      headers: await _getHeaders(includeAuth: true), // Assume que precisa por segurança
    );
    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else if (response.statusCode == 404) {
      throw Exception("Restaurante não encontrado");
    } else {
      throw Exception("Erro ao buscar restaurante por CNPJ: ${response.body} (Status: ${response.statusCode})");
    }
  }

  static Future<Map<String, dynamic>> getRestaurantByEmail(String email) async {
    final response = await http.get(
      Uri.parse("$baseUrl/restaurant/email/$email"), //
      // Pode ou não precisar de auth
      headers: await _getHeaders(includeAuth: true), // Assume que precisa por segurança
    );
    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else if (response.statusCode == 404) {
      throw Exception("Restaurante não encontrado");
    } else {
      throw Exception("Erro ao buscar restaurante por email: ${response.body} (Status: ${response.statusCode})");
    }
  }

  static Future<Map<String, dynamic>> updateRestaurant(Map<String, dynamic> restaurant) async {
    final response = await http.put(
      Uri.parse("$baseUrl/restaurant/update"), //
      headers: await _getHeaders(includeAuth: true), // Atualização requer autenticação
      body: jsonEncode(restaurant),
    );

    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else {
      throw Exception("Erro ao atualizar restaurante: ${response.body} (Status: ${response.statusCode})");
    }
  }

  static Future<Map<String, dynamic>> deleteRestaurant(String cnpj) async {
    final response = await http.delete(
      Uri.parse("$baseUrl/restaurant/delete/$cnpj"), //
      headers: await _getHeaders(includeAuth: true), // Deleção requer autenticação
    );
    if (response.statusCode == 200) {
       return jsonDecode(response.body);
    } else {
      throw Exception("Erro ao deletar restaurante: ${response.body} (Status: ${response.statusCode})");
    }
  }

  static Future<Map<String, dynamic>> updateOccupancy(String cnpj, int newOccupancy) async {
    final response = await http.patch(
      Uri.parse("$baseUrl/restaurant/occupancy/$cnpj"), //
      headers: await _getHeaders(includeAuth: true), // Atualização de ocupação requer autenticação
      body: jsonEncode({"new_occupancy": newOccupancy}),
    );

    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else {
      throw Exception("Erro ao atualizar ocupação: ${response.body} (Status: ${response.statusCode})");
    }
  }

  // Método para logout (limpar o token)
  static Future<void> logout() async {
    await _storage.delete(key: 'auth_token');
  }
}