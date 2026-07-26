# 👑 Crownd
### *Where every purchase is your crowning moment.*

![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![Supabase](https://img.shields.io/badge/Supabase-3ECF8E?style=for-the-badge&logo=supabase&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)
![Razorpay](https://img.shields.io/badge/Razorpay-02042B?style=for-the-badge&logo=razorpay&logoColor=white)
![Instagram](https://img.shields.io/badge/Instagram_API-E4405F?style=for-the-badge&logo=instagram&logoColor=white)
![Vanilla JS](https://img.shields.io/badge/Vanilla_JS-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black)
![Render](https://img.shields.io/badge/Render-46E3B7?style=for-the-badge&logo=render&logoColor=white)

> **Influencer Wallets** &nbsp;·&nbsp; **Verified UGC** &nbsp;·&nbsp; **Purchase-Linked Cashback** &nbsp;·&nbsp; **Brand Campaign Tiers** &nbsp;·&nbsp; **Crownd Score Matching**

*Real Buyers • Real Posts • Instagram-Verified Cashback • Crownd Score Unlock System • FastAPI + Supabase Backend*

**🔴 LIVE DEMO** — https://crownd3.onrender.com/
**📂 REPO** — https://github.com/ju-pyjanvi/Crownd


**PPT** - https://drive.google.com/file/d/1f2fkKyGfWk420u_qOf79_BoVtlaq075y/view?usp=sharing

---

## 📌 What Is Crownd?

Crownd turns micro-influencers — anyone with 1,000+ Instagram followers — into a brand's cheapest and most authentic marketing channel.

Creators **shop** at partner brands using a Crownd Wallet, **post** about it on Instagram, and **get real cashback** credited back. Brands pay only when a verified purchase and a verified post both happen — not for impressions, not for reach promises. Not for content that no one bought.

Traditional influencer marketing pays creators a flat fee whether or not the content performs. There's no way to confirm a post is tied to an actual purchase. Crownd closes that loop: purchase, post, and reach all flow through one platform — cashback is only ever paid out against something independently verified.

---

## ✨ Key Features

| Feature | Description |
|---|---|
| **Crownd Wallet** | An in-app balance every influencer earns into and spends from — funded by cashback, topped up via Razorpay for purchases at partner brands |
| **Buy → Post → Cashback Loop** | Influencer logs a purchase, posts on Instagram tagging the brand, and once verified, cashback is calculated and credited automatically |
| **Crownd Score** | A single 0–1000 score built from verified post count, engagement rate, and brand diversity — higher score unlocks access to premium brand tiers |
| **Three Brand Campaign Tiers** | Coronet (cashback campaigns), Regalia (product seeding / barter), Sovereign (curated collaborations, Score 750+ only) |
| **Instagram Graph API Verification** | Real post verification — checks brand tagging and account engagement before cashback releases. Falls back to mock for local dev |
| **JWT Auth** | Email/password signup and OAuth2 login with bearer-token-protected routes across every endpoint |
| **Razorpay Wallet Top-Ups** | Real test-mode payment orders, client-side checkout widget, HMAC SHA-256 server-side signature verification before any balance is credited |
| **First-Purchase Vouchers** | Bonus voucher issued automatically on a creator's first purchase from any brand — encourages brand discovery |

---

## 🖥️ Platform Walkthrough

### Landing — Shop. Post. Get Paid.
The homepage opens on a soft mint-and-blob aesthetic in Crownd's maroon, marigold, and mehendi-green palette. A **For Creators / For Brands** toggle switches the entire page between two audiences without a reload.

### How It Works — Step Flow
A three-step timeline explains the loop: shop at a partner brand using the Crownd Wallet → post a real opinion tagging the brand on Instagram → once verified, cashback lands back in the wallet, spendable at any partner brand.

### Where You Can Earn
Three category cards — **Fashion & Beauty**, **Food & Dining**, **Lifestyle & Tech** — each with a worked cashback example and real rupee figures, showing creators exactly what they stand to earn from content they were going to make anyway.

### Crownd Score — The Progression System
Scores run Signet (0–199) → Coronet (200–499) → Royal (500–799) → Sovereign (800+). Each tier unlocks progressively better brand partnerships. The score grows with every verified post — factoring in engagement rate, content quality, and how many *different* brands you've posted about, not loyalty to one.

### For Brands — Three Campaign Tiers
A dedicated brands page (switching via the toggle) lists Coronet, Regalia, and Sovereign as progressive cards — each tier includes everything from the one below it, plus additional capabilities. No middle card is pre-highlighted; each tier stands on its own.

### Dashboard — Wallet, Score, Live Campaigns
Once signed in, influencers see their real wallet balance, Crownd Score breakdown, and a campaign ladder of eligible vs. locked brand partnerships — pulled live from the backend. Starting a campaign calls the purchase endpoint directly and refreshes wallet and score state on completion.

### Wallet — Top-Ups & Transaction History
Triggers the full Razorpay flow: request an order from the backend → open the Razorpay checkout widget → verify the payment signature server-side → balance updates. Transactions are tagged `cashback`, `topup`, or `payment`.

---

## 🛠️ Architecture & Tech Stack

```
Crownd/
├── backend/
│   ├── main.py                 # FastAPI app, router registration, CORS
│   ├── database.py             # SQLAlchemy engine + session config
│   ├── models.py               # User, Wallet, Transaction, Brand, Purchase, CrowndScore
│   ├── schemas.py              # Pydantic request/response models
│   ├── auth.py                 # JWT creation/validation, bcrypt hashing, current-user deps
│   ├── requirements.txt
│   └── routers/
│       ├── influencer.py       # Signup, login, profile, Crownd Score
│       ├── brand.py            # Brand listing, tiers, eligibility check
│       ├── wallet.py           # Balance, Razorpay load/verify, transaction history
│       ├── purchase.py         # Purchase initiation, tier-based cashback calculation
│       ├── post.py             # Instagram post submission + verification + cashback credit
│       └── instagram_oauth.py  # Instagram Graph API OAuth callback
└── frontend/
    ├── index.html              # Landing page — Creators / Brands toggle
    ├── auth.html               # Sign up / sign in
    ├── dashboard.html          # Wallet, Crownd Score, campaign ladder
    ├── wallet.html             # Top-ups, transaction history
    ├── partner.html            # Brand partnership application
    ├── auth_callback.html      # Instagram OAuth redirect handler
    └── shopfirst.html          # First-purchase / voucher flow
```

| Layer | Technology |
|---|---|
| **Backend** | FastAPI (Python) — 5 routers, 17 endpoints |
| **Database** | PostgreSQL via Supabase — SQLAlchemy ORM |
| **Auth** | JWT bearer tokens via `python-jose`, bcrypt via `passlib` |
| **Payments** | Razorpay test-mode — order creation + HMAC signature verification |
| **Social Verify** | Instagram Graph API — Business Login, `instagram_basic` + `instagram_manage_insights` scopes |
| **Frontend** | Vanilla HTML/CSS/JS — no build step, no framework |
| **Hosting** | Render (backend) + GitHub Pages (frontend) |

---

## 🔬 How The Cashback Loop Works

Crownd verifies three things before a single rupee of cashback moves:

**1. Purchase**
`POST /purchase/initiate` — backend checks the influencer's Crownd Score against `min_crownd_score`, confirms wallet balance, checks brand-specific redemption cap, logs purchase as `post_required`.

**2. Post**
`POST /post/submit` — backend calls the Instagram Graph API to confirm the post exists, is tagged correctly, and meets engagement thresholds. Falls back to mock URL-pattern check when no live token is configured.

**3. Cashback**
Once the post verifies, cashback is calculated against the brand's campaign tier rules — a percentage of purchase value, capped at `max_cashback_cap` — and credited directly into the influencer's Crownd Wallet. Crownd Score is recalculated immediately, factoring in the new verified post and updated brand diversity.

**Brand Funding:** Brands never pay influencers directly. They pre-commit a monthly campaign budget; cashback is paid out of that budget only against verified purchase+post pairs. Crownd earns its commission on the underlying transaction value separately.

---

## 📊 Revenue Model

| Stream | Mechanism |
|---|---|
| **Brand Commission** | % of purchase value on every verified cashback-eligible transaction — billed to the brand separately from the cashback budget |
| **Wallet Transaction Fee** | Small platform fee on in-app wallet spends at partner brands |
| **Visa Interchange Share** | On virtual/physical card spends via a licensed PPI partner — standard programme-manager fintech arrangement |
| **Optional Physical Card** | ₹499 one-time co-branded card fee — activation filter, not core revenue |

---

## 🪙 Demo Wallet — Razorpay Test Mode

The live demo uses **Razorpay test mode**. No real money moves.

To trigger a wallet top-up in the demo:

| Field | Value |
|---|---|
| Card Number | `4111 1111 1111 1111` |
| Expiry | Any future date |
| CVV | Any 3 digits |
| OTP (if prompted) | `1234` |

The backend creates a real Razorpay test order, the frontend opens the Razorpay checkout widget, and after payment the server verifies the HMAC SHA-256 signature before crediting the balance. The full flow runs exactly as it would in production — just against Razorpay's sandbox.

---

## 📸 Instagram API — Live vs Mock

The backend supports two modes for Instagram verification, switchable via `.env`:

**Mock mode (default for local dev):**
```env
INSTAGRAM_ACCESS_TOKEN=mock
```
Post verification checks that the submitted URL is a valid Instagram URL pattern. Cashback credits automatically. Use this for local testing — no Facebook app required.

**Live mode (production):**
```env
INSTAGRAM_ACCESS_TOKEN=your_long_lived_token
```
Requires a Meta Developer app with Instagram Graph API access, a linked Facebook Page, and the `instagram_basic`, `instagram_manage_insights`, `pages_show_list`, and `pages_read_engagement` scopes approved. The backend checks the post exists, confirms the brand tag is present, and validates engagement before releasing cashback.

To generate a long-lived token: Meta Developer Console → Graph API Explorer → generate token with required scopes → exchange for a 60-day long-lived token via `GET /oauth/access_token?grant_type=ig_exchange_token`.

---

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- A [Supabase](https://supabase.com) project (Postgres connection string + anon key)
- [Razorpay](https://razorpay.com) test-mode API keys
- A Meta Developer app with Instagram Graph API access *(optional — mockable)*

### Installation

```bash
git clone https://github.com/ju-pyjanvi/Crownd.git
cd Crownd/backend

# Create and activate virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # macOS/Linux

pip install -r requirements.txt
```

### Environment Variables

Create a `.env` file inside `backend/`:

```env
DATABASE_URL=postgresql://postgres:[PASSWORD]@db.[PROJECT_REF].supabase.co:5432/postgres
SUPABASE_URL=https://[PROJECT_REF].supabase.co
SUPABASE_KEY=your_supabase_anon_key

RAZORPAY_KEY_ID=your_razorpay_test_key_id
RAZORPAY_KEY_SECRET=your_razorpay_test_key_secret

SECRET_KEY=your_jwt_signing_secret
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080

INSTAGRAM_ACCESS_TOKEN=mock   # or your live token
```

### Run

```bash
# Backend
cd backend
uvicorn main:app --reload
# API runs at http://localhost:8000
# Swagger docs at http://localhost:8000/docs

# Frontend — no build step
cd ../frontend
# Open index.html directly in any browser
```

---

## 🎯 User Flow

```
Sign Up  →  Load Wallet (Razorpay)  →  Browse Brands
    →  Initiate Purchase  →  Post on Instagram
        →  Submit Post URL  →  Verification
            →  Cashback Credited  →  Crownd Score ↑
```

| Step | Endpoint |
|---|---|
| Sign up | `POST /auth/signup` |
| Log in | `POST /auth/login` |
| Load wallet | `POST /wallet/load` → `POST /wallet/verify-payment` |
| Browse brands | `GET /brands/` or `GET /brands/eligible/me` |
| Start campaign | `POST /purchase/initiate` |
| Submit post | `POST /post/submit` |
| Check score | `GET /auth/score` |
| View transactions | `GET /wallet/transactions` |

---

## 👩‍💻 Built By

Designed and engineered end-to-end.

- **Business Model** — Cashback economics, three-tier brand campaign structure, Crownd Score design, and the brand-funds-cashback-separately revenue split
- **Backend** — FastAPI + Supabase, JWT auth, Razorpay payment verification, Instagram Graph API integration, tier-based cashback calculation engine
- **Frontend & Design** — Vanilla HTML/CSS/JS across five linked pages, maroon/marigold/mehendi-green identity, blob-field aesthetic, progressive tier cards
- **Research** — Market sizing and CAC-reduction benchmarks sourced from EY, BCG, Kofluence, and Nielsen

---

## 📄 License

MIT — see `LICENSE` for details.

---

*Where every purchase is your crowning moment.* 👑
