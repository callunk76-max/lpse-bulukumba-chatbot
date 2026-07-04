# 📤 Panduan Push ke Repository Git

Panduan langkah demi langkah untuk push semua file ke repository GitHub/GitLab Anda.

---

## 🔧 Persiapan Awal

### 1. Setup Git (jika belum pernah)
```bash
git config --global user.name "Nama Anda"
git config --global user.email "email@example.com"
```

### 2. Setup SSH Key (Recommended - Aman & Otomatis)

**Generate SSH Key:**
```bash
ssh-keygen -t ed25519 -C "email@example.com"
# Atau gunakan RSA jika ed25519 tidak support:
# ssh-keygen -t rsa -b 4096 -C "email@example.com"
```

**Add ke SSH Agent:**
```bash
# Linux/Mac
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519

# Windows PowerShell
# Pastikan Git Bash sudah installed
```

**Copy public key dan add ke GitHub/GitLab:**
```bash
# Copy ke clipboard
cat ~/.ssh/id_ed25519.pub  # Linux/Mac
# atau
type $env:USERPROFILE\.ssh\id_ed25519.pub  # Windows PowerShell
```

Kemudian:
- **GitHub**: Settings → SSH and GPG keys → New SSH key
- **GitLab**: Settings → SSH Keys

---

## 📂 Struktur Repository

Pastikan struktur folder di VPS Anda adalah:

```
~/lpse-bulukumba-chatbot/
├── backend/
│   ├── src/
│   ├── database/
│   ├── package.json
│   ├── .env.example
│   └── docker-compose.yml
├── flutter_app/
│   ├── lib/
│   ├── pubspec.yaml
│   ├── .env.example
│   └── android/ios/...
├── docs/
│   ├── LPSE_Bulukumba_Knowledge_Base.md
│   ├── ARCHITECTURE.md
│   ├── IMPLEMENTATION.md
│   └── DEPLOYMENT.md
├── .github/
│   └── workflows/  (CI/CD config)
├── .gitignore
├── README.md
└── LICENSE
```

---

## 🚀 Langkah-Langkah Push

### Opsi A: Repository Sudah Ada di GitHub/GitLab

#### 1. Clone Repository
```bash
# SSH (recommended)
git clone git@github.com:yourusername/lpse-bulukumba-chatbot.git

# Atau HTTPS
git clone https://github.com/yourusername/lpse-bulukumba-chatbot.git

cd lpse-bulukumba-chatbot
```

#### 2. Copy File-File dari Output
Dari `/mnt/user-data/outputs/`, copy:
- `README.md`
- `LPSE_Bulukumba_Knowledge_Base.md`
- `IMPLEMENTASI_CHATBOT_TEKNIS.md`
- `.gitignore`

```bash
# Dari directory `/mnt/user-data/outputs/`
cp README.md ~/lpse-bulukumba-chatbot/
cp LPSE_Bulukumba_Knowledge_Base.md ~/lpse-bulukumba-chatbot/docs/
cp IMPLEMENTASI_CHATBOT_TEKNIS.md ~/lpse-bulukumba-chatbot/docs/
cp .gitignore ~/lpse-bulukumba-chatbot/
```

#### 3. Stage Files
```bash
cd ~/lpse-bulukumba-chatbot

# Tambah semua file
git add .

# Atau tambah file spesifik
git add README.md docs/ .gitignore
```

#### 4. Commit
```bash
git commit -m "docs: Add knowledge base dan dokumentasi teknis

- Knowledge base LPSE Bulukumba lengkap
- Implementasi chatbot teknis dengan Flask API
- Architecture documentation
- Panduan deployment
"
```

#### 5. Push ke Repository
```bash
# Push ke branch main/master
git push origin main

# Atau develop jika ada
git push origin develop

# Check status
git status
```

#### 6. Verify
Buka https://github.com/yourusername/lpse-bulukumba-chatbot dan cek apakah file sudah terupload.

---

### Opsi B: Repository Belum Ada, Buat Baru

#### 1. Buat Repository di GitHub/GitLab
- Go to https://github.com/new
- Nama: `lpse-bulukumba-chatbot`
- Description: "Chatbot interaktif untuk LPSE Kabupaten Bulukumba"
- Visibility: Public
- **Jangan** initialize dengan README (nanti akan conflict)

#### 2. Inisialisasi Repository Lokal
```bash
mkdir -p ~/lpse-bulukumba-chatbot
cd ~/lpse-bulukumba-chatbot

# Initialize git
git init

# Tambah files
mkdir -p backend/src backend/database
mkdir -p flutter_app/{lib,assets}
mkdir -p docs
mkdir -p .github/workflows

# Copy file dari outputs
cp /mnt/user-data/outputs/README.md .
cp /mnt/user-data/outputs/LPSE_Bulukumba_Knowledge_Base.md docs/
cp /mnt/user-data/outputs/IMPLEMENTASI_CHATBOT_TEKNIS.md docs/
cp /mnt/user-data/outputs/.gitignore .

# Create placeholder files
touch backend/.env.example
touch flutter_app/.env.example
echo "# Backend Setup" > backend/README.md
echo "# Flutter App Setup" > flutter_app/README.md
```

#### 3. Stage & Commit
```bash
git add .
git commit -m "Initial commit: Project structure dan dokumentasi"
```

#### 4. Add Remote Repository
```bash
git remote add origin git@github.com:yourusername/lpse-bulukumba-chatbot.git

# Verify
git remote -v
```

#### 5. Push
```bash
# Jika branch default adalah 'master'
git branch -M main

# Push
git push -u origin main
```

---

## 🔄 Update Repository (Selanjutnya)

Setiap kali ada perubahan:

```bash
cd ~/lpse-bulukumba-chatbot

# Check status
git status

# Tambah changes
git add .

# Commit dengan message deskriptif
git commit -m "feat: Add chat endpoint API"

# Push
git push origin main
```

---

## 📝 Commit Message Best Practices

Format:
```
<type>(<scope>): <subject>

<body>

<footer>
```

**Type:**
- `feat`: Feature baru
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Code style (spacing, semicolon, etc)
- `refactor`: Code refactoring
- `test`: Testing
- `chore`: Build process, dependencies

**Contoh:**
```bash
git commit -m "feat(backend): Add chat message API endpoint

- Create POST /api/chat/message endpoint
- Integrate with knowledge base search
- Add request validation with Zod

Closes #123"
```

---

## 🌳 Git Branching Strategy

Disarankan gunakan Git Flow:

```
main (production)
  ├── release/v1.0.0
  │
develop (staging)
  ├── feature/chat-enhancement
  ├── feature/mobile-optimization
  └── bugfix/socket-connection
```

**Setup:**
```bash
# Create develop branch
git checkout -b develop
git push -u origin develop

# Create feature branch
git checkout -b feature/chat-enhancement develop

# Work & commit
git add .
git commit -m "feat: Improve chat UX"

# Push feature branch
git push -u origin feature/chat-enhancement

# Create Pull Request di GitHub/GitLab
# After review & merge, delete branch
```

---

## 🔐 Security Notes

### ⚠️ JANGAN Push:
- `.env` files dengan credentials asli
- API keys, passwords, secrets
- Database dump files
- Private certificates

### ✅ HARUS Upload:
- `.env.example` (template tanpa values)
- Documentation
- Code & tests
- Configuration templates

### Setup `.env.example`
```bash
# backend/.env.example
DATABASE_URL=postgresql://user:password@localhost:5432/lpse_chatbot
REDIS_URL=redis://localhost:6379
JWT_SECRET=your_secret_key_here
CLAUDE_API_KEY=your_api_key_here
PORT=3000
NODE_ENV=development
```

---

## 🆘 Troubleshooting

### Error: "Permission denied (publickey)"

**Solution:**
```bash
# Check SSH key
ssh -T git@github.com

# If not working, regenerate key
ssh-keygen -t ed25519 -C "email@example.com"
ssh-add ~/.ssh/id_ed25519

# Test again
ssh -T git@github.com
```

### Error: "fatal: 'origin' does not appear to be a 'git' repository"

**Solution:**
```bash
# Check remote
git remote -v

# If empty, add remote
git remote add origin git@github.com:yourusername/lpse-bulukumba-chatbot.git

# Verify
git remote -v
```

### Error: "Updates were rejected because the tip of your current branch is behind"

**Solution:**
```bash
# Pull latest changes
git pull origin main --rebase

# Then push
git push origin main
```

### Error: "CONFLICT: .gitignore"

**Solution:**
```bash
# Resolve conflict
git status  # see which files have conflicts
nano .gitignore  # edit and resolve

# Mark as resolved
git add .gitignore
git commit -m "resolve: merge conflict in .gitignore"
git push origin main
```

---

## 📊 Monitoring Push Status

### Check Push Log
```bash
# See commit history
git log --oneline -10

# See remote branches
git branch -a

# See remote status
git status
```

### GitHub/GitLab Actions
Setup CI/CD untuk automatic testing:

**File: `.github/workflows/test.yml`**
```yaml
name: Run Tests

on: [push, pull_request]

jobs:
  backend-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-node@v2
        with:
          node-version: '18'
      - run: cd backend && npm install && npm test
  
  flutter-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: subosito/flutter-action@v1
      - run: cd flutter_app && flutter test
```

---

## ✅ Checklist Sebelum Push

- [ ] Semua file sudah di-copy ke directory yang tepat
- [ ] `.env` files tidak diinclude (gunakan `.env.example`)
- [ ] `node_modules/`, `build/`, `.dart_tool/` di-gitignore
- [ ] README.md sudah lengkap dan informatif
- [ ] Commit message descriptive dan mengikuti convention
- [ ] Remote repository sudah dikonfigurasi dengan benar
- [ ] SSH key sudah setup atau HTTPS credentials siap
- [ ] Latest version di-push ke main/master branch

---

## 🎯 Next Steps

1. ✅ Push documentation & knowledge base ke GitHub
2. ⬜ Setup Backend project structure
3. ⬜ Setup Flutter app project structure
4. ⬜ Setup CI/CD pipeline
5. ⬜ Deploy ke VPS
6. ⬜ Setup monitoring & logging

---

## 📚 Resources

- Git Documentation: https://git-scm.com/doc
- GitHub Docs: https://docs.github.com
- GitLab Docs: https://docs.gitlab.com
- Git Flow: https://nvie.com/posts/a-successful-git-branching-model/
- Conventional Commits: https://www.conventionalcommits.org/

---

**Selamat! Repository Anda sudah siap untuk development! 🚀**

Jika ada pertanyaan atau ada masalah, silakan buka issue di repository atau hubungi tim development.

---
