---
name: SQLite pool_size/max_overflow fix
description: SQLAlchemy rejects pool_size and max_overflow for SQLite; must be conditional
---

## Rule
When creating a SQLAlchemy engine, do not pass `pool_size` or `max_overflow` if the database URL contains `sqlite`.

**Why:** SQLite uses `StaticPool` or `NullPool` internally and raises `TypeError` if you pass connection pool sizing args.

**How to apply:** See `backend/core/database.py` — it checks `"sqlite" in settings.database_url` and only adds pool args for non-SQLite engines. Also sets `connect_args={"check_same_thread": False}` for SQLite.
