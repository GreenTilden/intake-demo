"""Intake categories — seed defaults, list, manage."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Category, Staff
from app.auth import get_current_staff

router = APIRouter(tags=["categories"])

# Default categories for civil rights intake
DEFAULT_CATEGORIES = [
    {"id": "govt-surveillance", "label": "Government Surveillance / Gangstalking", "sort_order": 1},
    {"id": "police-misconduct", "label": "Police Misconduct", "sort_order": 2},
    {"id": "discrimination", "label": "Discrimination", "sort_order": 3},
    {"id": "immigration", "label": "Immigration", "sort_order": 4},
    {"id": "free-speech", "label": "Free Speech / First Amendment", "sort_order": 5},
    {"id": "privacy", "label": "Privacy / Data Rights", "sort_order": 6},
    {"id": "housing", "label": "Housing Discrimination", "sort_order": 7},
    {"id": "voting", "label": "Voting Rights", "sort_order": 8},
    {"id": "prisoners", "label": "Prisoners' Rights", "sort_order": 9},
    {"id": "other", "label": "Other", "sort_order": 99},
]


@router.get("/categories")
async def list_categories(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Category).where(Category.is_active == True).order_by(Category.sort_order)
    )
    cats = result.scalars().all()
    return {
        "categories": [
            {"id": c.id, "label": c.label, "description": c.description}
            for c in cats
        ]
    }


@router.post("/categories/seed", status_code=201)
async def seed_categories(db: AsyncSession = Depends(get_db)):
    """Seed default categories. Idempotent — skips existing."""
    existing = await db.execute(select(Category))
    if existing.scalars().all():
        return {"message": "Categories already seeded"}

    for cat in DEFAULT_CATEGORIES:
        db.add(Category(**cat))

    await db.commit()
    return {"message": "Seeded default categories", "count": len(DEFAULT_CATEGORIES)}
