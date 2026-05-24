# Vertrix

> **The modern Flask starter framework for deploying Machine Learning, Data Science, and AI models.**  
> Package your custom models, create clean API endpoints, secure prediction access, and log inferences from day one.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=flat-square&logo=python)
![Flask](https://img.shields.io/badge/Flask-3.0-black?style=flat-square&logo=flask)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)

---

## What's Included

| Feature | Details |
|---|---|
| Authentication | Register, Login, Logout with hashed passwords for secure model control |
| Database ORM | Flask-SQLAlchemy (SQLite default, MySQL-ready for logging model inferences) |
| Migrations | Flask-Migrate (Alembic-powered) |
| Blueprints | Modular route architecture to structure API prediction endpoints |
| App Factory | Clean `create_app()` pattern |
| Minimal Light UI | Bootstrap 5 + custom ultra-clean light theme with logo loading support |
| Config | dotenv-based environment configuration |
| Tests | pytest suite with in-memory DB fixtures for automated endpoint tests |

---

## Prerequisites

- Python **3.10** or newer
- `pip` and `venv` (both ship with Python)
- Git

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/Tedshub/Vertix.git
cd veltrix
```

### 2. Create and activate a virtual environment

**Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**Windows (Command Prompt):**
```cmd
python -m venv venv
venv\Scripts\activate.bat
```

**macOS / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

You should see `(venv)` at the start of your terminal prompt.

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

## Environment Setup

Copy the example environment file and edit it:

```bash
# Windows
copy .env.example .env

# macOS / Linux
cp .env.example .env
```

Open `.env` and set your values:

```env
SECRET_KEY=replace-this-with-a-long-random-string
FLASK_ENV=development
FLASK_DEBUG=True
DATABASE_URL=sqlite:///database.db
```

> Never commit `.env` to Git. It is already listed in `.gitignore`.

**Generate a strong secret key (optional but recommended):**
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

---

## Database Setup

Run the migration commands **once** after first setup (and again whenever you change your models):

```bash
# Initialise the migrations folder (first time only)
flask db init

# Generate a migration script based on your models
flask db migrate -m "Initial migration"

# Apply the migration to the database
flask db upgrade
```

The SQLite database file will be created automatically at `instance/database.db`.

---

## Running the Development Server

```bash
python run.py
```

Or using the Flask CLI:

```bash
flask run
```

Then open your browser at: **http://127.0.0.1:5000**

---

## Switching to MySQL

1. Install the MySQL driver:
   ```bash
   pip install pymysql
   ```

2. Update your `.env`:
   ```env
   DATABASE_URL=mysql+pymysql://username:password@localhost/veltrix_db
   ```

3. Create the database in MySQL:
   ```sql
   CREATE DATABASE veltrix_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   ```

4. Run migrations:
   ```bash
   flask db upgrade
   ```

---

## Running Tests

```bash
pytest
```

Verbose output:

```bash
pytest -v
```

With coverage report:

```bash
pip install pytest-cov
pytest --cov=app --cov-report=term-missing
```

---

## Project Structure

```text
veltrix/
│
├── app/
│   ├── __init__.py          # Application factory (create_app)
│   ├── config.py            # Dev / Test / Prod configuration classes
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   └── user.py          # User database model
│   │
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── main.py          # Landing + Dashboard routes
│   │   └── auth.py          # Register / Login / Logout routes
│   │
│   ├── templates/
│   │   ├── base.html        # Master layout (navbar, footer, flash)
│   │   ├── landing.html     # Public home page
│   │   ├── login.html       # Login form
│   │   ├── register.html    # Registration form
│   │   └── dashboard.html   # Protected user dashboard
│   │
│   ├── static/
│   │   ├── css/style.css    # Custom dark theme styles
│   │   ├── js/main.js       # Vanilla JS enhancements
│   │   └── img/             # Static images
│   │
│   └── utils/
│       ├── __init__.py
│       └── helpers.py       # format_datetime, slugify, truncate
│
├── instance/                # Auto-created; holds database.db (gitignored)
├── migrations/              # Flask-Migrate Alembic files
├── tests/
│   ├── __init__.py
│   └── test_app.py          # pytest test suite
│
├── .env                     # Your secrets (gitignored)
├── .env.example             # Template — safe to commit
├── .gitignore
├── run.py                   # Entry point: python run.py
├── requirements.txt
├── README.md
└── LICENSE
```

---

## Authentication Flow

| Action | URL | Method |
|---|---|---|
| Landing page | `/` | GET |
| Register | `/auth/register` | GET, POST |
| Login | `/auth/login` | GET, POST |
| Logout | `/auth/logout` | GET |
| Dashboard | `/dashboard` | GET (login required) |

- Unauthorized users visiting `/dashboard` are redirected to `/auth/login`.
- After logout, users are redirected to the landing page `/`.
- Passwords are hashed using **Werkzeug's** `generate_password_hash` (PBKDF2-SHA256).

---

## Customisation Tips

- **Add a new route:** Create a file in `app/routes/`, define a Blueprint, and register it in `app/__init__.py`.
- **Add a new model:** Create a file in `app/models/`, then run `flask db migrate && flask db upgrade`.
- **Change branding:** Search for "Veltrix" in `app/templates/` and `app/static/`.
- **Change colour palette:** Edit the CSS custom properties (`:root { ... }`) at the top of `app/static/css/style.css`.

---

## Dependencies

| Package | Purpose |
|---|---|
| `Flask` | Core web framework |
| `Flask-SQLAlchemy` | ORM / database abstraction |
| `Flask-Login` | Session-based authentication |
| `Flask-Migrate` | Database schema migrations |
| `python-dotenv` | Load environment variables from `.env` |
| `Werkzeug` | Password hashing, WSGI utilities |
| `email-validator` | Email format validation |

---

## License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

<p align="center">
  Built with Flask · Bootstrap 5 · SQLAlchemy
</p>