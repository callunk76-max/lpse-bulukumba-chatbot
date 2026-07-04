# Backend - LPSE Chatbot API

Express.js API server untuk chatbot LPSE Bulukumba.

## Setup

1. Install dependencies:
```bash
npm install
```

2. Setup environment:
```bash
cp .env.example .env
# Edit .env dengan database credentials Anda
```

3. Run migrations:
```bash
npm run migrate
```

4. Start server:
```bash
npm run dev     # Development dengan nodemon
npm start       # Production
```

## API Endpoints

- `POST /api/auth/register` - Register user
- `POST /api/chat/message` - Send chat message
- `GET /api/procurement/faq` - Get FAQ

Lihat dokumentasi lengkap di `/docs`.
