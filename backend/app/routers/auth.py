"""Auth routes — magic link login, session management."""
from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.auth import (
    create_magic_link, verify_magic_link, get_current_staff, SESSION_COOKIE,
)
from app.models import Staff

router = APIRouter(tags=["auth"])


@router.post("/auth/magic-link")
async def request_magic_link(body: dict, db: AsyncSession = Depends(get_db)):
    """Send a magic link to the staff member's email."""
    email = body.get("email", "").strip().lower()
    if not email:
        raise HTTPException(400, "email is required")

    token = await create_magic_link(email, db)

    # Always return success (don't leak whether email exists)
    # In production, send email here. For now, return token for dev.
    result = {"message": "If that email is registered, a login link has been sent."}

    # DEV ONLY: include token in response for testing
    if token:
        result["_dev_token"] = token

    return result


@router.get("/auth/verify")
async def verify_token(token: str, response: Response, db: AsyncSession = Depends(get_db)):
    """Verify magic link token and set session cookie."""
    staff = await verify_magic_link(token, db)
    if not staff:
        raise HTTPException(401, "Invalid or expired link")

    response.set_cookie(
        key=SESSION_COOKIE,
        value=str(staff.id),
        httponly=True,
        samesite="lax",
        max_age=7 * 24 * 3600,  # 7 days
    )

    return {
        "id": str(staff.id),
        "name": staff.name,
        "email": staff.email,
        "role": staff.role,
    }


@router.get("/auth/me")
async def get_me(staff: Staff = Depends(get_current_staff)):
    """Get current authenticated staff member."""
    return {
        "id": str(staff.id),
        "name": staff.name,
        "email": staff.email,
        "role": staff.role,
        "areas": staff.areas or [],
    }


@router.post("/auth/logout")
async def logout(response: Response):
    """Clear session cookie."""
    response.delete_cookie(SESSION_COOKIE)
    return {"message": "Logged out"}
