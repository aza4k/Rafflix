# 🎬 Rafflix (@RafflixBot)

Rafflix is a professional Telegram Bot for running prize raffles powered by Telegram Stars. It features a premium, dark-themed Telegram Web App (TWA) frontend for an immersive user experience.

## ✨ Features

- **Telegram Stars Integration**: Seamless ticket purchases using the new Telegram currency.
- **Dynamic Raffles**: Progressive prize draws that trigger automatically when targets are met.
- **Weighted Drawing Algorithm**: Fair and transparent winner selection.
- **Referral System**: Integrated bonus rewards for inviting friends.
- **User Streaks**: Bonus tickets for participating in multiple consecutive raffles.
- **Admin Tools**: Built-in wizard for creating and managing raffles.
- **Live Announcements**: Automatic channel updates for new raffles and winners.

## 🛠️ Tech Stack

- **Bot**: Python 3.11+ · aiogram 3.x
- **API**: FastAPI (Async)
- **Database**: PostgreSQL + SQLAlchemy 2.0 (Async) + Alembic
- **Worker**: Redis + Celery
- **Frontend**: React 18 + Vite + TailwindCSS

## 🚀 Quick Start

### 1. Requirements
- Docker and Docker Compose
- A Telegram Bot Token from [@BotFather](https://t.me/BotFather)

### 2. Configure Environment
Copy `.env.example` to `.env` and fill in your details:
```bash
cp .env.example .env
```

### 3. Build & Run
```bash
docker-compose up --build
```

### 4. Admin Access
Add your Telegram user ID to the `ADMIN_IDS` in `.env` to access the `/admin` commands.

## 📁 Project Structure

- `/bot`: Telegram bot handlers and logic.
- `/api`: FastAPI backend and authentication.
- `/core`: Shared models, database logic, and business rules.
- `/worker`: Background tasks for draws and streaks.
- `/webapp`: React frontend for the Telegram Web App.

---
Built by Antigravity AI.
