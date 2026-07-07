---
name: SQLite engine policy
description: SQLAlchemy pool_size/max_overflow must be omitted for SQLite
---

## Rule
When building a SQLAlchemy `create_engine` call, skip `pool_size` and `max_overflow` when the URL contains `sqlite`.

**Why:** SQLite uses internal single-threaded pool and raises `TypeError` if those args are passed.

**How to apply:** Detect `"sqlite" in database_url` and conditionally build kwargs. Also set `connect_args={"check_same_thread": False}` for SQLite only.
