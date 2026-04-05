# ChatApp - Full-Feature Chat Application

A modern chat application with async message processing, batch compression, and modular frontend components.

## 📁 Project Structure

```
chat-app/
├── backend/                    # Python FastAPI backend
│   ├── app/
│   │   ├── main.py           # FastAPI entry point
│   │   ├── config.py         # Environment configuration
│   │   ├── dependencies.py  # Shared dependencies (auth, db)
│   │   ├── models/          # SQLAlchemy data models
│   │   │   ├── user.py      # User model
│   │   │   ├── message.py   # Message model
│   │   │   ├── group.py     # Group & GroupMember models
│   │   │   ├── friend.py    # Friend relationship
│   │   │   └── reaction.py  # Emoji reactions
│   │   ├── routes/          # API endpoints
│   │   │   ├── auth.py      # Register, login, logout
│   │   │   ├── user.py      # Profile, avatar, block
│   │   │   ├── chat.py      # Send, delete messages
│   │   │   ├── group.py     # Create groups, admin
│   │   │   └── system.py    # Batch triggers, monitoring
│   │   ├── services/        # Business logic layer
│   │   ├── system/          # Async batch processing
│   │   ├── utils/           # Helper tools
│   │   └── sockets/         # WebSocket (optional)
│   └── requirements.txt     # Python packages
│
├── frontend/                 # React/Vite frontend
│   ├── src/
│   │   ├── pages/          # Auth, Chat, Group pages
│   │   ├── components/      # ChatBox, MessageItem, Avatar, etc.
│   │   ├── services/       # API client, WebSocket
│   │   └── store/          # Zustand state management
│   └── package.json
│
├── storage/                 # Local staging storage
├── data-pipeline/          # Processing layer
├── scripts/                # Dev tools
├── .env                    # Secrets (never commit)
├── docker-compose.yml      # Optional Docker setup
└── README.md
```

## 🚀 Features

- **Auth**: Register, login, JWT tokens, user profile, avatar, block user
- **Private Chat**: Send, delete, emoji reaction, add friends
- **Group Chat**: Admin, co-admin, group info, nickname system
- **Batch Processing**: Async queue, hourly compression (zstd), local storage
- **UI**: Three.js background, Avatar click → profile modal

## 🛠️ Tech Stack

- **Backend**: FastAPI, SQLAlchemy (async), PostgreSQL, Redis
- **Frontend**: React 18, Vite, Zustand, Framer Motion, Three.js
- **Storage**: Local file system, GitHub API backup, zstd compression

## 📦 Installation

```bash
# Install backend
cd backend
pip install -r requirements.txt

# Install frontend
cd frontend
npm install

# Start development
cd ..
./scripts/start.sh
```

## ⚙️ Configuration

Copy `.env.example` to `.env` and configure:

```env
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/chatapp
REDIS_URL=redis://localhost:6379/0
JWT_SECRET=your-secret-key
```

## 🔐 Security Best Practices

1. **Never commit secrets** - Use `.env` and add to `.gitignore`
2. **Hash passwords** - Using bcrypt via `passlib`
3. **JWT tokens** - Short expiration, HTTPS only in production
4. **Private GitHub repo** - For storage backup

## 📝 License

MIT