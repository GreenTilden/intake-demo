"""Authentication — magic link (email-based, no passwords).

Flow:
1. Staff enters email → POST /auth/magic-link
2. System sends email with one-time login link
3. Staff clicks link → GET /auth/verify?token=xxx
4. System sets session cookie (JWT, httponly)
5. Subsequent requests include cookie automatically
"""
import secrets
from datetime import datetime, timedelta, timezone

from fastapi import Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Staff, MagicLink

# In production, replace with proper JWT. For now, simple token-in-cookie.
SESSION_COOKIE = "intake_session"
MAGIC_LINK_EXPIRY = timedelta(hours=24)


async def create_magic_link(email: str, db: AsyncSession) -> str | None:
    """Create a magic link token for the given staff email.

    Returns the token string, or None if email not found.
    """
    result = await db.execute(select(Staff).where(Staff.email == email, Staff.is_active == True))
    staff = result.scalar_one_or_none()
    if not staff:
        return None

    token = secrets.token_urlsafe(48)
    link = MagicLink(
        token=token,
        staff_id=staff.id,
        expires_at=datetime.now(timezone.utc) + MAGIC_LINK_EXPIRY,
    )
    db.add(link)
    await db.commit()
    return token


async def verify_magic_link(token: str, db: AsyncSession) -> Staff | None:
    """Verify a magic link token. Returns staff if valid, None if expired/used."""
    result = await db.execute(
        select(MagicLink).where(
            MagicLink.token == token,
            MagicLink.used == False,
            MagicLink.expires_at > datetime.now(timezone.utc),
        )
    )
    link = result.scalar_one_or_none()
    if not link:
        return None

    # Mark as used
    link.used = True
    await db.commit()

    # Get staff
    result = await db.execute(select(Staff).where(Staff.id == link.staff_id))
    return result.scalar_one_or_none()


async def get_current_staff(request: Request, db: AsyncSession = Depends(get_db)) -> Staff:
    """Dependency — get the currently authenticated staff member from session cookie."""
    staff_id = request.cookies.get(SESSION_COOKIE)
    if not staff_id:
        raise HTTPException(status_code=401, detail="Not authenticated")

    result = await db.execute(select(Staff).where(Staff.id == staff_id, Staff.is_active == True))
    staff = result.scalar_one_or_none()
    if not staff:
        raise HTTPException(status_code=401, detail="Session expired")
    return staff


async def get_optional_staff(request: Request, db: AsyncSession = Depends(get_db)) -> Staff | None:
    """Dependency — get current staff or None (for public endpoints)."""
    staff_id = request.cookies.get(SESSION_COOKIE)
    if not staff_id:
        return None
    result = await db.execute(select(Staff).where(Staff.id == staff_id, Staff.is_active == True))
    return result.scalar_one_or_none()
