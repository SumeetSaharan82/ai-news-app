"""
Server-side daily usage tracking and subscription management.
Provides enforceable rate limits independent of client state.
"""

import os
from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from datetime import datetime, date
from pydantic import BaseModel
from typing import Optional

from backend.core.database import get_db
from backend.core.user_models import User, UserPreferences
from backend.api.v1.auth import get_current_user

router = APIRouter()

# Internal webhook secret — must match X-Webhook-Secret header on tier-update calls
_WEBHOOK_SECRET = os.environ.get("WEBHOOK_SECRET", "")

FREE_DAILY_LIMIT = 15
TIER_LIMITS = {"free": FREE_DAILY_LIMIT, "pro": 999999, "premium": 999999}


def _today_key() -> str:
    return date.today().isoformat()


def _get_usage(user: User) -> dict:
    """Read today's usage count from user preferences JSON."""
    prefs = user.preferences or {}
    usage = prefs.get("_usage", {})
    today = _today_key()
    return {"date": today, "count": usage.get(today, 0)}


def _increment_usage(user: User, db: Session) -> int:
    """Atomically increment today's read count. Returns new count."""
    prefs = dict(user.preferences or {})
    usage = dict(prefs.get("_usage", {}))
    today = _today_key()
    # Purge stale dates (keep only today)
    usage = {today: usage.get(today, 0)}
    usage[today] += 1
    prefs["_usage"] = usage
    user.preferences = prefs
    db.commit()
    return usage[today]


@router.get("/usage/status")
async def get_usage_status(
    current_user: User = Depends(get_current_user),
):
    """Return the authenticated user's tier and today's read count."""
    prefs = UserPreferences.from_dict(current_user.preferences or {})
    usage = _get_usage(current_user)
    limit = TIER_LIMITS.get(prefs.tier, FREE_DAILY_LIMIT)
    return {
        "tier": prefs.tier,
        "daily_limit": limit,
        "reads_today": usage["count"],
        "remaining": max(0, limit - usage["count"]),
        "is_over_limit": usage["count"] >= limit,
    }


@router.post("/usage/record-read")
async def record_article_read(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Record one article read server-side.
    Returns 402 if the free daily limit is exceeded.
    """
    prefs = UserPreferences.from_dict(current_user.preferences or {})
    limit = TIER_LIMITS.get(prefs.tier, FREE_DAILY_LIMIT)
    current_count = _get_usage(current_user)["count"]

    if prefs.tier == "free" and current_count >= limit:
        raise HTTPException(
            status_code=402,
            detail={
                "code": "daily_limit_exceeded",
                "reads_today": current_count,
                "limit": limit,
                "tier": prefs.tier,
            },
        )

    new_count = _increment_usage(current_user, db)
    return {
        "reads_today": new_count,
        "remaining": max(0, limit - new_count),
        "tier": prefs.tier,
    }


class TierUpdate(BaseModel):
    user_email: str   # identify the user to upgrade
    tier: str         # free | pro | premium


@router.post("/usage/update-tier")
async def update_tier(
    body: TierUpdate,
    x_webhook_secret: Optional[str] = Header(None, alias="X-Webhook-Secret"),
    db: Session = Depends(get_db),
):
    """
    Update a user's subscription tier.
    INTERNAL USE ONLY — requires X-Webhook-Secret header matching WEBHOOK_SECRET env var.
    Call from your Stripe webhook handler after verifying the Stripe signature.
    End users cannot call this; it is NOT protected by user auth, only by the server secret.
    """
    if not _WEBHOOK_SECRET or x_webhook_secret != _WEBHOOK_SECRET:
        raise HTTPException(status_code=403, detail="Forbidden — invalid webhook secret")

    if body.tier not in ("free", "pro", "premium"):
        raise HTTPException(status_code=400, detail="Invalid tier")

    user = db.query(User).filter(User.email == body.user_email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    prefs = dict(user.preferences or {})
    prefs["tier"] = body.tier
    prefs["daily_limit"] = FREE_DAILY_LIMIT if body.tier == "free" else 999999
    user.preferences = prefs
    user.updated_at = datetime.utcnow()
    db.commit()
    return {"email": body.user_email, "tier": body.tier, "daily_limit": prefs["daily_limit"]}
