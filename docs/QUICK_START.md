# ⚡ QUICK START - Push ke GitHub dalam 5 Langkah

**Waktu:** ~10 menit  
**Prasyarat:** GitHub account, SSH key (atau HTTPS), Git installed

---

## 🎯 STEP 1: Siapkan Repository di GitHub

1. Go to https://github.com/new
2. Nama: `lpse-bulukumba-chatbot`
3. Visibility: **Public**
4. **JANGAN** initialize dengan README
5. Click **Create Repository**
6. Copy URL: `git@github.com:yourusername/lpse-bulukumba-chatbot.git`

---

## 📂 STEP 2: Setup Folder Lokal

```bash
# Create & go to directory
mkdir -p ~/lpse-bulukumba-chatbot
cd ~/lpse-bulukumba-chatbot

# Create folder structure
mkdir -p backend/{src,database,config,middleware,routes,controllers,services}
mkdir -p flutter_app/{lib/{screens,widgets,providers,services,models},assets}
mkdir -p docs
mkdir -p .github/workflows
```

---

## 📋 STEP 3: Copy Files dari /outputs

```bash
# Copy dokumentasi
cp /mnt/user-data/outputs/README.md .
cp /mnt/user-data/outputs/.gitignore .
cp /mnt/user-data/outputs/LPSE_Bulukumba_Knowledge_Base.md docs/
cp /mnt/user-data/outputs/IMPLEMENTASI_CHATBOT_TEKNIS.md docs/
cp /mnt/user-data/outputs/PUSH_TO_REPO_GUIDE.md docs/

# Create .env template
cat > backend/.env.example << 'EOF'
DATABASE_URL=postgresql://user:password@localhost:5432/lpse
REDIS_URL=redis://localhost:6379
JWT_SECRET=your_secret_key
PORT=3000
NODE_ENV=development
EOF

cat > flutter_app/.env.example << 'EOF'
API_BASE_URL=http://localhost:3000/api
APP_VERSION=1.0.0
DEBUG_MODE=true
EOF
```

---

## 🔧 STEP 4: Init Git & Commit

```bash
# Initialize git
git init

# Configure user
git config user.name "Your Name"
git config user.email "your@email.com"

# Add all files
git add .

# Commit
git commit -m "Initial commit: Project structure & documentation

- Knowledge base LPSE Bulukumba
- Backend & Frontend structure
- Technical documentation
- Setup guides"
```

---

## 🚀 STEP 5: Push ke GitHub

```bash
# Set main branch
git branch -M main

# Add remote (ganti yourusername dengan username GitHub Anda)
git remote add origin git@github.com:yourusername/lpse-bulukumba-chatbot.git

# Push
git push -u origin main
```

✅ **Done!** Repository Anda sudah live di GitHub!

---

## ✨ Verify

```bash
# Check status
git status
# Should show: "On branch main, nothing to commit"

# Check remote
git remote -v
# Should show: origin  git@github.com:yourusername/lpse-bulukumba-chatbot.git

# Check logs
git log --oneline
# Should show your initial commit
```

Buka https://github.com/yourusername/lpse-bulukumba-chatbot dan lihat files Anda!

---

## 🆘 Troubleshooting

### Error: "Permission denied (publickey)"
```bash
# Setup SSH key
ssh-keygen -t ed25519
ssh-add ~/.ssh/id_ed25519

# Test connection
ssh -T git@github.com
```

### Error: "Repository not found"
- Pastikan repository sudah dibuat di GitHub
- Pastikan URL username benar

### Error: "fatal: bad credentials"
- Gunakan SSH key (lebih aman) daripada HTTPS
- Atau setup GitHub personal access token untuk HTTPS

### Script gagal?
```bash
# Coba manual step by step di atas
# Atau gunakan HTTPS:
git remote add origin https://github.com/yourusername/lpse-bulukumba-chatbot.git
```

---

## 📚 Next: Start Development

### Backend
```bash
cd backend
npm install
cp .env.example .env
npm run dev
```

### Flutter
```bash
cd flutter_app
flutter pub get
flutter run
```

Lihat **README.md** untuk dokumentasi lengkap!

---

## 🎓 Useful Commands untuk Kedepannya

```bash
# Pull latest changes
git pull origin main

# Create feature branch
git checkout -b feature/your-feature

# Add & commit
git add .
git commit -m "feat: your message"

# Push
git push origin feature/your-feature

# View history
git log --oneline -10

# Check status
git status
```

---

**Done! Happy Coding! 🚀**

Untuk help lebih lanjut: `cat PUSH_TO_REPO_GUIDE.md`

