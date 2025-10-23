import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

// 🔧 Coloque aqui a URL base do seu backend no Heroku
const String authURL = "https://tcc-user-auth-dbaeb4cec5d9.herokuapp.com";
const String baseUrl = "https://tcc-user-db-530d29de8ef0.herokuapp.com";

class ApiService {
  // Instância para armazenamento seguro do token
  static const _storage = FlutterSecureStorage();
  
  // =========================
  // Utilidades de Auth/Headers
  // =========================

  // Método privado para obter o token armazenado
 static Future<String?> _getToken() async => await _storage.read(key: 'auth_token');
 static Future<void> _setToken(String token) async {
    await _storage.write(key: 'auth_token', value: token);
  }

 static Future<Map<String, String>> _getHeaders({bool includeAuth = false}) async {
    final headers = {'Content-Type': 'application/json'};
    if (includeAuth) {
      final token = await _getToken();
      if (token != null && token.isNotEmpty) {
        headers['Authorization'] = 'Bearer $token';
      }
    }
    return headers;
  }
  static Future<http.Response> _safeRequest(Future<http.Response> Function() request) async {
    try {
      final response = await request();

      if (response.statusCode == 401) {
        await logout();
        throw Exception("Sessão expirada. Faça login novamente.");
      }

      return response;
    } catch (e) {
      throw Exception("Erro de conexão com o servidor: $e");
    }
  }

  // =====================================================
  // 🔑 AUTENTICAÇÃO (Login, Perfil, Logout)
  // =====================================================

  /// Faz login de usuário ou restaurante.
  /// [loginAs] deve ser `"user"` ou `"restaurant"`.
  static Future<Map<String, dynamic>> login({
    required String email,
    required String password,
    required String loginAs,
  }) async {
    final response = await _safeRequest(() async => http.post(
          Uri.parse("$authURL/auth/login"),
          headers: await _getHeaders(),
          body: jsonEncode({
            "email": email,
            "password": password,
            "login_as": loginAs,
          }),
        ));

    final body = jsonDecode(response.body);
    if (response.statusCode == 200) {
      final token = body['access_token'];
      if (token is String && token.isNotEmpty) {
        await _setToken(token);
      }
      return body;
    }
    throw Exception(body['detail'] ?? 'Falha no login (${response.statusCode})');
  }
 /// Retorna informações do usuário autenticado
  static Future<Map<String, dynamic>> getMe() async {
    final response = await _safeRequest(() async => http.get(
          Uri.parse("$authURL/auth/me"),
          headers: await _getHeaders(includeAuth: true),
        ));

    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else {
      throw Exception("Erro ao buscar perfil (${response.statusCode})");
    }
  }
  /// Encerra a sessão limpando o token salvo
  static Future<void> logout() async {
    await _storage.delete(key: 'auth_token');
  }

  // =====================================================
  // 👤 USUÁRIOS
  // =====================================================

  static Future<Map<String, dynamic>> createUser(Map<String, dynamic> user) async {
    final response = await _safeRequest(() async => http.post(
          Uri.parse("$baseUrl/user/create"),
          headers: await _getHeaders(),
          body: jsonEncode(user),
        ));

    if (response.statusCode == 201) {
      return jsonDecode(response.body);
    } else {
      throw Exception("Erro ao criar usuário: ${response.body}");
    }
  }

  static Future<Map<String, dynamic>> getUserByEmail(String email) async {
    final response = await _safeRequest(() async => http.get(
          Uri.parse("$baseUrl/user/email/$email"),
          headers: await _getHeaders(includeAuth: true),
        ));

    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else if (response.statusCode == 404) {
      throw Exception("Usuário não encontrado");
    } else {
      throw Exception("Erro ao buscar usuário (${response.statusCode})");
    }
  }

  static Future<Map<String, dynamic>> updateUser(Map<String, dynamic> user) async {
    final response = await _safeRequest(() async => http.put(
          Uri.parse("$baseUrl/user/update"),
          headers: await _getHeaders(includeAuth: true),
          body: jsonEncode(user),
        ));

    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else {
      throw Exception("Erro ao atualizar usuário: ${response.body}");
    }
  }

    // =====================================================
  // 🍽️ RESTAURANTES
  // =====================================================

  static Future<Map<String, dynamic>> createRestaurant(Map<String, dynamic> restaurant) async {
    final response = await _safeRequest(() async => http.post(
          Uri.parse("$baseUrl/restaurant/create"),
          headers: await _getHeaders(),
          body: jsonEncode(restaurant),
        ));

    if (response.statusCode == 201) {
      return jsonDecode(response.body);
    } else {
      throw Exception("Erro ao criar restaurante: ${response.body}");
    }
  }

  static Future<Map<String, dynamic>> getRestaurantByCnpj(String cnpj) async {
    final response = await _safeRequest(() async => http.get(
          Uri.parse("$baseUrl/restaurant/$cnpj"),
          headers: await _getHeaders(includeAuth: true),
        ));

    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else if (response.statusCode == 404) {
      throw Exception("Restaurante não encontrado");
    } else {
      throw Exception("Erro ao buscar restaurante (${response.statusCode})");
    }
  }

  static Future<Map<String, dynamic>> updateRestaurant(Map<String, dynamic> restaurant) async {
    final response = await _safeRequest(() async => http.put(
          Uri.parse("$baseUrl/restaurant/update"),
          headers: await _getHeaders(includeAuth: true),
          body: jsonEncode(restaurant),
        ));

    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else {
      throw Exception("Erro ao atualizar restaurante: ${response.body}");
    }
  }

  static Future<Map<String, dynamic>> updateOccupancy(String cnpj, int newOccupancy) async {
    final response = await _safeRequest(() async => http.patch(
          Uri.parse("$baseUrl/restaurant/occupancy/$cnpj"),
          headers: await _getHeaders(includeAuth: true),
          body: jsonEncode({"new_occupancy": newOccupancy}),
        ));

    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else {
      throw Exception("Erro ao atualizar ocupação: ${response.body}");
    }
  }
}