# DOKUMENTASI TEKNIS CHATBOT LPSE BULUKUMBA

---

## A. ARSITEKTUR SISTEM

### Skema Umum
```
┌─────────────────────────────────────────────────────────────┐
│                    FLUTTER MOBILE APP                      │
│  - UI Chat Interface                                        │
│  - Local Cache (SQLite/Hive)                                │
│  - State Management (Riverpod)                              │
│  - API Client (Dio)                                         │
└────────────────────────┬────────────────────────────────────┘
                         │ (REST API over HTTPS)
┌────────────────────────▼────────────────────────────────────┐
│               BACKEND SERVER (Node.js/Express)              │
│  - API Endpoint Handler                                     │
│  - Request Validation                                       │
│  - Response Formatting                                      │
│  - Error Handling                                           │
└────────────────────────┬────────────────────────────────────┘
                         │
         ┌───────────────┼───────────────┐
         │               │               │
┌────────▼───┐  ┌────────▼────┐  ┌─────▼────────┐
│ PostgreSQL │  │ Redis Cache │  │ Milvus/BM25  │
│ (Database) │  │ (Session)   │  │ (Semantic    │
│            │  │             │  │  Search)     │
└────────────┘  └─────────────┘  └──────────────┘
```

---

## B. TEKNOLOGI & DEPENDENCIES

### Frontend (Flutter/Dart)

**Core Dependencies:**
```yaml
# pubspec.yaml essentials
dependencies:
  flutter:
    sdk: flutter
  
  # State Management
  riverpod: ^2.x.x
  flutter_riverpod: ^2.x.x
  
  # HTTP Client
  dio: ^5.x.x
  
  # Local Storage
  hive: ^2.x.x
  hive_flutter: ^1.x.x
  
  # UI Components
  flutter_markdown: ^0.6.x
  intl: ^0.19.x
  
  # Other utilities
  uuid: ^4.x.x
  connectivity_plus: ^5.x.x
  
dev_dependencies:
  flutter_test:
    sdk: flutter
  hive_generator: ^2.x.x
  build_runner: ^2.x.x
```

---

### Backend (Node.js)

**Stack:**
- Runtime: Node.js 18+ LTS
- Framework: Express.js
- Database: PostgreSQL 14+
- Cache: Redis 7+
- Search: Milvus (untuk semantic search) atau BM25 (Elasticsearch)

**Package.json Minimal:**
```json
{
  "name": "lpse-bulukumba-chatbot-api",
  "version": "1.0.0",
  "main": "src/index.js",
  "type": "module",
  
  "dependencies": {
    "express": "^4.18.x",
    "dotenv": "^16.x.x",
    "pg": "^8.x.x",
    "redis": "^4.x.x",
    "jsonwebtoken": "^9.x.x",
    "cors": "^2.8.x",
    "helmet": "^7.x.x",
    "zod": "^3.x.x",
    "axios": "^1.x.x"
  },
  
  "devDependencies": {
    "nodemon": "^3.x.x",
    "eslint": "^8.x.x"
  },
  
  "scripts": {
    "start": "node src/index.js",
    "dev": "nodemon src/index.js",
    "test": "node --test"
  }
}
```

---

## C. STRUKTUR FOLDER BACKEND

```
backend/
├── src/
│   ├── index.js                    # Entry point
│   ├── config/
│   │   ├── database.js             # PostgreSQL connection
│   │   ├── redis.js                # Redis client
│   │   └── env.js                  # Environment variables
│   ├── middleware/
│   │   ├── auth.js                 # JWT authentication
│   │   ├── errorHandler.js         # Error handling
│   │   └── requestValidator.js     # Zod validation
│   ├── routes/
│   │   ├── chatbot.routes.js        # Chat endpoint
│   │   ├── auth.routes.js           # Authentication
│   │   └── procurement.routes.js    # Procurement info
│   ├── controllers/
│   │   ├── chatController.js        # Chat logic
│   │   ├── authController.js
│   │   └── procurementController.js
│   ├── services/
│   │   ├── chatService.js          # Core chat logic
│   │   ├── searchService.js        # Knowledge base search
│   │   ├── claudeService.js        # Claude API integration
│   │   └── cacheService.js         # Caching logic
│   ├── models/
│   │   ├── ChatMessage.js
│   │   ├── User.js
│   │   └── KnowledgeBase.js
│   ├── utils/
│   │   ├── logger.js
│   │   ├── validators.js
│   │   └── helpers.js
│   └── knowledge_base/
│       ├── data.json               # KB structured data
│       └── embeddings.json         # Pre-computed embeddings
├── database/
│   ├── migrations/
│   │   ├── 001_create_users.sql
│   │   ├── 002_create_messages.sql
│   │   └── 003_create_kb.sql
│   └── schema.sql
├── docker/
│   ├── Dockerfile
│   └── docker-compose.yml
├── .env.example
├── .gitignore
└── README.md
```

---

## D. DATABASE SCHEMA (PostgreSQL)

### Tabel Users
```sql
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  phone_number VARCHAR(15) UNIQUE NOT NULL,
  company_name VARCHAR(255),
  user_type VARCHAR(50), -- 'penyedia', 'calon_penyedia', 'umum'
  is_verified BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_users_phone ON users(phone_number);
```

### Tabel Chat Messages
```sql
CREATE TABLE chat_messages (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id),
  message_type VARCHAR(50), -- 'user', 'bot'
  content TEXT NOT NULL,
  is_helpful BOOLEAN, -- untuk rating
  metadata JSONB, -- extra data
  created_at TIMESTAMP DEFAULT NOW(),
  
  FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE INDEX idx_chat_user_id ON chat_messages(user_id);
CREATE INDEX idx_chat_created_at ON chat_messages(created_at);
```

### Tabel Knowledge Base
```sql
CREATE TABLE knowledge_base (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  category VARCHAR(100),
  subcategory VARCHAR(100),
  question TEXT,
  answer TEXT,
  keywords TEXT[], -- untuk pencarian
  section_reference VARCHAR(100), -- refer ke knowledge base doc
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_kb_category ON knowledge_base(category);
CREATE INDEX idx_kb_keywords ON knowledge_base USING GIN(keywords);
```

### Tabel Sessions (Optional, untuk tracking)
```sql
CREATE TABLE chat_sessions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id),
  session_start TIMESTAMP DEFAULT NOW(),
  session_end TIMESTAMP,
  message_count INTEGER DEFAULT 0,
  resolved BOOLEAN DEFAULT FALSE,
  
  FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE INDEX idx_sessions_user_id ON chat_sessions(user_id);
```

---

## E. API ENDPOINTS

### 1. Authentication

#### POST /api/auth/register
```json
Request:
{
  "phone_number": "085212345678",
  "company_name": "PT Contoh Jaya",
  "user_type": "penyedia"
}

Response (201):
{
  "success": true,
  "user_id": "uuid-xxx",
  "message": "Pendaftaran berhasil",
  "verification_required": true
}
```

#### POST /api/auth/verify
```json
Request:
{
  "phone_number": "085212345678",
  "otp_code": "123456"
}

Response (200):
{
  "success": true,
  "token": "jwt-token-xxx",
  "expires_in": 86400
}
```

---

### 2. Chat Endpoint

#### POST /api/chat/message
```json
Request:
{
  "message": "Bagaimana cara mendaftar di LPSE Bulukumba?",
  "session_id": "uuid-optional",
  "context": {
    "user_type": "calon_penyedia",
    "previous_intent": "pendaftaran"
  }
}

Response (200):
{
  "success": true,
  "bot_response": "Untuk mendaftar di LPSE Bulukumba, ikuti langkah-langkah berikut...",
  "session_id": "uuid-xxx",
  "metadata": {
    "category": "pendaftaran",
    "confidence": 0.95,
    "sources": ["section_4", "faq.registration"],
    "follow_up_suggested": true,
    "follow_up_questions": [
      "Apa saja dokumen yang diperlukan?",
      "Berapa lama proses verifikasi?"
    ]
  }
}
```

---

### 3. Procurement Information

#### GET /api/procurement/methods
```json
Response (200):
{
  "success": true,
  "methods": [
    {
      "name": "Tender",
      "value": "tender",
      "description": "...",
      "requirements": [],
      "timeline": "30-60 hari"
    },
    // ... more methods
  ]
}
```

#### GET /api/procurement/faq
```json
Request Query:
  ?category=pendaftaran
  ?search_term=HPS
  ?limit=10

Response (200):
{
  "success": true,
  "faqs": [
    {
      "id": "faq-001",
      "question": "Apa itu HPS?",
      "answer": "HPS adalah Harga Perkiraan Sendiri...",
      "category": "lelang",
      "helpful_count": 123
    }
  ]
}
```

---

## F. CHATBOT LOGIC FLOW

### Core Chat Processing Pipeline

```javascript
// services/chatService.js pseudocode

class ChatService {
  async processMessage(userMessage, userId, context) {
    // 1. Pre-processing
    const cleanedMessage = this.normalizeText(userMessage);
    const language = this.detectLanguage(cleanedMessage); // assume Indonesian
    
    // 2. Intent Recognition
    const intent = await this.intentClassifier.classify(cleanedMessage);
    // Output: {intent: "ask_registration", confidence: 0.92}
    
    // 3. Entity Extraction
    const entities = await this.entityExtractor.extract(cleanedMessage);
    // Output: {method: "tender", value: "123456"}
    
    // 4. Knowledge Base Search
    const relevantDocs = await this.searchKnowledgeBase(
      cleanedMessage, 
      intent, 
      entities
    );
    
    // 5. Response Generation
    let response;
    
    if (intent.confidence > 0.8) {
      // High confidence - use KB directly
      response = await this.generateFromKB(relevantDocs, entities);
    } else {
      // Low confidence - ask for clarification or use Claude
      response = await this.claudeService.generateResponse(
        userMessage,
        relevantDocs,
        context
      );
    }
    
    // 6. Post-processing
    const formattedResponse = this.formatResponse(response);
    
    // 7. Caching & Logging
    await this.cacheResponse(userMessage, formattedResponse);
    await this.logMessage(userId, userMessage, formattedResponse);
    
    return {
      response: formattedResponse,
      metadata: {
        intent,
        entities,
        sources: relevantDocs.map(d => d.reference),
        confidence: intent.confidence
      }
    };
  }
  
  async searchKnowledgeBase(query, intent, entities) {
    // 1. Hybrid Search approach
    
    // Keyword search (BM25)
    const keywordResults = await this.bm25Search(query);
    
    // Semantic search (vector similarity)
    const embeddedQuery = await this.embedText(query);
    const semanticResults = await this.vectorSearch(embeddedQuery);
    
    // Category-based search
    const categoryResults = intent 
      ? await this.categorySearch(intent)
      : [];
    
    // Combine & deduplicate
    const combined = this.combineResults(
      keywordResults, 
      semanticResults, 
      categoryResults
    );
    
    return combined.slice(0, 5); // Top 5 results
  }
  
  generateFromKB(docs, entities) {
    // Template-based response generation
    const primaryDoc = docs[0];
    
    // Format with markdown
    let response = `**${primaryDoc.title}**\n\n`;
    response += primaryDoc.content;
    
    // Add related info if relevant
    if (docs.length > 1) {
      response += `\n\n**Informasi terkait:**\n`;
      docs.slice(1, 3).forEach(doc => {
        response += `- ${doc.title}\n`;
      });
    }
    
    return response;
  }
}
```

---

## G. INTEGRASI CLAUDE API (OPTIONAL)

Jika ingin menggunakan Claude untuk response generation yang lebih natural:

```javascript
// services/claudeService.js

import Anthropic from "@anthropic-ai/sdk";

class ClaudeService {
  constructor() {
    this.client = new Anthropic({
      apiKey: process.env.CLAUDE_API_KEY,
    });
  }

  async generateResponse(userMessage, knowledgeContext, conversationHistory) {
    const systemPrompt = `
      Anda adalah chatbot profesional untuk LPSE (Layanan Pengadaan Secara Elektronik) 
      Kabupaten Bulukumba. Gunakan informasi berikut untuk menjawab pertanyaan pengguna:
      
      ${knowledgeContext.map(doc => `
        - **${doc.category}**: ${doc.content}
      `).join('\n')}
      
      Berikan jawaban yang:
      1. Akurat dan berdasarkan regulasi terbaru (Perpres 16 Tahun 2018 dan perubahannya)
      2. Jelas dan mudah dipahami oleh penyedia barang/jasa
      3. Selalu referensikan sumber regulasi jika diperlukan
      4. Tanyakan klarifikasi jika pertanyaan ambigu
      5. Tawarkan bantuan lebih lanjut
    `;

    const response = await this.client.messages.create({
      model: "claude-opus-4-6", // atau sonnet-4-6 untuk balance
      max_tokens: 1000,
      system: systemPrompt,
      messages: [
        ...conversationHistory, // Previous messages
        {
          role: "user",
          content: userMessage,
        },
      ],
    });

    return response.content[0].text;
  }
}
```

---

## H. FLUTTER CHATBOT UI

### Struktur Folder Frontend
```
flutter_app/
├── lib/
│   ├── main.dart
│   ├── models/
│   │   ├── message.dart
│   │   ├── user.dart
│   │   └── procurement.dart
│   ├── providers/
│   │   ├── chat_provider.dart       # Riverpod
│   │   ├── auth_provider.dart
│   │   └── ui_provider.dart
│   ├── screens/
│   │   ├── splash_screen.dart
│   │   ├── login_screen.dart
│   │   ├── chat_screen.dart         # Main chat UI
│   │   └── info_screen.dart
│   ├── widgets/
│   │   ├── message_bubble.dart
│   │   ├── chat_input.dart
│   │   └── suggestion_chips.dart
│   ├── services/
│   │   ├── api_service.dart         # Dio HTTP client
│   │   ├── local_storage.dart       # Hive
│   │   └── notification_service.dart
│   └── utils/
│       ├── colors.dart
│       ├── strings.dart
│       └── validators.dart
├── assets/
│   ├── images/
│   └── fonts/
├── pubspec.yaml
└── README.md
```

### Contoh Chat Provider (Riverpod)
```dart
// lib/providers/chat_provider.dart

import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../services/api_service.dart';

final chatProvider = StateNotifierProvider<ChatNotifier, List<Message>>((ref) {
  final apiService = ref.watch(apiServiceProvider);
  return ChatNotifier(apiService);
});

class ChatNotifier extends StateNotifier<List<Message>> {
  final ApiService _apiService;
  
  ChatNotifier(this._apiService) : super([]);
  
  Future<void> sendMessage(String userMessage) async {
    // Add user message to state
    state = [...state, Message(
      id: DateTime.now().toString(),
      content: userMessage,
      isUser: true,
      timestamp: DateTime.now(),
    )];
    
    try {
      // Call backend
      final response = await _apiService.post('/chat/message', {
        'message': userMessage,
        'session_id': _currentSessionId,
      });
      
      // Add bot response
      state = [...state, Message(
        id: response['bot_response_id'],
        content: response['bot_response'],
        isUser: false,
        timestamp: DateTime.now(),
        metadata: response['metadata'],
      )];
    } catch (e) {
      // Handle error
      state = [...state, Message(
        id: DateTime.now().toString(),
        content: 'Maaf, ada kesalahan. Silakan coba lagi.',
        isUser: false,
        timestamp: DateTime.now(),
      )];
    }
  }
}
```

---

## I. DOCKER SETUP

### Dockerfile Backend
```dockerfile
FROM node:18-alpine

WORKDIR /app

COPY package*.json ./
RUN npm ci --only=production

COPY src ./src
COPY database ./database

EXPOSE 3000

ENV NODE_ENV=production

CMD ["npm", "start"]
```

### docker-compose.yml
```yaml
version: '3.8'

services:
  postgres:
    image: postgres:14-alpine
    environment:
      POSTGRES_DB: lpse_chatbot
      POSTGRES_USER: lpse_user
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./database/schema.sql:/docker-entrypoint-initdb.d/1-schema.sql
    ports:
      - "5432:5432"
    networks:
      - lpse_network

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    networks:
      - lpse_network

  backend:
    build: .
    ports:
      - "3000:3000"
    environment:
      DATABASE_URL: postgresql://lpse_user:${DB_PASSWORD}@postgres:5432/lpse_chatbot
      REDIS_URL: redis://redis:6379
      NODE_ENV: ${NODE_ENV}
      CLAUDE_API_KEY: ${CLAUDE_API_KEY}
    depends_on:
      - postgres
      - redis
    networks:
      - lpse_network

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./certs:/etc/nginx/certs:ro
    depends_on:
      - backend
    networks:
      - lpse_network

volumes:
  postgres_data:
  redis_data:

networks:
  lpse_network:
    driver: bridge
```

---

## J. ENVIRONMENT VARIABLES (.env)

```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/lpse_chatbot
DB_HOST=localhost
DB_PORT=5432
DB_USER=lpse_user
DB_PASSWORD=your_secure_password
DB_NAME=lpse_chatbot

# Redis
REDIS_URL=redis://localhost:6379
REDIS_PASSWORD=optional_redis_password

# Server
NODE_ENV=development
PORT=3000
LOG_LEVEL=info

# JWT
JWT_SECRET=your_jwt_secret_key_here
JWT_EXPIRES_IN=86400

# CORS
CORS_ORIGIN=http://localhost:8080,https://yourdomain.com

# Claude API (optional)
CLAUDE_API_KEY=your_claude_api_key

# App
APP_NAME=LPSE Bulukumba Chatbot
VERSION=1.0.0
```

---

## K. DEPLOYMENT

### VPS Setup (Ubuntu 22.04)

#### 1. Prepare Server
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y \
  curl \
  wget \
  git \
  docker.io \
  docker-compose \
  nginx \
  certbot \
  python3-certbot-nginx

# Start Docker
sudo systemctl enable docker
sudo systemctl start docker

# Add current user to docker group
sudo usermod -aG docker $USER
```

#### 2. Clone & Setup Project
```bash
cd /var/www
git clone https://github.com/yourusername/lpse-chatbot.git
cd lpse-chatbot

# Setup environment
cp .env.example .env
# Edit .env with production values
nano .env

# Build Docker images
docker-compose build

# Run migrations
docker-compose exec backend npm run migrate
```

#### 3. Start Services
```bash
# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f backend
```

#### 4. SSL Certificate (Let's Encrypt)
```bash
sudo certbot certonly --standalone -d yourdomain.com

# Auto-renew
sudo systemctl enable certbot.timer
sudo systemctl start certbot.timer
```

#### 5. Nginx Configuration
```nginx
server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    location /api {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    location / {
        # Static files or mobile app download
        root /var/www/lpse-chatbot/public;
    }
}

server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$server_name$request_uri;
}
```

---

## L. MONITORING & LOGGING

### Application Logging
```javascript
// utils/logger.js
import winston from 'winston';

const logger = winston.createLogger({
  level: process.env.LOG_LEVEL || 'info',
  format: winston.format.json(),
  transports: [
    new winston.transports.File({ filename: 'logs/error.log', level: 'error' }),
    new winston.transports.File({ filename: 'logs/combined.log' }),
    new winston.transports.Console({
      format: winston.format.simple()
    })
  ]
});

export default logger;
```

### Monitoring Stack
- **PM2** untuk process management
- **ELK Stack** atau **Grafana** untuk visualization
- **Sentry** untuk error tracking (optional)

---

## M. TESTING STRATEGY

### Backend Testing
```bash
# Unit tests
npm test -- --reporter=verbose

# Integration tests
npm run test:integration

# Coverage
npm run test:coverage
```

### Frontend Testing
```bash
# Widget tests
flutter test

# Integration tests
flutter drive --target=test_driver/app.dart
```

---

## N. SECURITY CHECKLIST

- ✅ Use HTTPS/TLS everywhere
- ✅ Implement JWT with short expiry
- ✅ Rate limiting on API endpoints
- ✅ Input validation & sanitization
- ✅ SQL injection prevention (use parameterized queries)
- ✅ CORS properly configured
- ✅ Sensitive data encrypted at rest
- ✅ Regular security updates
- ✅ Database backups automated
- ✅ Monitoring & alerting configured

---

## O. TIMELINE IMPLEMENTASI

**Phase 1 (Minggu 1-2): Foundation**
- Setup project structure
- Database design & migrations
- Basic API endpoints

**Phase 2 (Minggu 2-3): Backend Core**
- Chat service implementation
- Knowledge base search
- Authentication & authorization

**Phase 3 (Minggu 3-4): Frontend**
- Flutter project setup
- Chat UI implementation
- API integration

**Phase 4 (Minggu 4-5): Integration & Testing**
- End-to-end testing
- Performance optimization
- Bug fixes

**Phase 5 (Minggu 5-6): Deployment**
- Production setup
- SSL certificates
- Monitoring setup
- Launch

---

## P. ESTIMASI RESOURCES

| Item | Estimasi |
|------|----------|
| Development | 4-6 minggu (1 developer fullstack) |
| VPS Bulanan | Rp 200k - Rp 500k (tergantung traffic) |
| Domain | Rp 70k - Rp 150k/tahun |
| SSL Certificate | Gratis (Let's Encrypt) |
| Backup Storage | Rp 50k - Rp 100k/bulan |

---

**Dokumen ini akan diupdate seiring perkembangan project.**

---
