# Trekking Management Application V2 (TMA-V2)

A full-stack trekking management system supporting Admin, Staff, and Trekker roles for trek lifecycle management, bookings, participant tracking, and notifications.

## Tech Stack

**Backend:** Flask, Flask-RESTful, Flask-JWT-Extended, Flask-CORS, SQLAlchemy, SQLite, Werkzeug Security, Flask-Mail, Flask-Caching + Redis, Celery + Celery Beat, python-dotenv

**Frontend:** Vue 3, Vue Router, Axios, Bootstrap 5.3.8 (CDN), Chart.js 4.5.1

## Prerequisites

Make sure these are installed on your machine before setting up the project:

- Python 3.10+
- Node.js 18+ and npm
- Redis server
- Git (optional, only needed if cloning via git)

## Project Structure

```
Trekking_Management_May26/
├── backend/          # Flask API, models, Celery tasks
├── frontend/         # Vue 3 application
├── package.json      # (root — not used by the app directly)
└── README.md
```

## 1. Backend Setup

```bash
cd backend
python3 -m venv venv
source venv/bin/activate        # On native Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Environment Variables

Create a `.env` file inside `backend/` with the following (values are examples — use your own):

```
JWT_SECRET_KEY=your_secret_key_here
MAIL_USERNAME=your_gmail_address@gmail.com
MAIL_PASSWORD=your_gmail_app_password
REDIS_URL=redis://localhost:6379/0
```

> This file is not included in the repo/zip for security reasons — you must create it yourself on every new machine.

### Database

The SQLite database is created automatically on first run. The Admin account is seeded programmatically — no manual setup needed.

## 2. Frontend Setup

```bash
cd frontend
npm install
```

## 3. Start Redis

Redis must be running before starting Celery or the backend.

```bash
redis-server
```

(If not installed: `sudo apt install redis-server` on WSL/Linux.)

## 4. Running the Application

Open four separate terminals:

**Terminal 1 — Backend (Flask)**
```bash
cd backend
source venv/bin/activate
flask run
```

**Terminal 2 — Celery Worker**
```bash
cd backend
source venv/bin/activate
celery -A app.celery worker --loglevel=info
```

**Terminal 3 — Celery Beat (scheduled tasks)**
```bash
cd backend
source venv/bin/activate
celery -A app.celery beat --loglevel=info
```

**Terminal 4 — Frontend (Vue)**
```bash
cd frontend
npm run dev
```

The frontend will typically be available at `http://localhost:5173` and the backend API at `http://localhost:5000` (confirm against your actual Flask/Vite config).

## Roles & Access

| Role | Account Creation | Key Permissions |
|---|---|---|
| Admin | Pre-seeded | Create/approve/cancel treks, manage staff & users, view all stats |
| Staff | Created by Admin only | Update slots, open/close treks, mark completed, view assigned bookings (read-only) |
| Trekker | Self-registration | Book treks, manage own bookings and profile |

## Notes

- Bootstrap is loaded via CDN only — do not `npm install bootstrap`, as this causes modal/backdrop conflicts.
- Celery Beat is configured for IST (`enable_utc = False`); trek close-warnings and reminders are scheduled accordingly.
- `node_modules` and `venv` are excluded from version control/zips — always reinstall via `npm install` and `pip install -r requirements.txt` on a new machine.
