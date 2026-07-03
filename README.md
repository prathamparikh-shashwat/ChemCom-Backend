# FastAPI Standard Backend Template

A production-ready, clean-architecture template for building RESTful APIs using Python FastAPI, SQLAlchemy, Pydantic, and SQLite/PostgreSQL.

## Project Structure

This project follows a component-based clean architecture:

```text
Backend-ChemCom/
├── app/
│   ├── api/
│   │   ├── deps.py              # Injectable dependencies (DB session, auth checks)
│   │   └── v1/
│   │       ├── api.py           # V1 endpoint router aggregator
│   │       └── endpoints/
│   │           ├── auth.py      # Login and authentication tokens
│   │           └── users.py     # User creation, registration, and profile management
│   ├── core/
│   │   ├── config.py            # Pydantic Settings configuration validator
│   │   ├── database.py          # SQLAlchemy engine & session setup
│   │   └── security.py          # Hashing (bcrypt) & JWT token utilities
│   ├── crud/
│   │   └── crud_user.py         # Encapsulated database queries for users
│   ├── models/
│   │   └── user.py              # SQLAlchemy database model
│   ├── schemas/
│   │   └── user.py              # Pydantic schema validation & serialization models
│   └── main.py                  # App entry point, CORS settings, lifespan setup
├── .env                         # Local environment variables
├── .env.example                 # Example configuration
├── .gitignore                   # Standard gitignore configurations
└── requirements.txt             # Frozen dependencies file
```

---

## Getting Started

### 1. Installation

1. Create and activate a Python virtual environment (if you haven't already):
   ```bash
   # On Windows (PowerShell/CMD)
   python -m venv .venv
   .venv\Scripts\activate
   
   # On Linux/macOS
   python3 -m venv .venv
   source .venv/bin/activate
   ```

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### 2. Configuration

Create a `.env` file in the root directory (one is created automatically with defaults during initialization) and configure your secrets:
```env
PROJECT_NAME="FastAPI Standard Backend"
API_V1_STR="/api/v1"
SECRET_KEY="your-super-secret-key-change-me-in-production"
ACCESS_TOKEN_EXPIRE_MINUTES=60
DATABASE_URL="sqlite:///./sql_app.db"
```

### 3. Running the Server

Start the development server using `uvicorn` with hot-reload enabled:
```bash
uvicorn app.main:app --reload
```

The application will be accessible at:
- **API URL**: [http://127.0.0.1:8000](http://127.0.0.1:8000)
- **Interactive Swagger Docs**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc alternative documentation**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

*Note: The SQLite database file (`sql_app.db`) will be auto-generated in the root directory when the server starts for the first time.*

---

## Core Features

- **Pydantic v2**: Type-safe settings management (`pydantic-settings`) and request validation.
- **SQLAlchemy 2.0**: Modern declarative mapping, database connections, and session management.
- **JWT Authentication**: OAuth2 compatible flows with access token creation (`python-jose`) and secure hashing (`bcrypt`).
- **Clean Structure**: Highly modular layout suitable for large projects with separate directories for API routers, models, schemas, and database CRUD repository logic.
