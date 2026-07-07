---
name: python-jose blocked by Replit firewall
description: python-jose==3.3.0 is blocked by the Replit package firewall; PyJWT is the replacement
---

## Rule
Do not attempt to install `python-jose` or `python-jose[cryptography]` — Replit's package firewall returns 403.

**Why:** The package is flagged by Replit's security registry.

**How to apply:** Use `PyJWT` instead. The API is similar but not identical:
- Import: `import jwt` and `from jwt.exceptions import InvalidTokenError`
- `jwt.encode(payload, secret, algorithm="HS256")` — returns `str` in PyJWT 2.x (no `.decode()` needed)
- `jwt.decode(token, secret, algorithms=["HS256"])` — same as jose
- `backend/core/auth.py` has already been updated to use PyJWT
- `requirements.txt` has `PyJWT==2.8.0` (replacing `python-jose[cryptography]==3.3.0`)
