# Crypto Alerts API

A lightweight, multi‐tenant service for registering price‐threshold alerts on cryptocurrencies, backed by FastAPI, PostgreSQL, Redis, and Celery. Users can create alerts and receive notifications (email, SMS, webhook) when prices cross specified thresholds.

---

## 🚀 Project Overview

- **Language & Framework:** Python 3.11, FastAPI  
- **Database:** PostgreSQL (SQLAlchemy + Alembic)  
- **Cache & Queue:** Redis + Celery  
- **Auth:** JWT (Bearer)  
- **Notifications:** Pluggable channels (email, SMS, webhooks)  
- **Containerization:** Docker & Docker Compose

---

## 📦 Prerequisites

- Docker & Docker Compose (v2+)  
- (Optional) Python 3.11 + virtualenv, if running locally  

---

## ⚙️ Setup & Running with Docker

1. **Clone the repo**  
   ```bash
   git clone https://github.com/your-org/crypto-alerts-api.git
   cd crypto-alerts-api
   ```

2. **Configure environment**  
   Copy `.env.example` → `.env` and fill in secrets:
   ```ini
   DATABASE_URL=postgresql+psycopg2://postgres:example@db:5432/crypto_alerts
   REDIS_URL=redis://redis:6379/0
   JWT_SECRET=your_jwt_secret_here
   BACKEND_CORS_ORIGINS=["http://localhost:3000"]
   ```

3. **Build & start containers**  
   ```bash
   docker-compose up --build -d
   ```

4. **Apply migrations**  
   ```bash
   docker-compose run --rm api alembic upgrade head
   ```

5. **Check API docs**  
   Open in your browser:  
   ```
   http://localhost:8000/api/v1/docs
   ```

---

## 🗂 Alembic Migrations

All schema changes are managed with Alembic.

- **Create a new revision**  
  ```bash
  docker-compose run --rm api alembic revision --autogenerate -m "describe change"
  ```

- **Apply migrations**  
  ```bash
  docker-compose run --rm api alembic upgrade head
  ```

- **Downgrade (rollback) to a specific revision**  
  ```bash
  docker-compose run --rm api alembic downgrade <revision_id>
  ```

- **Reset to zero (empty schema)**  
  ```bash
  docker-compose run --rm api alembic downgrade base
  ```

---

## 🧩 Managing Dependencies

- **Requirements file**  
  All Python deps are pinned in `requirements.txt`.  
- **Adding a new dependency**  
  ```bash
  pip install <package>
  pip freeze > requirements.txt
  ```
- **Docker rebuild** (after deps change)  
  ```bash
  docker-compose up -d --build api
  ```

---

## 🔧 Running Locally (no Docker)

1. **Create & activate venv**  
   ```bash
   python3.11 -m venv .venv
   source .venv/bin/activate
   ```

2. **Install deps**  
   ```bash
   pip install -r requirements.txt
   ```

3. **Start Postgres & Redis**  
   Use your local installs or run via Docker:
   ```bash
   docker-compose up -d db redis
   ```

4. **Configure `.env`** (as above) and export:
   ```bash
   export $(grep -v '^#' .env | xargs)
   ```

5. **Run migrations**  
   ```bash
   alembic upgrade head
   ```

6. **Start FastAPI with reload**  
   ```bash
   uvicorn app.main:app --reload
   ```

---

## 📚 Usage

1. **Sign up**  
   `POST /api/v1/auth/signup` with JSON `{ "email": "...", "password": "..." }`

2. **Log in**  
   `POST /api/v1/auth/login` with JSON `{ "email": "...", "password": "..." }`  
   → returns `{ "access_token":"…", "token_type":"bearer" }`

3. **Authorize in Swagger UI**  
   Click **Authorize**, paste `Bearer <access_token>`.

4. **CRUD Alerts**  
   - `POST   /api/v1/alerts`  
   - `GET    /api/v1/alerts`  
   - `GET    /api/v1/alerts/{id}`  
   - `PUT    /api/v1/alerts/{id}`  
   - `DELETE /api/v1/alerts/{id}`  

---

## 🛡 Security & Best Practices

- Secrets loaded from `.env` via Pydantic’s `BaseSettings`  
- JWT tokens with expiration  
- HTTPS should be enforced in production  
- Rate‐limit endpoints (e.g. with `slowapi`)  
- Structured logging + monitoring

---

## 📦 Dockerfile & Compose Highlights

- **Dockerfile**  
  - Python 3.11-slim base  
  - `requirements.txt` layer caching  
  - `uvicorn --reload` for dev

- **docker-compose.yml**  
  - Services: `api`, `db` (Postgres), `redis`  
  - Named volume for Postgres data  
  - `.env` mounted into `api`

---

## 🏗️ Next Steps

- Add Celery workers & beat scheduler  
- Integrate polling of Binance API  
- Implement notifier channels (SendGrid, webhooks)  
- Write end-to-end & integration tests  
- Configure CI/CD (GitHub Actions → AWS)
