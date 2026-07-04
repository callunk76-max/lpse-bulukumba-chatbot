#!/bin/bash

# ============================================
# LPSE Bulukumba Chatbot - Setup & Push Script
# ============================================
# Script ini membantu setup project structure 
# dan push ke GitHub/GitLab secara otomatis
# ============================================

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}"
echo "╔════════════════════════════════════════════════════════╗"
echo "║   LPSE Bulukumba Chatbot - Setup & Push ke GitHub      ║"
echo "╚════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# ============================================
# 1. GATHERING INFORMATION
# ============================================

echo -e "${YELLOW}📋 Step 1: Gathering Information${NC}"
echo ""

# Get Git username
read -p "GitHub/GitLab username: " GIT_USERNAME

# Get repository name (default: lpse-bulukumba-chatbot)
read -p "Repository name (default: lpse-bulukumba-chatbot): " REPO_NAME
REPO_NAME=${REPO_NAME:-lpse-bulukumba-chatbot}

# Get Git host (default: github.com)
read -p "Git host - github.com atau gitlab.com? (default: github.com): " GIT_HOST
GIT_HOST=${GIT_HOST:-github.com}

# Get branch name
read -p "Main branch (default: main): " BRANCH_NAME
BRANCH_NAME=${BRANCH_NAME:-main}

# Construct repository URL
REPO_URL="git@${GIT_HOST}:${GIT_USERNAME}/${REPO_NAME}.git"

echo ""
echo -e "${GREEN}✓ Configuration:${NC}"
echo "  Repository URL: ${REPO_URL}"
echo "  Branch: ${BRANCH_NAME}"
echo ""

# ============================================
# 2. SETUP PROJECT STRUCTURE
# ============================================

echo -e "${YELLOW}📂 Step 2: Setting Up Project Structure${NC}"
echo ""

# Go to home directory or specified path
read -p "Project directory path (default: ~/${REPO_NAME}): " PROJECT_PATH
PROJECT_PATH=${PROJECT_PATH:-~/${REPO_NAME}}

# Create directories
mkdir -p "${PROJECT_PATH}"
cd "${PROJECT_PATH}"

echo "Creating folder structure..."

mkdir -p backend/{src,database,config,middleware,routes,controllers,services,models,utils}
mkdir -p flutter_app/{lib/{screens,widgets,providers,services,models,utils},assets/{images,fonts}}
mkdir -p docs
mkdir -p .github/workflows
mkdir -p logs

echo -e "${GREEN}✓ Folder structure created${NC}"
echo ""

# ============================================
# 3. COPY DOCUMENTATION FILES
# ============================================

echo -e "${YELLOW}📄 Step 3: Copying Documentation Files${NC}"
echo ""

# Copy from /mnt/user-data/outputs/ if available
if [ -d "/mnt/user-data/outputs/" ]; then
    echo "Copying from /mnt/user-data/outputs/..."
    
    cp /mnt/user-data/outputs/README.md . 2>/dev/null || echo "  ⚠ README.md not found"
    cp /mnt/user-data/outputs/LPSE_Bulukumba_Knowledge_Base.md docs/ 2>/dev/null || echo "  ⚠ Knowledge Base not found"
    cp /mnt/user-data/outputs/IMPLEMENTASI_CHATBOT_TEKNIS.md docs/ 2>/dev/null || echo "  ⚠ Implementation docs not found"
    cp /mnt/user-data/outputs/.gitignore . 2>/dev/null || echo "  ⚠ .gitignore not found"
    cp /mnt/user-data/outputs/PUSH_TO_REPO_GUIDE.md docs/ 2>/dev/null || echo "  ⚠ Push guide not found"
    
    echo -e "${GREEN}✓ Documentation files copied${NC}"
else
    echo -e "${YELLOW}⚠ /mnt/user-data/outputs/ not found, creating minimal files...${NC}"
    
    # Create minimal README
    cat > README.md << 'EOF'
# LPSE Bulukumba Chatbot

Aplikasi chatbot interaktif untuk membantu penyedia barang/jasa di LPSE Kabupaten Bulukumba.

## Dokumentasi

Lihat folder `docs/` untuk dokumentasi lengkap.

## Quick Start

Lihat `backend/README.md` dan `flutter_app/README.md` untuk panduan setup masing-masing.
EOF
fi

echo ""

# ============================================
# 4. CREATE .ENV.EXAMPLE FILES
# ============================================

echo -e "${YELLOW}⚙️  Step 4: Creating .env.example Files${NC}"
echo ""

# Backend .env.example
cat > backend/.env.example << 'EOF'
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/lpse_chatbot
DB_HOST=localhost
DB_PORT=5432
DB_USER=lpse_user
DB_PASSWORD=your_secure_password

# Redis
REDIS_URL=redis://localhost:6379

# Server
NODE_ENV=development
PORT=3000

# JWT
JWT_SECRET=your_jwt_secret_key_here
JWT_EXPIRES_IN=86400

# Claude API (optional)
CLAUDE_API_KEY=your_claude_api_key

# CORS
CORS_ORIGIN=http://localhost:8080,https://yourdomain.com
EOF

# Flutter .env.example
cat > flutter_app/.env.example << 'EOF'
# API Configuration
API_BASE_URL=http://localhost:3000/api
API_TIMEOUT_SECONDS=30

# App Configuration
APP_NAME=LPSE Bulukumba Chatbot
APP_VERSION=1.0.0
DEBUG_MODE=true

# Feature Flags
ENABLE_OFFLINE_MODE=true
ENABLE_VOICE_CHAT=false
EOF

echo -e "${GREEN}✓ .env.example files created${NC}"
echo ""

# ============================================
# 5. CREATE PLACEHOLDER README FILES
# ============================================

echo -e "${YELLOW}📝 Step 5: Creating README Files${NC}"
echo ""

cat > backend/README.md << 'EOF'
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
EOF

cat > flutter_app/README.md << 'EOF'
# Frontend - LPSE Chatbot Mobile App

Flutter mobile application untuk chatbot LPSE Bulukumba.

## Setup

1. Get dependencies:
```bash
flutter pub get
```

2. Setup environment:
```bash
cp .env.example .env
# Edit .env dengan API URL backend Anda
```

3. Run app:
```bash
flutter run
```

4. Build APK:
```bash
flutter build apk --release
```

## Requirements

- Flutter SDK 3.x
- Dart 3.x
- Android SDK 21+ atau iOS 11+

Lihat dokumentasi lengkap di `/docs`.
EOF

echo -e "${GREEN}✓ README files created${NC}"
echo ""

# ============================================
# 6. INITIALIZE GIT REPOSITORY
# ============================================

echo -e "${YELLOW}🔧 Step 6: Initializing Git Repository${NC}"
echo ""

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo -e "${RED}❌ Git is not installed. Please install Git first.${NC}"
    exit 1
fi

# Initialize git if not already done
if [ ! -d .git ]; then
    git init
    echo -e "${GREEN}✓ Git repository initialized${NC}"
else
    echo -e "${YELLOW}⚠ Git repository already exists${NC}"
fi

# Configure git user if not already set
if [ -z "$(git config user.name)" ]; then
    read -p "Git user name (your name): " GIT_USER_NAME
    git config user.name "${GIT_USER_NAME}"
fi

if [ -z "$(git config user.email)" ]; then
    read -p "Git email address: " GIT_USER_EMAIL
    git config user.email "${GIT_USER_EMAIL}"
fi

echo ""

# ============================================
# 7. SETUP GIT REMOTE
# ============================================

echo -e "${YELLOW}🌐 Step 7: Setting Up Git Remote${NC}"
echo ""

# Check if remote already exists
if git remote get-url origin &> /dev/null; then
    echo -e "${YELLOW}⚠ Remote 'origin' already exists${NC}"
    CURRENT_URL=$(git remote get-url origin)
    echo "Current URL: ${CURRENT_URL}"
    
    read -p "Replace with new URL? (y/n, default: n): " REPLACE_REMOTE
    REPLACE_REMOTE=${REPLACE_REMOTE:-n}
    
    if [ "${REPLACE_REMOTE}" = "y" ]; then
        git remote remove origin
        git remote add origin "${REPO_URL}"
        echo -e "${GREEN}✓ Remote URL updated${NC}"
    fi
else
    git remote add origin "${REPO_URL}"
    echo -e "${GREEN}✓ Remote added: ${REPO_URL}${NC}"
fi

echo ""

# ============================================
# 8. STAGING & COMMITTING
# ============================================

echo -e "${YELLOW}💾 Step 8: Staging & Committing${NC}"
echo ""

# Add all files
git add .
echo "✓ Files staged"

# Create initial commit
git commit -m "Initial commit: Project structure and documentation

- Backend setup with Express.js structure
- Flutter app structure
- Documentation and knowledge base
- API endpoints planning
- Deployment guides" 2>/dev/null || echo "⚠ No changes to commit"

echo -e "${GREEN}✓ Commit created${NC}"
echo ""

# ============================================
# 9. BRANCH SETUP
# ============================================

echo -e "${YELLOW}🌳 Step 9: Setting Up Branch${NC}"
echo ""

# Rename branch if not main
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
if [ "${CURRENT_BRANCH}" != "${BRANCH_NAME}" ]; then
    git branch -M "${BRANCH_NAME}"
    echo -e "${GREEN}✓ Branch renamed to: ${BRANCH_NAME}${NC}"
else
    echo "✓ Using branch: ${BRANCH_NAME}"
fi

echo ""

# ============================================
# 10. PUSH TO REPOSITORY
# ============================================

echo -e "${YELLOW}🚀 Step 10: Pushing to Repository${NC}"
echo ""

# Check if repository exists on remote
echo "Checking remote repository..."
read -p "Push to remote now? (y/n, default: y): " DO_PUSH
DO_PUSH=${DO_PUSH:-y}

if [ "${DO_PUSH}" = "y" ]; then
    echo "Pushing to ${REPO_URL}..."
    
    # Try to push
    if git push -u origin "${BRANCH_NAME}" 2>&1; then
        echo -e "${GREEN}✓ Successfully pushed to ${REPO_URL}${NC}"
    else
        echo -e "${RED}❌ Push failed. Possible reasons:${NC}"
        echo "  1. Remote repository doesn't exist"
        echo "  2. SSH key not configured"
        echo "  3. Permissions issue"
        echo ""
        echo "Solution:"
        echo "  1. Create repository on ${GIT_HOST}"
        echo "  2. Setup SSH key: ssh-keygen -t ed25519"
        echo "  3. Try again: git push -u origin ${BRANCH_NAME}"
        exit 1
    fi
else
    echo -e "${YELLOW}⚠ Skipping push. You can push manually later:${NC}"
    echo "  git push -u origin ${BRANCH_NAME}"
fi

echo ""

# ============================================
# 11. VERIFICATION
# ============================================

echo -e "${YELLOW}✅ Step 11: Verification${NC}"
echo ""

echo "Repository status:"
git status
echo ""

echo "Remote configuration:"
git remote -v
echo ""

echo "Commit log:"
git log --oneline -3
echo ""

# ============================================
# COMPLETION MESSAGE
# ============================================

echo -e "${GREEN}"
echo "╔════════════════════════════════════════════════════════╗"
echo "║          ✓ Setup Complete & Ready to Go!              ║"
echo "╚════════════════════════════════════════════════════════╝"
echo -e "${NC}"

echo ""
echo -e "${BLUE}📍 Project Location: ${PROJECT_PATH}${NC}"
echo -e "${BLUE}📱 Repository URL: ${REPO_URL}${NC}"
echo -e "${BLUE}🌳 Branch: ${BRANCH_NAME}${NC}"
echo ""

echo -e "${YELLOW}Next Steps:${NC}"
echo ""
echo "1️⃣  Start Backend Development:"
echo "   cd ${PROJECT_PATH}/backend"
echo "   npm install"
echo "   cp .env.example .env"
echo "   npm run dev"
echo ""
echo "2️⃣  Start Flutter Development:"
echo "   cd ${PROJECT_PATH}/flutter_app"
echo "   flutter pub get"
echo "   flutter run"
echo ""
echo "3️⃣  Make Changes & Push:"
echo "   git add ."
echo "   git commit -m 'Your message'"
echo "   git push origin ${BRANCH_NAME}"
echo ""
echo "4️⃣  View on Web:"
echo "   https://${GIT_HOST}/${GIT_USERNAME}/${REPO_NAME}"
echo ""

echo -e "${GREEN}Happy Coding! 🚀${NC}"
echo ""
