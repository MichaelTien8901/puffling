# User Management Research Report

**Date:** 2026-02-17
**Status:** Research — not planned for implementation
**Decision:** Keep current single-user system
**Related:** [backup-strategy.md](backup-strategy.md)

## Current State

Puffling is a single-user personal app. A `User` model exists with `user_id` on all tables, but the user is auto-provisioned (no auth, no login, no roles). This was an intentional design choice for future multi-user extensibility without current overhead.

## Proposed Feature

Add full user management with:
- Role-based access: **administrator** and **user** roles
- Admin can manage users and all settings
- User signup with email validation for new accounts/passwords

## Scope Assessment

### 1. Authentication System
- Password hashing (bcrypt/argon2)
- JWT or session-based tokens
- Login/logout REST endpoints
- Token refresh mechanism
- Secure cookie or bearer token transport

### 2. Role & Permission Model
- `Role` model (admin, user) linked to `User`
- Permission middleware on all existing routes
- Admin-only routes: user CRUD, global settings, kill switch
- User routes: own strategies, backtests, trades, AI chat

### 3. User Signup & Email Validation
- Registration endpoint (`POST /api/auth/signup`)
- Email verification token generation
- SMTP or third-party email service (SendGrid, AWS SES, etc.)
- Email templates for verification and password reset
- Account activation flow

### 4. Password Management
- Secure password reset flow (token-based, time-limited)
- Password change endpoint for authenticated users
- Password strength validation

### 5. Admin Panel
- User list with role assignment
- Enable/disable user accounts
- View and manage all users' strategies, trades, settings
- System-wide settings management

### 6. Backend Changes
- Auth middleware on **all existing routes** (breaking change)
- New `backend/api/routes/auth.py` — login, signup, verify, reset
- New `backend/services/auth_service.py` — token management, password hashing
- New `backend/models/role.py` — role model and user-role association
- Update `backend/core/deps.py` — role-based dependency injection
- Database migration for roles table and user schema changes

### 7. Frontend Changes
- Login page
- Signup page with email verification flow
- Password reset page
- Admin user management page
- Auth context/provider wrapping all pages
- Protected route wrapper
- Token storage and refresh logic

### 8. Infrastructure Requirements
- Email service (SMTP server or cloud email API)
- Environment config for email credentials
- Potentially a background task queue for sending emails

## Impact Analysis

- **High effort:** Touches nearly every existing route and requires new infrastructure
- **Breaking change:** All existing API consumers need auth tokens
- **New dependency:** Email delivery service
- **Estimated scope:** Largest single feature addition to Puffling

## Database Migration Path (SQLite → Production DB)

If multi-user is needed, the database must migrate from SQLite to PostgreSQL (or MySQL). Below is the current state and migration plan.

### Current Database State

- **Engine:** SQLite (`sqlite:///./puffling.db`), configurable via `PUFFLING_DATABASE_URL`
- **Schema management:** `Base.metadata.create_all()` — no versioned migrations
- **SQLite-specific:** WAL journal mode enabled, foreign keys enforced via PRAGMA
- **Alembic:** Not installed, no migration scripts exist
- **Docker:** No database service defined — backend uses local SQLite file

### Tables (15 across 14 model files)

| Table | Model File | Key Fields |
|-------|-----------|------------|
| `users` | user.py | id, name |
| `settings` | settings.py | user_id, key, value (JSON) |
| `strategy_configs` | strategy_config.py | user_id, strategy params |
| `backtest_results` | backtest_result.py | user_id, metrics |
| `watchlists` | watchlist.py | user_id, symbols (JSON) |
| `ai_conversations` | ai_conversation.py | user_id, messages (JSON) |
| `scheduled_jobs` | scheduled_job.py | user_id, job config |
| `portfolio_goals` | portfolio_goal.py | user_id, targets |
| `alert_configs` | alert_config.py | user_id, conditions |
| `alert_history` | alert_history.py | user_id, trigger events |
| `agent_logs` | agent_log.py | user_id, execution logs |
| `optimization_jobs` | optimization_job.py | user_id, job tracking |
| `trade_history` | trade_history.py | user_id, trade records |
| `live_adaptation_configs` | live_adaptation.py | user_id, adaptation config |
| `adaptation_events` | live_adaptation.py | config_id, event log |

All 14 data tables already carry `user_id` with foreign key to `users.id` — multi-user scoping is already in the schema.

### Migration Steps

#### 1. Add Alembic (schema versioning)
- Add `alembic` to `pyproject.toml` dependencies
- Run `alembic init migrations` to create config
- Generate baseline migration from existing models
- All future schema changes go through `alembic revision --autogenerate`

#### 2. Update `backend/core/database.py`
- Remove SQLite-specific PRAGMA event listener (WAL, foreign keys)
- Use dialect detection: keep SQLite pragmas for dev, skip for PostgreSQL
- Configure connection pooling (`QueuePool` for PostgreSQL, `StaticPool` for SQLite tests)
- Add pool size, max overflow, and timeout settings

#### 3. Update `backend/core/config.py`
- Add connection pool settings (`pool_size`, `max_overflow`)
- Add optional SSL/TLS config for remote database connections
- Default remains SQLite for single-user/dev mode

#### 4. Update `docker-compose.yml`
- Add PostgreSQL service with persistent volume
- Backend service depends on database, uses `DATABASE_URL=postgresql://...`
- Add health check for database readiness

```yaml
# Example addition
services:
  db:
    image: postgres:16
    environment:
      POSTGRES_DB: puffling
      POSTGRES_USER: puffling
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - pgdata:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U puffling"]
```

#### 5. Data Migration (SQLite → PostgreSQL)
- Export existing SQLite data via `sqlite3 .dump` or SQLAlchemy bulk read
- Transform auto-provisioned default user to a proper admin account
- Import into PostgreSQL with constraints enforced
- Verify foreign key integrity post-migration

#### 6. User Model Changes (for auth)
- Add columns to `users`: `email`, `password_hash`, `role`, `is_active`, `email_verified`
- Alembic migration to alter existing table
- Backfill existing default user as admin role

### Database Option Comparison

| Factor | SQLite (current) | PostgreSQL | MySQL |
|--------|-----------------|------------|-------|
| Setup | Zero config | Docker service | Docker service |
| Concurrency | Single-writer | Full MVCC | Row-level locking |
| JSON support | Limited | Native JSONB | JSON type |
| Full-text search | FTS5 extension | Built-in tsvector | FULLTEXT index |
| Scaling | Single machine | Horizontal (replicas) | Horizontal (replicas) |
| Best for | Single-user/dev | Multi-user production | Multi-user production |

**Recommended production DB:** PostgreSQL — best JSON support (JSONB for stored params/metrics), mature ecosystem, strong SQLAlchemy support, free.

## Recommendation

Keep the current single-user system with SQLite. The existing `user_id` columns and environment-configurable `DATABASE_URL` provide a clean migration path when multi-user support becomes necessary. This feature should only be pursued when there is a concrete need to share or deploy Puffling as a multi-user service.
