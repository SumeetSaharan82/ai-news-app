---
name: JWT library policy
description: Use PyJWT not python-jose for JWT in this project
---

## Rule
Always use `PyJWT` for JWT signing/verification. Do not add `python-jose` or `python-jose[cryptography]`.

**Why:** `python-jose==3.3.0` is blocked by the Replit package firewall (403). PyJWT is the safe alternative.

**How to apply:** Import as `import jwt` and `from jwt.exceptions import InvalidTokenError`. `jwt.encode()` returns a plain `str` in PyJWT 2.x — no `.decode()` call needed.

**Fail-fast policy:** In `backend/core/auth.py`, if `DEBUG=False` and `SECRET_KEY` equals the known default string, the server raises `RuntimeError` at startup. This prevents accidental production deployment with a weak secret.
