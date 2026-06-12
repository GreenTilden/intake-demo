"""Dashboard — metrics, queue depth, intake statistics."""
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Intake, Staff, Category
from app.auth import get_current_staff

router = APIRouter(tags=["dashboard"])


@router.get("/dashboard")
async def get_dashboard(
    db: AsyncSession = Depends(get_db),
    _: Staff = Depends(get_current_staff),
):
    now = datetime.now(timezone.utc)
    thirty_days_ago = now - timedelta(days=30)
    seven_days_ago = now - timedelta(days=7)

    # Status counts
    status_q = (
        select(Intake.status, func.count())
        .group_by(Intake.status)
    )
    by_status = {row[0]: row[1] for row in (await db.execute(status_q)).all()}

    # Source counts (letter vs web vs phone etc)
    source_q = (
        select(Intake.source, func.count())
        .group_by(Intake.source)
    )
    by_source = {row[0]: row[1] for row in (await db.execute(source_q)).all()}

    # Category counts
    cat_q = (
        select(Intake.category_id, func.count())
        .group_by(Intake.category_id)
    )
    by_category = {(row[0] or "uncategorized"): row[1] for row in (await db.execute(cat_q)).all()}

    # Recent volume (last 30 days)
    recent_q = select(func.count()).where(Intake.created_at >= thirty_days_ago)
    last_30 = (await db.execute(recent_q)).scalar() or 0

    weekly_q = select(func.count()).where(Intake.created_at >= seven_days_ago)
    last_7 = (await db.execute(weekly_q)).scalar() or 0

    # Open queue depth
    open_count = sum(by_status.get(s, 0) for s in ("new", "reviewed", "assigned", "in_progress"))

    # Staff caseloads
    caseload_q = (
        select(Staff.name, func.count())
        .join(Intake, Intake.assigned_to == Staff.id)
        .where(Intake.status.notin_(["resolved", "closed"]))
        .group_by(Staff.name)
    )
    caseloads = {row[0]: row[1] for row in (await db.execute(caseload_q)).all()}

    # Avg time to resolution (last 30 days)
    resolved_q = (
        select(func.avg(
            func.extract("epoch", Intake.resolved_at) - func.extract("epoch", Intake.created_at)
        ))
        .where(Intake.resolved_at.isnot(None))
        .where(Intake.resolved_at >= thirty_days_ago)
    )
    avg_resolution_secs = (await db.execute(resolved_q)).scalar()
    avg_resolution_days = round(avg_resolution_secs / 86400, 1) if avg_resolution_secs else None

    total_q = select(func.count()).select_from(Intake)
    total = (await db.execute(total_q)).scalar() or 0

    return {
        "total": total,
        "openQueue": open_count,
        "last30Days": last_30,
        "last7Days": last_7,
        "avgResolutionDays": avg_resolution_days,
        "byStatus": by_status,
        "bySource": by_source,
        "byCategory": by_category,
        "caseloads": caseloads,
    }
