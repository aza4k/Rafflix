# 🚀 Rafflix: Railway Serverga Joylash Qo'llanmasi

Ushbu qo'llanma orqali Rafflix loyihasini GitHub orqali Railway serveriga qanday joylashni bosqichma-bosqich o'rganasiz.

## 1-bosqich: GitHub'ga yuklash

1. GitHub'da yangi repozitoriya oching: `https://github.com/aza4k/Rafflix`
2. Loyihangizni GitHub'ga yuklang:
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/aza4k/Rafflix.git
   git push -u origin main
   ```

## 2-bosqich: Railway'da loyiha yaratish

1. [Railway.app](https://railway.app/) saytiga kiring.
2. **New Project** -> **Deploy from GitHub repo** tanlang.
3. `Rafflix` repozitoriyasini tanlang.

### 2.1. Servislarni "Split" qilish (bo'lish)
Railway avvomat ravishda bitta repo uchun bitta servis yaratadi. Bizga esa 4 ta kerak.
1. Dashboardda tepada **+ (Add Service)** tugmasini bosing.
2. Yana **GitHub Repo**ni tanlang va o'sha `Rafflix` reponi tanlang.
3. Buni jami 4 marta takrorlang (API, Bot, Worker, Beat uchun).

Endi har birining **Settings** bo'limiga kirib, nomini va buyrug'ini (Start Command) o'zgartiring:

Railway loyihangizga quyidagi xizmatlarni qo'shing:
1. **Add Service** -> **Database** -> **Add PostgreSQL**.
2. **Add Service** -> **Database** -> **Add Redis**.

Railway avtomatik ravishda `DATABASE_URL` va `REDIS_URL` o'zgaruvchilarini yaratadi.

## 4-bosqich: Servislarni sozlash

Rafflix 4 ta asosiy servisdan tashkil topgan. Railway'da har birini alohida xizmat (Service) sifatida qo'shing:

### 1. API Servis (FastAPI)
- **Settings** -> **Public Networking**: Portni `8000` ga sozlang.
- **Service Name**: `api` deb nomlang.
- **Start Command**: `  `

### 2. Bot Servis (Telegram Bot)
- **Service Name**: `bot` deb nomlang.
- **Start Command**: `python -m bot.main`

### 3. Worker Servis (Celery)
- **Service Name**: `worker` deb nomlang.
- **Start Command**: `celery -A worker.celery_app worker --loglevel=info`

### 4. Beat Servis (Celery Beat)
- **Service Name**: `beat` deb nomlang.
- **Start Command**: `celery -A worker.celery_app beat --loglevel=info`

## 5-bosqich: Environment Variables (.env)

Har bir servis uchun (api, bot, worker, beat) **Variables** bo'limiga quyidagilarni kiriting:

| O'zgaruvchi | Qiymat (Railway reference) |
| :--- | :--- |
| `DATABASE_URL` | `${{Postgres.DATABASE_URL}}` |
| `REDIS_URL` | `${{Redis.REDIS_URL}}` |
| `BOT_TOKEN` | BotFather tokeni |
| `BOT_USERNAME` | Bot userneymi |
| `ADMIN_IDS` | Sizning ID |
| `CHANNEL_ID` | Kanal ID |
| `WEBAPP_URL` | `api` servisi bergan URL |

> [!IMPORTANT]
> Railway bergan `DATABASE_URL` odatda `postgresql://` bilan boshlanadi. Bizning kodimiz esa `postgresql+asyncpg://`ni talab qiladi.
> Men kodimizni shunday o'zgartiraman-ki, u avtomatik ravishda `+asyncpg`ni qo'shib oladi.

## 6-bosqich: Web App (Frontend)

Web App'ni Railway'da static site sifatida yoki alohida xizmat qilib joylash mumkin.
1. `webapp` papkasiga kiring.
2. `VITE_API_URL` o'zgaruvchisini API servisi linkiga sozlang.
3. Railway'da yangi xizmat qo'shib, **Root Directory**ni `webapp` qilib sozlang.

---
Muvaffaqiyatli joylashga tildoshmiz! 🚀
Agar savollar bo'lsa, Antigravity AI doim yordamga tayyor.
