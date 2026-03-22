import 'package:shared_preferences/shared_preferences.dart';

class SessionStore {
  static const String _tokenKey = 'dala.auth_token';

  Future<String?> readToken() async {
    final preferences = await SharedPreferences.getInstance();
    return preferences.getString(_tokenKey);
  }

  Future<void> writeToken(String token) async {
    final preferences = await SharedPreferences.getInstance();
    await preferences.setString(_tokenKey, token);
  }

  Future<void> clear() async {
    final preferences = await SharedPreferences.getInstance();
    await preferences.remove(_tokenKey);
  }
}
