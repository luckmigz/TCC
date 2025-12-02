import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

// ===============================
// 🌐 URLs base dos microserviços
// ===============================
const String authURL = "https://tcc-user-auth-dbaeb4cec5d9.herokuapp.com";
const String baseUrl = "https://tcc-user-db-530d29de8ef0.herokuapp.com";
const String analyticsURL = "https://tcc-ia-analytics-914b4026a324.herokuapp.com";

// ===============================
// 🔧 API SERVICE UNIFICADO (com async/await correto)
// ===============================

// Torna a exceção pública para os widgets poderem capturar
class AuthExpiredException implements Exception {
  final String message;
  const AuthExpiredException([this.message = 'Sessão expirada. Faça login novamente.']);
  @override
  String toString() => 'AuthExpiredException: $message';
}

class ApiService {
  // Armazenamento seguro de token
  static const _storage = FlutterSecureStorage();

  // Lê token salvo
  static Future<String?> _getToken() async {
    return await _storage.read(key: 'auth_token');
  }

  // Gera cabeçalhos padrão + token opcional
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

  // Wrapper para requisições seguras (trata 401 e exceções de rede)
  static Future<http.Response> _safeRequest(
    Future<http.Response> Function() request,
  ) async {
    try {
      final response = await request();
      if (response.statusCode == 401) {
        await _storage.delete(key: 'auth_token');
        throw const AuthExpiredException();
      }
      return response;
    } catch (e) {
      // Propaga sessão expirada; demais erros são convertidos em erro de conexão
      if (e is AuthExpiredException) rethrow;
      throw Exception('Erro de conexão. Verifique sua rede ou servidor.');
    }
  }

  // ===============================
  // 🔐 LOGIN E PERFIL
  // ===============================
  static Future<Map<String, dynamic>> login({
    required String email,
    required String password,
    required String loginAs,
  }) async {
    final response = await _safeRequest(() async {
      return await http.post(
        Uri.parse("$authURL/auth/login"),
        headers: await _getHeaders(),
        body: jsonEncode({
          "email": email,
          "password": password,
          "login_as": loginAs,
        }),
      );
    });

    final body = jsonDecode(response.body);

    if (response.statusCode == 200 && body['access_token'] != null) {
      await _storage.write(key: 'auth_token', value: body['access_token']);
      return body;
    } else {
      throw Exception(body['detail'] ?? 'Erro no login (${response.statusCode})');
    }
  }

  static Future<Map<String, dynamic>> getMe() async {
    final response = await _safeRequest(() async {
      return await http.get(
        Uri.parse("$authURL/auth/me"),
        headers: await _getHeaders(includeAuth: true),
      );
    });

    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else {
      throw Exception("Erro ao buscar perfil: ${response.body}");
    }
  }

  static Future<void> logout() async {
    await _storage.delete(key: 'auth_token');
  }

  // ===============================
  // 👤 USUÁRIOS
  // ===============================
  static Future<Map<String, dynamic>> createUser(Map<String, dynamic> user) async {
    final response = await _safeRequest(() async {
      return await http.post(
        Uri.parse("$baseUrl/user/create"),
        headers: await _getHeaders(),
        body: jsonEncode(user),
      );
    });

    if (response.statusCode == 201) {
      return jsonDecode(response.body);
    } else {
      throw Exception("Erro ao criar usuário: ${response.body}");
    }
  }

  static Future<Map<String, dynamic>> getUserByEmail(String email) async {
    final response = await _safeRequest(() async {
      return await http.get(
        Uri.parse("$baseUrl/user/email/$email"),
        headers: await _getHeaders(),
      );
    });

    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else {
      throw Exception("Usuário não encontrado: ${response.body}");
    }
  }

  static Future<Map<String, dynamic>> updateUser(Map<String, dynamic> user) async {
    final response = await _safeRequest(() async {
      return await http.put(
        Uri.parse("$baseUrl/user/update"),
        headers: await _getHeaders(),
        body: jsonEncode(user),
      );
    });

    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else {
      throw Exception("Erro ao atualizar usuário: ${response.body}");
    }
  }

  static Future<void> deleteUser(String email) async {
    final response = await _safeRequest(() async {
      return await http.delete(
        Uri.parse("$baseUrl/user/delete/$email"),
        headers: await _getHeaders(),
      );
    });

    if (response.statusCode != 200) {
      throw Exception("Erro ao deletar usuário: ${response.body}");
    }
  }

  // ===============================
  // 🍽️ RESTAURANTES
  // ===============================
  static Future<Map<String, dynamic>> createRestaurant(Map<String, dynamic> restaurant) async {
    final response = await _safeRequest(() async {
      return await http.post(
        Uri.parse("$baseUrl/restaurant/create"),
        headers: await _getHeaders(),
        body: jsonEncode(restaurant),
      );
    });

    if (response.statusCode == 201) {
      return jsonDecode(response.body);
    } else {
      throw Exception("Erro ao criar restaurante: ${response.body}");
    }
  }

  static Future<Map<String, dynamic>> getRestaurantByCnpj(String cnpj) async {
    final response = await _safeRequest(() async {
      return await http.get(
        Uri.parse("$baseUrl/restaurant/$cnpj"),
        headers: await _getHeaders(),
      );
    });

    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else {
      throw Exception("Restaurante não encontrado: ${response.body}");
    }
  }

  static Future<Map<String, dynamic>> getRestaurantByEmail(String email) async {
    final response = await _safeRequest(() async {
      return await http.get(
        Uri.parse("$baseUrl/restaurant/email/$email"),
        headers: await _getHeaders(),
      );
    });

    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else {
      throw Exception("Restaurante não encontrado: ${response.body}");
    }
  }

  static Future<Map<String, dynamic>> updateRestaurant(Map<String, dynamic> restaurant) async {
    final response = await _safeRequest(() async {
      return await http.put(
        Uri.parse("$baseUrl/restaurant/update"),
        headers: await _getHeaders(),
        body: jsonEncode(restaurant),
      );
    });

    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else {
      throw Exception("Erro ao atualizar restaurante: ${response.body}");
    }
  }

  static Future<void> deleteRestaurant(String cnpj) async {
    final response = await _safeRequest(() async {
      return await http.delete(
        Uri.parse("$baseUrl/restaurant/delete/$cnpj"),
        headers: await _getHeaders(),
      );
    });

    if (response.statusCode != 200) {
      throw Exception("Erro ao deletar restaurante: ${response.body}");
    }
  }

  static Future<Map<String, dynamic>> updateOccupancy(String cnpj, int newOccupancy) async {
    final response = await _safeRequest(() async {
      return await http.patch(
        Uri.parse("$baseUrl/restaurant/occupancy/$cnpj"),
        headers: await _getHeaders(),
        body: jsonEncode({"new_occupancy": newOccupancy}),
      );
    });

    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else {
      throw Exception("Erro ao atualizar ocupação: ${response.body}");
    }
  }

  // ===============================
  // 📊 ANALYTICS
  // ===============================
  static Future<Map<String, dynamic>> getAnalyticsData(String cnpj) async {
    final response = await _safeRequest(() async {
      return await http.post(
        Uri.parse("$analyticsURL/analytics/generate"),
        headers: await _getHeaders(),
        body: jsonEncode({"cnpj": cnpj}),
      );
    });
if (response.statusCode == 200 || response.statusCode == 201) {
    final data = jsonDecode(response.body);
   
    return data;
  } else {
 
    throw Exception("Erro ao obter dados de analytics: ${response.body}");
  }
  }
static Future<Map<String, dynamic>> getReportsData(String cnpj) async {
    final response = await _safeRequest(() async {
      return await http.post(
        Uri.parse("$analyticsURL/reports/generate"),
        headers: await _getHeaders(),
        body: jsonEncode({"cnpj": cnpj}),
      );
    });
if (response.statusCode == 200 || response.statusCode == 201) {
    final data = jsonDecode(response.body);
   
    return data;
  } else {
 
    throw Exception("Erro ao obter dados de analytics: ${response.body}");
  }
  }
}



