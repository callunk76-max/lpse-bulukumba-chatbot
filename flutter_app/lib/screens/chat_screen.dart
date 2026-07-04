import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../models/chat_message.dart';
import '../services/chat_service.dart';

class ChatScreen extends StatefulWidget {
  const ChatScreen({Key? key}) : super(key: key);

  @override
  State<ChatScreen> createState() => _ChatScreenState();
}

class _ChatScreenState extends State<ChatScreen> {
  final TextEditingController _controller = TextEditingController();
  bool _isLoading = false;

  @override
  Widget build(BuildContext context) {
    final chatService = Provider.of<ChatService>(context);
    return Scaffold(
      appBar: AppBar(
        title: const Text('LPSE Bulukumba Chatbot'),
      ),
      body: Column(
        children: [
          Expanded(
            child: ListView.builder(
              reverse: true,
              itemCount: chatService.messages.length,
              itemBuilder: (context, index) {
                final msg = chatService.messages[chatService.messages.length - 1 - index];
                return _buildMessageBubble(msg);
              },
            ),
          ),
          if (_isLoading) const LinearProgressIndicator(),
          _buildInputArea(),
        ],
      ),
    );
  }

  Widget _buildMessageBubble(ChatMessage msg) {
    final isUser = msg.role == 'user';
    return Align(
      alignment: isUser ? Alignment.centerRight : Alignment.centerLeft,
      child: Container(
        margin: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
        padding: const EdgeInsets.all(12),
        decoration: BoxDecoration(
          color: isUser ? Colors.indigo.shade100 : Colors.grey.shade200,
          borderRadius: BorderRadius.circular(12),
        ),
        child: Text(msg.content),
      ),
    );
  }

  Widget _buildInputArea() {
    final chatService = Provider.of<ChatService>(context, listen: false);
    return Padding(
      padding: const EdgeInsets.all(8.0),
      child: Row(
        children: [
          Expanded(
            child: TextField(
              controller: _controller,
              textInputAction: TextInputAction.send,
              onSubmitted: (_) => _sendMessage(),
              decoration: const InputDecoration(
                hintText: 'Ketik pertanyaan…',
                border: OutlineInputBorder(),
              ),
            ),
          ),
          const SizedBox(width: 8),
          IconButton(
            icon: const Icon(Icons.send),
            color: Colors.indigo,
            onPressed: _sendMessage,
          ),
        ],
      ),
    );
  }

  Future<void> _sendMessage() async {
    final text = _controller.text.trim();
    if (text.isEmpty) return;
    _controller.clear();
    setState(() => _isLoading = true);
    final chatService = Provider.of<ChatService>(context, listen: false);
    await chatService.sendMessage(text);
    setState(() => _isLoading = false);
  }
}
