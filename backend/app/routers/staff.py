"""Staff management — list, create, update staff members."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Staff, Intake
from app.auth import get_current_staff

router = APIRouter(tags=["staff"])


@router.get("/staff")
async def list_staff(
    db: AsyncSession = Depends(get_db),
    _: Staff = Depends(get_current_staff),
):
    result = await db.execute(select(Staff).where(Staff.is_active == True).order_by(Staff.name))
    staff_list = result.scalars().all()

    # Get caseload counts
    counts_q = (
        select(Intake.assigned_to, func.count())
        .where(Intake.status.notin_(["resolved", "closed"]))
        .group_by(Intake.assigned_to)
    )
    counts = {str(row[0]): row[1] for row in (await db.execute(counts_q)).all()}

    return {
        "staff": [
            {
                "id": str(s.id),
                "name": s.name,
                "email": s.email,
                "role": s.role,
                "areas": s.areas or [],
                "activeCaseload": counts.get(str(s.id), 0),
            }
            for s in staff_list
        ]
    }


@router.post("/staff", status_code=201)
async def create_staff(
    body: dict,
    db: AsyncSession = Depends(get_db),
    current: Staff = Depends(get_current_staff),
):
    if current.role != "admin":
        raise HTTPException(403, "Admin access required")
    if not body.get("email") or not body.get("name"):
        raise HTTPException(400, "email and name are required")

    # Check duplicate
    existing = await db.execute(select(Staff).where(Staff.email == body["email"].lower()))
    if existing.scalar_one_or_none():
        raise HTTPException(409, "Staff with this email already exists")

    staff = Staff(
        email=body["email"].strip().lower(),
        name=body["name"].strip(),
        role=body.get("role", "volunteer"),
        areas=body.get("areas", []),
    )
    db.add(staff)
    await db.commit()
    await db.refresh(staff)

    return {
        "id": str(staff.id),
        "name": staff.name,
        "email": staff.email,
        "role": staff.role,
        "areas": staff.areas or [],
    }


@router.put("/staff/{staff_id}")
async def update_staff(
    staff_id: str,
    body: dict,
    db: AsyncSession = Depends(get_db),
    current: Staff = Depends(get_current_staff),
):
    if current.role != "admin":
        raise HTTPException(403, "Admin access required")

    result = await db.execute(select(Staff).where(Staff.id == staff_id))
    staff = result.scalar_one_or_none()
    if not staff:
        raise HTTPException(404, "Staff not found")

    for key in ("name", "role", "areas", "is_active"):
        json_key = key.replace("_", "")  # isActive → is_active handled below
        if key in body:
            setattr(staff, key, body[key])
    if "isActive" in body:
        staff.is_active = body["isActive"]

    await db.commit()
    await db.refresh(staff)

    return {
        "id": str(staff.id),
        "name": staff.name,
        "email": staff.email,
        "role": staff.role,
        "areas": staff.areas or [],
        "isActive": staff.is_active,
    }
