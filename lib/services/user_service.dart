class User {
  final String name;
  final String email;

  User({required this.name, required this.email});
}

class UserService {
  static User? _currentUser;

  // Salva usuário em memória
  static Future<void> saveUser(User? user) async {
    _currentUser = user;
  }

  // Retorna usuário
  static User? getUser() => _currentUser;

  // "Logout" = limpar usuário
  static Future<void> logout() async {
    _currentUser = null;
  }

  // Dados do restaurante simulados
  static int mesasDisponiveis = 4;
  static int totalMesas = 10;
  static String mesaAtual = "Mesa 4";
  static String tempoMesa = "30min";
  static int numeroClientes = 12;
  static double valorMesaMaisUsada = 150.0;

  // Métodos para atualizar dados do restaurante
  static void updateMesas({int? disponiveis, int? total}) {
    if (disponiveis != null) mesasDisponiveis = disponiveis;
    if (total != null) totalMesas = total;
  }

  static void updateMesaAtual(String mesa, String tempo) {
    mesaAtual = mesa;
    tempoMesa = tempo;
  }

  static void updateAnalise({int? clientes, double? valorMaisUsada}) {
    if (clientes != null) numeroClientes = clientes;
    if (valorMaisUsada != null) valorMesaMaisUsada = valorMaisUsada;
  }
}
