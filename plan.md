# 🎬 Rafflix (@RafflixBot) — Full Vibe Coding Prompt

---

## PROJECT OVERVIEW

Build **Rafflix** — a Telegram Bot (`@RafflixBot`) with a **Telegram Web App (TWA)** frontend for running gift raffles powered by **Telegram Stars**. Users buy tickets using Stars, accumulate tickets in a personal Rafflix wallet, and compete to win Telegram Gifts. A referral system rewards users with bonus tickets when friends make real purchases.

**Brand identity:** The name "Rafflix" blends *Raffle* + *-flix* (implying a stream of exciting drops). The vibe is premium, dark, cinematic — like a gift lottery platform you'd actually trust.

---

## TECH STACK

| Layer | Technology |
|---|---|
| Bot framework | Python 3.11+ · aiogram 3.x |
| Web App frontend | React 18 + Vite + TailwindCSS |
| Backend API | FastAPI (async) |
| Database | PostgreSQL 15 + SQLAlchemy 2.0 (async) |
| Migrations | Alembic |
| Cache / Queue | Redis + Celery |
| Telegram Payments | Telegram Stars (XTR) via Invoice API |
| Hosting hint | Single VPS — nginx reverse proxy |

---

## ENVIRONMENT VARIABLES

```env
BOT_TOKEN=                  # @RafflixBot token from @BotFather
WEBHOOK_URL=                # https://yourdomain.com/webhook
WEBAPP_URL=                 # https://yourdomain.com (served frontend)
DATABASE_URL=               # postgresql+asyncpg://...
REDIS_URL=                  # redis://localhost:6379/0
ADMIN_IDS=                  # comma-separated Telegram user IDs
CHANNEL_ID=                 # Telegram channel ID for raffle announcements
BOT_USERNAME=RafflixBot     # used for referral links: t.me/RafflixBot?start=ref_XXX
```

---

## DATABASE SCHEMA

Create all tables with SQLAlchemy ORM (async). Use UUID primary keys everywhere.

### `users`
```
id              UUID PK
telegram_id     BIGINT UNIQUE NOT NULL
username        VARCHAR(64)
full_name       VARCHAR(256)
referred_by     UUID FK → users.id  NULLABLE
ticket_balance  INT DEFAULT 0          -- current spendable tickets
total_earned    INT DEFAULT 0
total_spent     INT DEFAULT 0
streak_count    INT DEFAULT 0          -- consecutive raffles participated
is_banned       BOOL DEFAULT FALSE
created_at      TIMESTAMPTZ DEFAULT now()
updated_at      TIMESTAMPTZ
```

### `raffles`
```
id              UUID PK
title           VARCHAR(256)           -- e.g. "🧸 Teddy Bear Raffle"
gift_name       VARCHAR(256)           -- Telegram gift internal name/id
gift_price      INT NOT NULL           -- price in Stars
ticket_price    INT DEFAULT 1          -- Stars per ticket (always 1 or 2)
multiplier      FLOAT DEFAULT 3.0      -- target = gift_price × multiplier
target_stars    INT                    -- computed: gift_price × multiplier
collected_stars INT DEFAULT 0          -- real Stars paid (NOT including bonus tickets)
status          ENUM('draft','active','drawing','completed','cancelled')
winner_id       UUID FK → users.id  NULLABLE
ends_at         TIMESTAMPTZ NULLABLE   -- optional deadline
created_by      UUID FK → users.id
created_at      TIMESTAMPTZ DEFAULT now()
completed_at    TIMESTAMPTZ NULLABLE
```

### `ticket_ledger`
```
id              UUID PK
user_id         UUID FK → users.id
amount          INT NOT NULL           -- positive = credit, negative = debit
type            ENUM('purchase','referral','admin_grant','streak_bonus','raffle_entry')
ref_raffle_id   UUID FK → raffles.id  NULLABLE
ref_user_id     UUID FK → users.id    NULLABLE   -- who triggered this (e.g. referral source)
note            VARCHAR(512)
created_at      TIMESTAMPTZ DEFAULT now()
```

### `raffle_entries`
```
id              UUID PK
raffle_id       UUID FK → raffles.id
user_id         UUID FK → users.id
tickets_used    INT NOT NULL           -- how many tickets this user put in
created_at      TIMESTAMPTZ DEFAULT now()
UNIQUE(raffle_id, user_id)             -- one entry row per user per raffle, update tickets_used if they add more
```

### `referrals`
```
id              UUID PK
referrer_id     UUID FK → users.id
referred_id     UUID FK → users.id  UNIQUE   -- each user referred once
raffle_id       UUID FK → raffles.id NULLABLE -- which raffle triggered confirmation
status          ENUM('pending','confirmed','rewarded')
confirmed_at    TIMESTAMPTZ NULLABLE
created_at      TIMESTAMPTZ DEFAULT now()
```

### `transactions`
```
id              UUID PK
user_id         UUID FK → users.id
telegram_payment_charge_id  VARCHAR(256) UNIQUE
stars_amount    INT NOT NULL
tickets_granted INT NOT NULL
raffle_id       UUID FK → raffles.id NULLABLE
status          ENUM('pending','completed','refunded')
created_at      TIMESTAMPTZ DEFAULT now()
```

---

## CORE BUSINESS LOGIC

### 1. Ticket Wallet

Every user has a **single global Rafflix Wallet** (`users.ticket_balance`) — their personal ticket balance across all raffles.

- Tickets never expire.
- Every balance change MUST write a row to `ticket_ledger` first, then update `users.ticket_balance`. Do this in a single DB transaction.
- Helper function: `async def credit_tickets(session, user_id, amount, type, ref_raffle_id=None, ref_user_id=None, note="")`
- Helper function: `async def debit_tickets(session, user_id, amount, type, ref_raffle_id, note="")` — raises `InsufficientTicketsError` if balance < amount.

### 2. Buying Tickets (Telegram Stars)

Flow:
1. User taps "Buy Tickets" in Web App → selects quantity (1–50).
2. Web App calls `sendInvoice` via bot (using `web_app_open_invoice`).
3. Invoice: `currency="XTR"`, `prices=[LabeledPrice("Tickets", quantity)]`, `payload=JSON({user_id, quantity, raffle_id_hint})`.
4. On `pre_checkout_query` → always answer OK.
5. On `successful_payment`:
   - Record `transactions` row.
   - `credit_tickets(user_id, quantity, 'purchase', note=f"Bought {quantity} tickets")`.
   - If user was referred and this is their **first purchase ever** → trigger referral confirmation (see §4).
   - Reply with confirmation message.

### 3. Entering a Raffle

Flow:
1. User opens raffle detail in Web App → sees their balance → picks ticket count → taps "Enter".
2. Web App sends `POST /api/raffles/{raffle_id}/enter` with `{ tickets: N }`.
3. Backend:
   - Check raffle status == 'active'.
   - Check user balance >= N.
   - `debit_tickets(user_id, N, 'raffle_entry', ref_raffle_id=raffle_id)`.
   - Upsert `raffle_entries` (add N to existing `tickets_used` if row exists).
   - Do NOT add to `collected_stars` here — `collected_stars` only tracks real Stars paid.
   - Return updated entry + new balance.

**Important distinction:**
- `raffle.collected_stars` = sum of real Stars from `transactions` linked to this raffle (or all purchases made while raffle is active — your choice, document it).
- Raffle completion trigger: `collected_stars >= target_stars`.
- Bonus tickets from referrals participate in the draw but do NOT count toward `collected_stars`.

### 4. Referral System

**Rules:**
- Each user has one referral link: `t.me/RafflixBot?start=ref_{user_id_short}`.
- When user A clicks that link and starts the bot → record `referrals(referrer=A_inviter, referred=A, status='pending')`.
- When the referred user makes their **first ever Stars purchase** → set status='confirmed', then:
  - `credit_tickets(referrer_id, 1, 'referral', ref_user_id=referred_id, note="Referral bonus")`.
  - Set status='rewarded'.
  - Notify referrer: "🎉 Your friend {name} joined and bought tickets! +1 ticket added to your wallet."
- **Anti-abuse rules** (enforce all):
  - Only first purchase triggers the reward. Subsequent purchases by the same referred user = no extra reward.
  - A referrer can earn max **5 referral tickets per raffle period** (track per raffle, or per 7-day window — your choice, document it).
  - A user cannot refer themselves (check `referrer_id != referred_id`).
  - Telegram account age check: query `user.created_at` from Telegram — if account is less than 30 days old, mark referral as suspicious, give reward only after manual admin review (add `is_suspicious BOOL` flag to referrals).

### 5. Raffle Drawing

Triggered automatically when `collected_stars >= target_stars`.

Algorithm:
```python
async def draw_winner(raffle_id):
    # 1. Set raffle status = 'drawing' (prevents new entries)
    # 2. Fetch all raffle_entries for this raffle
    # 3. Build weighted ticket pool:
    pool = []
    for entry in entries:
        pool.extend([entry.user_id] * entry.tickets_used)
    # 4. Pick winner
    winner_id = random.choice(pool)
    # 5. Set raffle.winner_id = winner_id, status = 'completed', completed_at = now()
    # 6. Send Telegram Gift to winner via sendGift API
    # 7. Announce in channel/group
    # 8. Update streak_count for all participants (+1), reset for non-participants
```

**If gift delivery fails** (user never opened bot DM):
- Store `delivery_status = 'failed'` on raffle.
- Alert admin via bot message with winner's username + gift name.
- Admin can retry manually or issue Stars refund.

### 6. Streak Bonus

After every raffle completes:
- For every participant: `user.streak_count += 1`
- For every non-participant (who participated in previous): `user.streak_count = 0`
- If `streak_count` reaches 5 → `credit_tickets(user_id, 1, 'streak_bonus', note="5-raffle streak bonus!")`
- If `streak_count` reaches 10 → `credit_tickets(user_id, 3, 'streak_bonus', note="10-raffle streak bonus!")`

---

## BOT COMMANDS & HANDLERS

### User Commands
```
/start [ref_XXXX]   — Welcome message + register user + handle referral param
/wallet             — Show ticket balance + mini summary
/raffles            — List active raffles (inline keyboard)
/history            — Last 10 ticket ledger entries
/referral           — Show referral link + stats
/help               — How it works explanation
```

### Admin Commands (only for ADMIN_IDS)
```
/admin              — Admin panel keyboard
/newraffle          — Start raffle creation wizard (conversation handler):
                       → Gift name → Gift price (Stars) → Multiplier → Ticket price → Deadline (optional) → Confirm
/endraffle [id]     — Force-complete a raffle (manual draw trigger)
/cancelraffle [id]  — Cancel + refund all Stars
/granttickets [user_id] [amount] [reason]  — Grant bonus tickets manually
/stats              — Global stats: total users, active raffles, Stars collected
```

### Handlers
```
pre_checkout_query          — Always answer True
successful_payment          — Credit tickets + referral check
callback_query: join_raffle — Deep link from channel post into Web App
```

---

## FASTAPI BACKEND ENDPOINTS

All endpoints require Telegram Web App `initData` in header `X-Telegram-Init-Data`. Validate it using HMAC-SHA256 with BOT_TOKEN before processing any request.

```
GET  /api/me                         — Current user profile + balance
GET  /api/raffles                    — List active raffles
GET  /api/raffles/{id}               — Raffle detail + user's current entry
POST /api/raffles/{id}/enter         — Enter raffle { tickets: int }
GET  /api/wallet                     — Balance + ledger history (paginated)
GET  /api/referral                   — Referral link + stats (count, rewarded, pending)
GET  /api/raffles/{id}/participants  — List participants + ticket counts (public, for transparency)
```

---

## TELEGRAM WEB APP FRONTEND

### Design

Dark theme matching Telegram's aesthetic. Use these design tokens:

```css
--bg-primary:    #0F0F0F   /* near-black base */
--bg-card:       #1C1C1E   /* card surfaces */
--bg-elevated:   #2C2C2E   /* inputs, chips */
--accent:        #FFD60A   /* gold — Stars color, Rafflix primary CTA */
--accent-soft:   #FFD60A22 /* accent backgrounds */
--text-primary:  #FFFFFF
--text-secondary:#AEAEB2
--text-muted:    #636366
--success:       #30D158
--danger:        #FF453A
--border:        #38383A
--radius-card:   16px
--radius-btn:    12px
```

Font: System font stack (`-apple-system, BlinkMacSystemFont, 'SF Pro Display', sans-serif`) — matches Telegram native feel.
Logo: "Rafflix" wordmark — the "R" letter in gold (#FFD60A) on dark bg, rest white. Keep it compact for mobile header.

### Pages / Screens

**1. Home (`/`)**
```
Header: Rafflix logo + "🎟️ {balance} tickets" chip (top right) chip (top right)
Section: Active Raffles (card list)
  Each card:
    - Gift emoji + name
    - Progress bar: collected_stars / target_stars (gold fill)
    - "X tickets sold · Y spots left"
    - Countdown timer if deadline set
    - [Enter Raffle →] button
Section: My Active Entries (if any)
Bottom nav: Home | Wallet | Referral | History
```

**2. Raffle Detail (`/raffle/:id`)**
```
Back button
Gift image/emoji (large, centered)
Title + prize value in Stars
Progress bar (animated, gold)
Stats row: Total tickets | Participants | Your tickets
"Win probability: X.X%" (recalculated live as user adjusts)

Ticket selector:
  [−] [  3  ] [+]   ← tap or hold
  "Cost: 3 tickets from your wallet"
  "Your wallet: 12 🎟️  →  9 🎟️ after"
[Enter with N tickets] CTA button (gold, full-width)

Participants section (collapsible):
  List of participants with ticket counts (for transparency)
  
If raffle status = 'drawing':
  Animated spinner "Drawing winner..."
If status = 'completed':
  Winner banner with confetti animation
```

**3. Wallet (`/wallet`)**
```
Balance card (prominent):
  🎟️ 12 tickets
  [+ Buy tickets]  ← opens Stars invoice

Buy tickets modal:
  Quantity selector [1] [5] [10] [25] [50]
  "= {N} Stars" shown below
  [Pay with Stars ⭐] button

Transaction history list:
  Each row: icon + description + amount (+/-) + date
  Types styled differently:
    + purchase   → gold
    + referral   → green  
    + streak     → purple
    - entry      → white/muted
```

**4. Referral (`/referral`)**
```
Referral link card:
  "Invite friends, earn tickets"
  [t.me/RafflixBot?start=ref_XXXX]
  [📋 Copy link]  [📤 Share]

Stats grid:
  Invited: 8 | Confirmed: 3 | Earned: 3 🎟️

How it works (3 steps):
  1. Share your link
  2. Friend buys tickets
  3. You get +1 ticket

Referral list (collapsible):
  Each friend: avatar initial + name + status badge
```

**5. History (`/history`)**
```
Ledger list (paginated, 20 per page):
  Each entry: type icon | note | ±amount | timestamp
Filter chips: All | Purchases | Referrals | Entries | Bonuses
```

### Web App Behavior Notes
- Initialize with `Telegram.WebApp.ready()` on mount.
- Use `Telegram.WebApp.openInvoice()` for Stars payments.
- Use `Telegram.WebApp.MainButton` for primary CTAs on detail screens.
- Use `Telegram.WebApp.HapticFeedback` on button taps and state changes.
- Handle `Telegram.WebApp.onEvent('invoiceClosed', callback)` to refresh balance after payment.
- Support `Telegram.WebApp.colorScheme` (dark/light) — default to dark, respect system if light.

---

## CHANNEL / GROUP ANNOUNCEMENT FORMAT

When a new raffle starts, bot posts to configured channel:

```
🎬 RAFFLIX — NEW RAFFLE — 🧸 Teddy Bear

💰 Prize value: 15 ⭐ Stars
🎟️ Ticket price: 1 ticket
🎯 Target pool: 45 Stars (3×)
👥 0 participants · 0 tickets sold

[🎟️ Join on Rafflix] ← button opens Web App
```

Bot edits this message live as tickets are sold (every 5 new tickets or on each entry — configurable).

When raffle completes:
```
🎬 RAFFLIX — RAFFLE COMPLETE — 🧸 Teddy Bear

🎉 Winner: @username
🎟️ They held 7 of 45 tickets (15.6% chance)
⭐ Pool: 45 Stars collected
🎁 Gift sent directly to winner!

Thanks to all 23 participants 🙏
```

---

## SECURITY REQUIREMENTS

1. **Validate every Web App request**: Verify `initData` HMAC signature using bot token. Reject anything that fails.
2. **Idempotency**: Use `telegram_payment_charge_id` as unique key — never credit the same payment twice.
3. **DB transactions**: All balance operations (credit + ledger write) must be atomic.
4. **Rate limiting**: Max 10 API requests per second per user (Redis-based).
5. **Admin verification**: All `/admin*` commands check `message.from_user.id in ADMIN_IDS` before executing.
6. **Referral self-referral guard**: Always check `referrer_id != referred_id` at the DB constraint level too.

---

## ERROR HANDLING

| Scenario | Behavior |
|---|---|
| Insufficient tickets | 400 response + "Not enough tickets" toast in Web App |
| Raffle not active | 409 response + friendly message |
| Payment already processed | 200 idempotent response (no double credit) |
| Gift delivery failed | Admin DM alert + `delivery_status='failed'` stored |
| DB connection lost | 503 + retry logic in Celery task |
| Invalid initData | 401 immediately |

---

## FOLDER STRUCTURE

```
rafflix-bot/
├── bot/
│   ├── main.py               # aiogram app + webhook setup
│   ├── handlers/
│   │   ├── start.py          # /start + referral param
│   │   ├── payments.py       # pre_checkout + successful_payment
│   │   ├── admin.py          # admin commands + raffle wizard
│   │   └── menu.py           # /wallet /referral /raffles /history
│   ├── keyboards/
│   │   ├── inline.py
│   │   └── reply.py
│   └── utils/
│       ├── referral.py       # referral confirmation logic
│       └── announcer.py      # channel post + edit logic
├── api/
│   ├── main.py               # FastAPI app
│   ├── auth.py               # initData HMAC validator
│   ├── routers/
│   │   ├── raffles.py
│   │   ├── wallet.py
│   │   └── referral.py
│   └── schemas/              # Pydantic models
├── core/
│   ├── models.py             # SQLAlchemy ORM models
│   ├── database.py           # async engine + session factory
│   ├── wallet.py             # credit_tickets / debit_tickets helpers
│   ├── draw.py               # draw_winner algorithm
│   └── config.py             # Settings from env
├── worker/
│   ├── celery_app.py
│   └── tasks.py              # draw trigger, streak update, announcements
├── migrations/               # Alembic
├── webapp/                   # React + Vite frontend
│   ├── src/
│   │   ├── pages/
│   │   │   ├── Home.jsx
│   │   │   ├── RaffleDetail.jsx
│   │   │   ├── Wallet.jsx
│   │   │   ├── Referral.jsx
│   │   │   └── History.jsx
│   │   ├── components/
│   │   │   ├── RaffleCard.jsx
│   │   │   ├── ProgressBar.jsx
│   │   │   ├── TicketSelector.jsx
│   │   │   ├── BottomNav.jsx
│   │   │   └── TransactionRow.jsx
│   │   ├── hooks/
│   │   │   ├── useTelegram.js    # WebApp SDK wrapper
│   │   │   └── useApi.js         # fetch wrapper with initData header
│   │   ├── store/
│   │   │   └── userStore.js      # Zustand store
│   │   └── styles/
│   │       └── tokens.css        # Design tokens
│   └── vite.config.js
├── docker-compose.yml
└── README.md
```

---

## IMPLEMENTATION ORDER

Build in this exact sequence to avoid blockers:

1. **Database models + migrations** — get schema locked first
2. **`core/wallet.py`** — credit/debit helpers with ledger (most critical logic)
3. **Bot `/start` handler** — user registration + referral param parsing
4. **Payments handler** — pre_checkout + successful_payment + ticket crediting
5. **FastAPI auth middleware** — initData validation (needed before any API work)
6. **Raffle CRUD** — admin create/list/complete, API endpoints
7. **Raffle entry endpoint** — debit tickets + upsert raffle_entries
8. **Draw algorithm** — `core/draw.py` + Celery trigger task
9. **Referral confirmation logic** — hook into first purchase flow
10. **Streak logic** — Celery task post-draw
11. **Channel announcer** — post on create, edit on entry, complete post
12. **React Web App** — build pages in order: Home → Wallet → Raffle Detail → Referral → History
13. **Admin commands** — raffle wizard, grant tickets, stats
14. **Polish** — haptic feedback, animations, error toasts, loading states

---

## KEY BUSINESS RULES SUMMARY (Never Violate)

```
✅ collected_stars counts ONLY real Stars paid — never bonus tickets
✅ Raffle triggers when collected_stars >= target_stars
✅ Bonus tickets JOIN the draw pool but don't affect collected_stars
✅ Every balance change = atomic DB transaction + ledger row
✅ Referral reward fires ONCE per referred user (their first purchase)
✅ Max 5 referral bonus tickets per referrer per raffle/week window
✅ Referrer cannot be referred_id
✅ Raffle entries are final — no refunds on tickets used in a raffle
✅ Stars refund only on raffle cancellation (via Telegram Stars refund API)
✅ Admin gift delivery failure must alert admin immediately
✅ All API endpoints validate Telegram initData signature
```

---

*Build Rafflix step by step. Start with the database schema and wallet logic — everything else depends on those being correct. Bot username: @RafflixBot*