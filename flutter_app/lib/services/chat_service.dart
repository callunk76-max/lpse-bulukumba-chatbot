import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import '../models/chat_message.dart';

class ChatService extends ChangeNotifier {
  final List<ChatMessage> _messages = [];
  List<ChatMessage> get messages => List<ChatMessage>.unmodifiable(_messages);

  final String _baseUrl = 'http://10.0.2.2:5015'; // Adjust when running on device/emulator

  Future<void> sendMessage(String userText) async {
    // Add user message locally
    _messages.add(ChatMessage(role: 'user', content: userText));
    notifyListeners();

    // Call backend
    try {
      final resp = await http.post(
        Uri.parse('$_baseUrl/chat'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'query': userText,
          'source_filter': 'all',
        }),
      );

      if (resp.statusCode == 200) {
        final data = jsonDecode(resp.body);
        final answer = data['answer'] ?? 'Tidak ada jawaban.';
        _messages.add(ChatMessage(role: 'assistant', content: answer));
      } else {
        _messages.add(ChatMessage(
          role: 'assistant',
          content: 'Error ${resp.statusCode}: ${resp.reasonPhrase}',
        ));
      }
    } catch (e) {
      _messages.add(ChatMessage(
        role: 'assistant',
        content: 'Gagal menghubungi server: $e',
      ));
    }
    notifyListeners();
  }
}
