class User {
  final String name;
  final String email;
  final String password;
  final String cpf;

  User({
    required this.name,
    required this.email,
    required this.password,
    required this.cpf,
  });

  // --- ADICIONE ESTE MÉTODO ---
  Map<String, dynamic> toJson() {
    return {
      'name': name,
      'email': email,
      'password': password,
      'cpf': cpf,
    };
  }
}