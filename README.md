# Personal Loan Tracker

A comprehensive self-hosted personal loan tracker.
Track money you lent and borrowed — with full payment history,
interest calculation, file attachments, and alerts.

Runs 100% locally on Docker / Portainer.

---

## Stack

| Service    | Image / Tech        | Port (local) |
|------------|---------------------|--------------|
| Database   | PostgreSQL 16       | 5432         |
| Backend    | FastAPI (Python)    | 8000         |
| Frontend   | React + Vite        | 5173         |
| Proxy      | Nginx               | **8080**     |
| Worker     | Python cron job     | —            |

---

## Quick Start (Kubuntu + Docker)

### 1. Clone / copy the project
```bash
cd ~/projects
# copy this folder here
cd loan-tracker
```

### 2. Create your .env file
```bash
cp .env.example .env
nano .env   # set your passwords and secret key
```

### 3. Start everything
```bash
docker compose up -d
```

### 4. Open the app
```
http://localhost:8080
```

---

## Portainer Setup

1. Open Portainer → **Stacks** → **Add stack**
2. Name it `loan-tracker`
3. Paste the contents of `docker-compose.yml`
4. Add environment variables from your `.env` file
   under **Environment variables**
5. Click **Deploy the stack**

---

## Folder Structure

```
loan-tracker/
├── docker-compose.yml
├── .env.example
├── .gitignore
│
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── migrations/
│   │   ├── init.sql      ← full schema + triggers
│   │   └── seed.sql      ← sample data (dev only)
│   └── app/
│       ├── main.py
│       ├── database.py
│       ├── config.py
│       ├── worker.py
│       ├── models/       ← SQLAlchemy ORM models
│       ├── schemas/      ← Pydantic request/response schemas
│       ├── api/          ← FastAPI route handlers
│       ├── services/     ← Business logic
│       └── utils/        ← Interest calc, file handling
│
├── frontend/
│   ├── Dockerfile
│   ├── package.json
│   └── src/
│       ├── pages/        ← Dashboard, Loans, People, etc.
│       ├── components/   ← Reusable UI components
│       ├── hooks/        ← Custom React hooks
│       └── utils/        ← API client, formatters
│
└── nginx/
    └── nginx.conf
```

---

## Data & Backups

All data lives in named Docker volumes:
- `loan_tracker_postgres_data` — database
- `loan_tracker_uploads` — attached files

### Manual backup
```bash
# Database
docker exec loan_tracker_db pg_dump -U loan_user loan_tracker > backup_$(date +%Y%m%d).sql

# Uploads
docker run --rm -v loan_tracker_uploads:/data -v $(pwd)/backups:/backup \
  alpine tar czf /backup/uploads_$(date +%Y%m%d).tar.gz -C /data .
```

---

## Features

- Track loans you gave (lent) and received (borrowed)
- Full contact info per person (name, phone, email, ID)
- Simple and compound interest with per-period ledger
- Log partial and full payments with method + reference
- Attach photos, PDFs, and screenshots to loans/payments
- Alerts: overdue, due-soon (7 days), partial reminders
- Complete audit log of every change
- Dashboard with net balance, overdue count, due soon
- Export to CSV and per-loan PDF statements
- 100% local — no cloud, no account, no tracking
