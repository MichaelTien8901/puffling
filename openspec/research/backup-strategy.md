# Backup & Data Security Research Report

**Date:** 2026-02-17
**Status:** Research — not planned for implementation
**Related:** [user-management.md](user-management.md)

## Data Inventory

### Database (Primary Store)

**Location:** `puffling.db` (SQLite with WAL mode)
**Files:** `puffling.db`, `puffling.db-shm`, `puffling.db-wal` — all three required for integrity

| Table | Sensitivity | Notes |
|-------|-------------|-------|
| `trade_history` | **CRITICAL** | Executed trades — non-recoverable, needed for tax/audit |
| `ai_conversations` | **CRITICAL** | LLM chat history — may contain sensitive decisions |
| `strategy_configs` | HIGH | Custom strategy parameters |
| `backtest_results` | HIGH | Performance metrics |
| `optimization_jobs` | HIGH | Parameter search results |
| `portfolio_goals` | HIGH | Asset allocation targets |
| `live_adaptation_configs` | HIGH | Live parameter tuning |
| `adaptation_events` | HIGH | Parameter change history |
| `agent_logs` | HIGH | AI agent execution reports |
| `scheduled_jobs` | Medium | Cron task configs |
| `alert_configs` | Medium | Alert rules |
| `alert_history` | Medium | Alert trigger logs |
| `settings` | Medium | User preferences (JSON) |
| `watchlists` | Low | Saved symbol lists |
| `users` | Low | User profiles |

### Secrets & Credentials

| Secret | Location | Risk if Leaked |
|--------|----------|----------------|
| Alpaca API key & secret | `.env` / env vars | Unauthorized trading |
| IBKR host/port/client ID | `.env` / env vars | Unauthorized connection |
| Future: DB credentials (PostgreSQL) | `.env` / env vars | Full data breach |
| Future: JWT signing key | `.env` / env vars | Auth bypass |
| Future: SMTP/email credentials | `.env` / env vars | Spam/phishing |

**Current state:** `.env` is gitignored. Credentials exist only on host or in container environment — no centralized secret management.

## Backup Tiers

### Tier 1 — CRITICAL (daily)

| Item | Size | Notes |
|------|------|-------|
| `puffling.db` + `-shm` + `-wal` | ~1.2 MB | Must backup all 3 files together |
| `.env` | <1 KB | Encrypted separately from DB |

### Tier 2 — HIGH (on change / weekly)

| Item | Size | Notes |
|------|------|-------|
| Source code (`backend/`, `frontend/`) | ~5 MB | Already in git |
| `openspec/` | ~100 KB | Design decisions |
| `pyproject.toml`, `docker-compose.yml` | <10 KB | Infrastructure definition |

### Skip (regenerable)

| Item | Size | Why |
|------|------|-----|
| `node_modules/` | 517 MB | `npm ci` from lock file |
| `.next/` | 24 KB | `npm run build` |
| `__pycache__/` | ~100 KB | Python bytecode |
| `test.db` | 140 KB | Test-only data |

## Backup Strategies

### Option A: Local Encrypted Backup (simplest)

**How:** Cron script using SQLite `.backup` API + GPG encryption + local/external drive.

```bash
#!/bin/bash
# backup-puffling.sh
BACKUP_DIR="/path/to/backups"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/puffling_$DATE.tar.gz.gpg"

# Safe SQLite backup (handles WAL correctly)
sqlite3 puffling.db ".backup '$BACKUP_DIR/puffling_snapshot.db'"

# Bundle DB + env + source
tar czf - puffling_snapshot.db .env | \
  gpg --symmetric --cipher-algo AES256 -o "$BACKUP_FILE"

rm "$BACKUP_DIR/puffling_snapshot.db"

# Retain last 30 days
find "$BACKUP_DIR" -name "puffling_*.tar.gz.gpg" -mtime +30 -delete
```

**Pros:** Zero cloud dependency, GPG encryption at rest, simple restore.
**Cons:** No off-site protection, manual setup.

### Option B: Cloud Storage (S3 / GCS / B2)

**How:** Same local backup script + upload to encrypted cloud bucket.

```bash
# After creating local backup...
aws s3 cp "$BACKUP_FILE" s3://puffling-backups/ --storage-class STANDARD_IA
# or
b2 upload-file puffling-backups "$BACKUP_FILE" "backups/$DATE.tar.gz.gpg"
```

**Pros:** Off-site, durable, versioned.
**Cons:** Cloud account required, egress costs, credential management.
**Cost:** ~$0.01/month for 1 GB on S3 Glacier or Backblaze B2.

### Option C: Git-Based DB Backup (lightweight)

**How:** Separate private git repo for database snapshots.

```bash
sqlite3 puffling.db ".backup backup-repo/puffling.db"
cd backup-repo
git add puffling.db
git commit -m "backup $(date +%Y-%m-%d)"
git push origin main
```

**Pros:** Versioned history, easy diff of schema, free on private GitHub/GitLab.
**Cons:** Not suitable for large DBs, binary diffs inefficient, secrets must NOT go here.

### Option D: Docker Volume Backup (if migrated to PostgreSQL)

**How:** `pg_dump` with encryption, scheduled via cron or Docker healthcheck.

```bash
docker exec puffling-db pg_dump -U puffling puffling | \
  gpg --symmetric --cipher-algo AES256 -o "$BACKUP_FILE"
```

**Pros:** Native PostgreSQL tooling, supports point-in-time recovery with WAL archiving.
**Cons:** Only applicable after PostgreSQL migration.

## Security Requirements

### Encryption

| Layer | Requirement | Tool |
|-------|-------------|------|
| At rest (backup files) | AES-256 encryption | GPG symmetric or age |
| At rest (secrets) | Separate from DB backup | GPG or vault |
| In transit (cloud upload) | TLS | HTTPS (default for S3/GCS/B2) |
| In transit (DB connection) | TLS | PostgreSQL SSL (future) |

### Access Control

| Concern | Mitigation |
|---------|------------|
| Backup files readable by others | `chmod 600` on all backup files |
| `.env` in plaintext | Encrypt separately, `chmod 600` |
| Cloud bucket public access | Bucket policy: private only, IAM scoped |
| Backup encryption key | Store separately from backups (password manager, hardware key) |
| Restore access | Only admin role (when multi-user) |

### Secrets Management (current vs future)

| Stage | Approach |
|-------|----------|
| **Now (single-user)** | `.env` file on host, gitignored, `chmod 600` |
| **Future (multi-user)** | Docker secrets or HashiCorp Vault, injected at runtime |
| **Production** | Cloud KMS (AWS KMS / GCP KMS) for encryption keys |

## SQLite Backup Considerations

SQLite with WAL mode requires special care:

1. **Never copy `puffling.db` while the app is running** — the WAL file may have uncommitted transactions
2. **Use `sqlite3 .backup` command** — this creates a consistent snapshot
3. **Or use `VACUUM INTO`** — creates a compacted copy: `sqlite3 puffling.db "VACUUM INTO 'backup.db'"`
4. **All 3 files together** — if copying raw files, stop the app first and copy `.db`, `.db-shm`, `.db-wal` as a set

## Restore Procedure

```bash
# 1. Stop services
docker compose down

# 2. Decrypt backup
gpg --decrypt puffling_20260217.tar.gz.gpg | tar xzf -

# 3. Replace database
cp puffling_snapshot.db puffling.db
rm -f puffling.db-shm puffling.db-wal  # Clean WAL state

# 4. Restore secrets
cp .env.backup .env
chmod 600 .env

# 5. Restart
docker compose up -d backend frontend
```

## Recommended Backup Schedule

| Data | Frequency | Retention | Method |
|------|-----------|-----------|--------|
| Database (`puffling.db`) | Daily | 30 days rolling | Option A (local encrypted) |
| Database (off-site) | Weekly | 90 days | Option B (cloud) or C (git) |
| Secrets (`.env`) | On change | Permanent | Password manager or encrypted vault |
| Source code | Every commit | Permanent | git (already done) |
| Full snapshot | Monthly | 12 months | Option B (cloud) |

## Recommendation

Start with **Option A (local encrypted backup)** via a cron script. It's zero-cost, handles the current SQLite setup safely, and provides daily encrypted snapshots. Add **Option B (cloud)** for off-site redundancy when the app holds real trading data. Migrate to **Option D (PostgreSQL pg_dump)** when multi-user support is implemented.

Total backup size: ~15–20 MB (database + secrets + source, excluding regenerable artifacts).
