# LPSE Bulukumba Chatbot 🤖

Aplikasi chatbot interaktif untuk membantu penyedia barang/jasa memahami proses pengadaan di Layanan Pengadaan Secara Elektronik (LPSE) Kabupaten Bulukumba.

## 🌟 Fitur Utama

- 💬 **Chat Interaktif** - Tanya jawab seputar pengadaan barang/jasa
- 🔍 **Smart Search** - Pencarian cerdas dari knowledge base LPSE
- 📱 **Mobile First** - Aplikasi Flutter yang responsif
- 🔐 **Secure** - Enkripsi data dan autentikasi JWT
- 📊 **Real-time** - Response cepat dengan caching
- 📚 **Comprehensive** - Knowledge base mencakup regulasi terbaru (Perpres 46/2025)

## 🏗️ Arsitektur

```
┌─────────────────────────┐
│   Flutter Mobile App    │ (Android & iOS)
└────────────┬────────────┘
             │ REST API
┌────────────▼────────────┐
│  Node.js/Express API    │
│  - Chat Handler         │
│  - KB Search            │
│  - Authentication       │
└────────────┬────────────┘
             │
    ┌────────┼────────┐
    │        │        │
┌───▼──┐ ┌──▼──┐ ┌───▼────┐
│ PostgreSQL  │ Redis │ Milvus │
└────────┘ └──────┘ └────────┘
```

## 📋 Persyaratan

### Backend
- Node.js 18+ LTS
- PostgreSQL 14+
- Redis 7+
- Docker & Docker Compose (optional)

### Frontend
- Flutter SDK 3.x
- Android SDK 21+ atau iOS 11+
- Dart 3.x

## 🚀 Quick Start

### 1. Clone Repository
```bash
git clone https://github.com/yourusername/lpse-bulukumba-chatbot.git
cd lpse-bulukumba-chatbot
```

### 2. Setup Backend

#### Docker (Recommended)
```bash
cd backend
docker-compose up -d

# Run migrations
docker-compose exec backend npm run migrate

# Verify
curl http://localhost:3000/api/health
```

#### Manual Setup
```bash
cd backend

# Install dependencies
npm install

# Setup .env
cp .env.example .env
nano .env  # Edit dengan database credentials Anda

# Run migrations
npm run migrate

# Start server
npm run dev  # Development
# atau
npm start    # Production
```

### 3. Setup Frontend

```bash
cd flutter_app

# Get dependencies
flutter pub get

# Setup .env
cp .env.example .env
nano .env  # Edit dengan API URL backend

# Run app
flutter run

# Build APK (Android)
flutter build apk --release

# Build IPA (iOS)
flutter build ios --release
```

## 📖 Dokumentasi

- **Knowledge Base**: `docs/LPSE_Bulukumba_Knowledge_Base.md`
- **API Reference**: `backend/API.md`
- **Architecture**: `docs/ARCHITECTURE.md`
- **Deployment**: `docs/DEPLOYMENT.md`

## 🔧 Environment Variables

### Backend (.env)
```env
DATABASE_URL=postgresql://user:password@localhost:5432/lpse_chatbot
REDIS_URL=redis://localhost:6379
JWT_SECRET=your_secret_key
CLAUDE_API_KEY=your_claude_key_optional
PORT=3000
NODE_ENV=development
```

### Frontend (.env)
```env
API_BASE_URL=http://localhost:3000/api
APP_NAME=LPSE Bulukumba Chatbot
DEBUG_MODE=true
```

## 📁 Struktur Folder

```
lpse-bulukumba-chatbot/
├── backend/
│   ├── src/
│   │   ├── index.js
│   │   ├── config/
│   │   ├── routes/
│   │   ├── controllers/
│   │   ├── services/
│   │   ├── models/
│   │   └── middleware/
│   ├── database/
│   │   ├── schema.sql
│   │   └── migrations/
│   ├── docker-compose.yml
│   ├── Dockerfile
│   ├── package.json
│   └── .env.example
│
├── flutter_app/
│   ├── lib/
│   │   ├── main.dart
│   │   ├── screens/
│   │   ├── widgets/
│   │   ├── providers/
│   │   ├── services/
│   │   ├── models/
│   │   └── utils/
│   ├── pubspec.yaml
│   └── .env.example
│
├── docs/
│   ├── LPSE_Bulukumba_Knowledge_Base.md
│   ├── ARCHITECTURE.md
│   ├── API.md
│   └── DEPLOYMENT.md
│
└── README.md
```

## 🧪 Testing

### Backend
```bash
cd backend
npm test
npm run test:coverage
```

### Frontend
```bash
cd flutter_app
flutter test
```

## 🚢 Deployment

### Docker Compose (Production)
```bash
docker-compose -f docker-compose.prod.yml up -d
```

### Manual VPS Deployment
Lihat `docs/DEPLOYMENT.md` untuk panduan lengkap.

## 📊 API Endpoints

### Health Check
```bash
GET /api/health
```

### Authentication
```bash
POST /api/auth/register
POST /api/auth/verify
POST /api/auth/logout
```

### Chat
```bash
POST /api/chat/message
GET /api/chat/history/:sessionId
```

### Procurement Info
```bash
GET /api/procurement/methods
GET /api/procurement/faq
GET /api/procurement/timeline
```

Lihat `backend/API.md` untuk detail lengkap.

## 🤝 Contributing

1. Fork repository
2. Buat feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📝 License

MIT License - Gratis untuk penggunaan non-komersial

## 👥 Tim

- **Project Manager**: Dinas BPBJ Kabupaten Bulukumba
- **Developer**: [Nama Anda]
- **QA**: [Tim QA]

## 📞 Kontak & Support

- **Email**: [email support]
- **WhatsApp**: [nomor support]
- **Issues**: https://github.com/yourusername/lpse-bulukumba-chatbot/issues

## 📅 Roadmap

- [x] Fase 1: Setup infrastructure
- [x] Fase 2: Backend core development
- [x] Fase 3: Frontend development
- [ ] Fase 4: Integration testing
- [ ] Fase 5: Production deployment
- [ ] Fase 6: Monitoring & optimization
- [ ] Fitur: Integration dengan API LPSE real
- [ ] Fitur: Voice chat support
- [ ] Fitur: Multi-language support

## 🙏 Ucapan Terima Kasih

Terima kasih kepada:
- LKPP (Lembaga Kebijakan Pengadaan Barang/Jasa)
- Pemerintah Kabupaten Bulukumba
- Semua kontributor

---

**Made with ❤️ for Kabupaten Bulukumba**

Last Updated: Juli 2026
