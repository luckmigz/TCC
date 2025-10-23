class User {
  final String name;
  final String email;
  final String cnpj;

  User({
    required this.name,
    required this.email,
    required this.cnpj,
  });

  // Cria um User a partir de um JSON do backend
  factory User.fromJson(Map<String, dynamic> json) {
    return User(
      name: json['name'] ?? '',
      email: json['email'] ?? '',
      cnpj: json['cnpj'] ?? '',
    );
  }

  // Converte para JSON (se necessário enviar)
  Map<String, dynamic> toJson() {
    return {
      'name': name,
      'email': email,
      'cnpj': cnpj,
    };
  }
}
