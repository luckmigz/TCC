import 'package:flutter/material.dart';

class PerfilDesign extends StatelessWidget {
  final String userName;
  final String userEmail;
  final VoidCallback onSignOut;
  final VoidCallback onDeleteAccount;
  final Color appBarColor;
  final Color iconColor;
  final String logoPath;
  final String logoAppBarPath;

  const PerfilDesign({
    super.key,
    required this.userName,
    required this.userEmail,
    required this.onSignOut,
    required this.onDeleteAccount,
    this.appBarColor = const Color.fromRGBO(46, 133, 157, 1),
    this.iconColor = Colors.blue,
    this.logoPath = "logo.png",
    this.logoAppBarPath = "logo.png",
  });

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text(
          "Perfil",
          style: TextStyle(fontWeight: FontWeight.bold),
        ),
        backgroundColor: appBarColor,
        actions: [
          Padding(
            padding: const EdgeInsets.only(right: 16.0),
            child: Image.asset(
              logoAppBarPath,
              height: 50,
              fit: BoxFit.contain,
            ),
          ),
        ],
      ),
      body: Padding(
        padding: const EdgeInsets.all(20.0),
        child: Column(
          children: [
            const SizedBox(height: 20),
            Container(
              width: double.infinity,
              decoration: BoxDecoration(
                color: Colors.grey[200],
                borderRadius: BorderRadius.circular(16),
              ),
              padding: const EdgeInsets.all(20),
              child: Column(
                children: [
                  const SizedBox(height: 20),
                  const CircleAvatar(
                    radius: 40,
                    backgroundColor: Colors.grey,
                    child: Icon(Icons.person, size: 50, color: Colors.white),
                  ),
                  const SizedBox(height: 10),
                  Text(
                    userName,
                    style: const TextStyle(
                      fontWeight: FontWeight.bold,
                      fontSize: 16,
                    ),
                  ),
                  Text(
                    userEmail,
                    style: const TextStyle(color: Colors.black54),
                  ),
                  const SizedBox(height: 20),
                  ElevatedButton(
                    onPressed: onSignOut,
                    style: ElevatedButton.styleFrom(
                      backgroundColor: const Color.fromRGBO(225, 105, 30, 1),
                      minimumSize: const Size(150, 45),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(8),
                      ),
                    ),
                    child: const Text(
                      "SIGN OUT",
                      style: TextStyle(
                        color: Colors.white,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 20),
            TextButton(
              onPressed: onDeleteAccount,
              child: const Text(
                "DELETE ACCOUNT",
                style: TextStyle(
                  color: Colors.redAccent,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ),
            const SizedBox(height: 30),
            Expanded(
              child: ListView(
                children: const [
                  _UserOption(icon: Icons.person, title: "Account"),
                  _UserOption(icon: Icons.payments, title: "Payments"),
                  _UserOption(icon: Icons.devices, title: "Devices"),
                  _UserOption(icon: Icons.bar_chart, title: "Stats"),
                  _UserOption(icon: Icons.help_outline, title: "Help"),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _UserOption extends StatelessWidget {
  final IconData icon;
  final String title;

  const _UserOption({required this.icon, required this.title});

  @override
  Widget build(BuildContext context) {
    return ListTile(
      leading: Icon(icon, color: Colors.black87),
      title: Text(title),
      trailing: const Icon(Icons.arrow_forward_ios, size: 16),
      onTap: () {},
    );
  }
}
