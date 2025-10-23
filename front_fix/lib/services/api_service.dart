import 'dart:convert';
import 'package:http/http.dart' as http;

// 🌐 URLs base dos microserviços
const String authURL = "https://tcc-user-auth-dbaeb4cec5d9.herokuapp.com";
const String baseUrl = "https://tcc-user-db-530d29de8ef0.herokuapp.com";
const String analyticsURL = "http://0.0.0.0:8000"; // FastAPI local (IA e Analytics)

class ApiService {
  // ===============================
  // 🔐 LOGIN E PERFIL
  // ===============================
  static Future<Map<String, dynamic>> login({
    required String email,
    required String password,
    required String loginAs,
  }) async {
    final url = Uri.parse("$authURL/login");
    final response = await http.post(
      url,
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        "email": email,
        "password": password,
        "login_as": loginAs,
      }),
    );

    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else {
      throw Exception("Erro ao fazer login: ${response.body}");
    }
  }

  static Future<Map<String, dynamic>> getMe(String token) async {
    final url = Uri.parse("$authURL/auth/me");
    final response = await http.get(
      url,
      headers: {"Authorization": "Bearer $token"},
    );

    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else {
      throw Exception("Token inválido ou expirado");
    }
  }

  // ===============================
  // 👤 USUÁRIOS
  // ===============================
  static Future<Map<String, dynamic>> createUser(Map<String, dynamic> user) async {
    final response = await http.post(
      Uri.parse("$baseUrl/user/create"),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode(user),
    );

    if (response.statusCode == 201) {
      return jsonDecode(response.body);
    } else {
      throw Exception("Erro ao criar usuário: ${response.body}");
    }
  }

  static Future<Map<String, dynamic>> getUserByEmail(String email) async {
    final response = await http.get(Uri.parse("$baseUrl/user/email/$email"));
    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else {
      throw Exception("Usuário não encontrado");
    }
  }

  static Future<Map<String, dynamic>> updateUser(Map<String, dynamic> user) async {
    final response = await http.put(
      Uri.parse("$baseUrl/user/update"),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode(user),
    );

    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else {
      throw Exception("Erro ao atualizar usuário: ${response.body}");
    }
  }

  static Future<void> deleteUser(String email) async {
    final response = await http.delete(Uri.parse("$baseUrl/user/delete/$email"));
    if (response.statusCode != 200) {
      throw Exception("Erro ao deletar usuário: ${response.body}");
    }
  }

  // ===============================
  // 🍽️ RESTAURANTES
  // ===============================
  static Future<Map<String, dynamic>> createRestaurant(Map<String, dynamic> restaurant) async {
    final response = await http.post(
      Uri.parse("$baseUrl/restaurant/create"),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode(restaurant),
    );

    if (response.statusCode == 201) {
      return jsonDecode(response.body);
    } else {
      throw Exception("Erro ao criar restaurante: ${response.body}");
    }
  }

  static Future<Map<String, dynamic>> getRestaurantByCnpj(String cnpj) async {
    final response = await http.get(Uri.parse("$baseUrl/restaurant/$cnpj"));
    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else {
      throw Exception("Restaurante não encontrado");
    }
  }

  static Future<Map<String, dynamic>> getRestaurantByEmail(String email) async {
    final response = await http.get(Uri.parse("$baseUrl/restaurant/email/$email"));
    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else {
      throw Exception("Restaurante não encontrado");
    }
  }

  static Future<Map<String, dynamic>> updateRestaurant(Map<String, dynamic> restaurant) async {
    final response = await http.put(
      Uri.parse("$baseUrl/restaurant/update"),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode(restaurant),
    );

    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else {
      throw Exception("Erro ao atualizar restaurante: ${response.body}");
    }
  }

  static Future<void> deleteRestaurant(String cnpj) async {
    final response = await http.delete(Uri.parse("$baseUrl/restaurant/delete/$cnpj"));
    if (response.statusCode != 200) {
      throw Exception("Erro ao deletar restaurante: ${response.body}");
    }
  }

  static Future<Map<String, dynamic>> updateOccupancy(String cnpj, int newOccupancy) async {
    final response = await http.patch(
      Uri.parse("$baseUrl/restaurant/occupancy/$cnpj"),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({"new_occupancy": newOccupancy}),
    );

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
    final url = Uri.parse("$analyticsURL/analytics/generate");
    final response = await http.post(
      url,
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({"cnpj": cnpj}),
    );

    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else {
      throw Exception("Erro ao obter dados de analytics: ${response.body}");
    }
  }
}
