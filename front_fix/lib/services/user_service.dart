class User {
  final String name;
  final String email;
  final String cnpj; // 🔹 Adicionado

  User({
    required this.name,
    required this.email,
    required this.cnpj,
  });
}

class UserService {
  static User? _currentUser;

  // Salva o usuário em memória
  static Future<void> saveUser(User? user) async {
    _currentUser = user;
  }

  // Retorna o usuário atual
  static User? getUser() => _currentUser;

  // Retorna o CNPJ do usuário atual (ou string vazia se não logado)
  static String get cnpj => _currentUser?.cnpj ?? '';

  // "Logout" = limpar usuário
  static Future<void> logout() async {
    _currentUser = null;
  }

  // 🔸 Caso futuramente precise armazenar dados analíticos locais
  static Map<String, dynamic> analyticsData = {};

  static void updateAnalytics(Map<String, dynamic> data) {
    analyticsData = data;
  }
}
