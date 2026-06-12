"""Intake request management — web form + scanned letter OCR.

Two intake paths:
1. Web form: POST /intakes with JSON body
2. Scanned letter: POST /intakes/scan with file upload → OCR → draft intake
"""
import os
import uuid
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Form
from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models import Intake, Note, Attachment, Staff, AuditLog
from app.auth import get_current_staff
from app.services.ocr import extract_text, is_supported

router = APIRouter(tags=["intakes"])

UPLOAD_DIR = os.environ.get("UPLOAD_DIR", "/opt/intake/uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)


# ── List / Search ─────────────────────────────────────────────

@router.get("/intakes")
async def list_intakes(
    status: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    urgency: Optional[str] = Query(None),
    source: Optional[str] = Query(None),
    assigned_to: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    limit: int = Query(50, le=200),
    offset: int = Query(0),
    db: AsyncSession = Depends(get_db),
    staff: Staff = Depends(get_current_staff),
):
    q = select(Intake).options(
        selectinload(Intake.category),
        selectinload(Intake.assigned_staff),
    )

    if status:
        q = q.where(Intake.status == status)
    if category:
        q = q.where(Intake.category_id == category)
    if urgency:
        q = q.where(Intake.urgency == urgency)
    if source:
        q = q.where(Intake.source == source)
    if assigned_to:
        q = q.where(Intake.assigned_to == assigned_to)
    if search:
        pattern = f"%{search}%"
        q = q.where(
            Intake.description.ilike(pattern)
            | Intake.first_name.ilike(pattern)
            | Intake.last_name.ilike(pattern)
        )

    # Count before pagination
    count_q = select(func.count()).select_from(q.subquery())
    total = (await db.execute(count_q)).scalar()

    q = q.order_by(desc(Intake.created_at)).offset(offset).limit(limit)
    result = await db.execute(q)
    intakes = result.scalars().all()

    return {
        "intakes": [_serialize_intake(i) for i in intakes],
        "total": total,
        "limit": limit,
        "offset": offset,
    }


# ── Get One ───────────────────────────────────────────────────

@router.get("/intakes/{intake_id}")
async def get_intake(
    intake_id: str,
    db: AsyncSession = Depends(get_db),
    staff: Staff = Depends(get_current_staff),
):
    result = await db.execute(
        select(Intake)
        .options(
            selectinload(Intake.category),
            selectinload(Intake.assigned_staff),
            selectinload(Intake.created_by_staff),
            selectinload(Intake.notes).selectinload(Note.author),
            selectinload(Intake.attachments),
        )
        .where(Intake.id == intake_id)
    )
    intake = result.scalar_one_or_none()
    if not intake:
        raise HTTPException(404, "Intake not found")

    data = _serialize_intake(intake)
    data["notes"] = [
        {
            "id": str(n.id),
            "text": n.text,
            "author": n.author.name if n.author else None,
            "createdAt": n.created_at.isoformat(),
        }
        for n in intake.notes
    ]
    data["attachments"] = [
        {
            "id": str(a.id),
            "filename": a.filename,
            "contentType": a.content_type,
            "sizeBytes": a.size_bytes,
            "extractedText": a.extracted_text or "",
            "ocrStatus": a.ocr_status,
            "createdAt": a.created_at.isoformat(),
        }
        for a in intake.attachments
    ]
    return data


# ── Create (Web Form) ────────────────────────────────────────

@router.post("/intakes", status_code=201)
async def create_intake(
    body: dict,
    db: AsyncSession = Depends(get_db),
    staff: Staff = Depends(get_current_staff),
):
    if not body.get("firstName") or not body.get("lastName"):
        raise HTTPException(400, "firstName and lastName are required")
    if not body.get("description"):
        raise HTTPException(400, "description is required")

    intake = Intake(
        first_name=body["firstName"],
        last_name=body["lastName"],
        phone=body.get("phone", ""),
        email=body.get("email", ""),
        preferred_contact=body.get("preferredContact", "phone"),
        address=body.get("address", ""),
        state=body.get("state", ""),
        source=body.get("source", "web"),
        category_id=body.get("category") or None,
        description=body["description"],
        urgency=body.get("urgency", "normal"),
        created_by=staff.id,
    )
    db.add(intake)

    # Audit
    db.add(AuditLog(
        staff_id=staff.id,
        action="create",
        entity_type="intake",
        entity_id=str(intake.id),
    ))

    await db.commit()
    await db.refresh(intake)
    return _serialize_intake(intake)


# ── Scan & OCR (Letter Upload) ───────────────────────────────

@router.post("/intakes/scan", status_code=201)
async def scan_intake(
    file: UploadFile = File(...),
    first_name: str = Form(default=""),
    last_name: str = Form(default=""),
    category: str = Form(default=""),
    db: AsyncSession = Depends(get_db),
    staff: Staff = Depends(get_current_staff),
):
    """Upload a scanned letter/PDF. OCR extracts text, creates draft intake."""
    if not is_supported(file.filename or ""):
        raise HTTPException(400, f"Unsupported file type. Supported: PDF, JPG, PNG, TIFF")

    # Save file
    file_id = str(uuid.uuid4())
    ext = os.path.splitext(file.filename or "upload")[1]
    storage_path = os.path.join(UPLOAD_DIR, f"{file_id}{ext}")

    content = await file.read()
    with open(storage_path, "wb") as f:
        f.write(content)

    # OCR
    ocr_status = "complete"
    extracted = ""
    try:
        extracted = extract_text(storage_path)
    except Exception:
        ocr_status = "failed"

    # Create intake with OCR text as description
    intake = Intake(
        first_name=first_name or "Unknown",
        last_name=last_name or "Unknown",
        source="letter",
        category_id=category or None,
        description=extracted or "[OCR failed — review scanned document]",
        status="new",
        created_by=staff.id,
    )
    db.add(intake)
    await db.flush()  # get intake.id

    # Create attachment linked to intake
    attachment = Attachment(
        intake_id=intake.id,
        filename=file.filename or f"scan{ext}",
        content_type=file.content_type or "application/octet-stream",
        size_bytes=len(content),
        storage_path=storage_path,
        extracted_text=extracted,
        ocr_status=ocr_status,
        uploaded_by=staff.id,
    )
    db.add(attachment)

    db.add(AuditLog(
        staff_id=staff.id,
        action="scan",
        entity_type="intake",
        entity_id=str(intake.id),
        details={"ocrStatus": ocr_status, "filename": file.filename},
    ))

    await db.commit()
    await db.refresh(intake)

    result = _serialize_intake(intake)
    result["extractedText"] = extracted
    result["ocrStatus"] = ocr_status
    return result


# ── Update ────────────────────────────────────────────────────

@router.put("/intakes/{intake_id}")
async def update_intake(
    intake_id: str,
    body: dict,
    db: AsyncSession = Depends(get_db),
    staff: Staff = Depends(get_current_staff),
):
    result = await db.execute(select(Intake).where(Intake.id == intake_id))
    intake = result.scalar_one_or_none()
    if not intake:
        raise HTTPException(404, "Intake not found")

    updatable = {
        "firstName": "first_name",
        "lastName": "last_name",
        "phone": "phone",
        "email": "email",
        "preferredContact": "preferred_contact",
        "address": "address",
        "state": "state",
        "category": "category_id",
        "description": "description",
        "urgency": "urgency",
        "status": "status",
        "assignedTo": "assigned_to",
        "resolution": "resolution",
    }

    changes = {}
    for json_key, model_key in updatable.items():
        if json_key in body:
            old = getattr(intake, model_key)
            new = body[json_key] or None if model_key in ("category_id", "assigned_to") else body[json_key]
            if old != new:
                setattr(intake, model_key, new)
                changes[json_key] = {"from": str(old), "to": str(new)}

    if "status" in body and body["status"] in ("resolved", "closed"):
        intake.resolved_at = datetime.now(timezone.utc)

    intake.updated_at = datetime.now(timezone.utc)

    db.add(AuditLog(
        staff_id=staff.id,
        action="update",
        entity_type="intake",
        entity_id=str(intake.id),
        details=changes,
    ))

    await db.commit()
    await db.refresh(intake)
    return _serialize_intake(intake)


# ── Add Note ──────────────────────────────────────────────────

@router.post("/intakes/{intake_id}/notes", status_code=201)
async def add_note(
    intake_id: str,
    body: dict,
    db: AsyncSession = Depends(get_db),
    staff: Staff = Depends(get_current_staff),
):
    result = await db.execute(select(Intake).where(Intake.id == intake_id))
    if not result.scalar_one_or_none():
        raise HTTPException(404, "Intake not found")

    if not body.get("text"):
        raise HTTPException(400, "text is required")

    note = Note(
        intake_id=intake_id,
        author_id=staff.id,
        text=body["text"],
    )
    db.add(note)
    await db.commit()
    await db.refresh(note)

    return {
        "id": str(note.id),
        "text": note.text,
        "author": staff.name,
        "createdAt": note.created_at.isoformat(),
    }


# ── Upload Attachment ─────────────────────────────────────────

@router.post("/intakes/{intake_id}/attachments", status_code=201)
async def upload_attachment(
    intake_id: str,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    staff: Staff = Depends(get_current_staff),
):
    result = await db.execute(select(Intake).where(Intake.id == intake_id))
    if not result.scalar_one_or_none():
        raise HTTPException(404, "Intake not found")

    file_id = str(uuid.uuid4())
    ext = os.path.splitext(file.filename or "upload")[1]
    storage_path = os.path.join(UPLOAD_DIR, f"{file_id}{ext}")

    content = await file.read()
    with open(storage_path, "wb") as f:
        f.write(content)

    # OCR if it's a scannable document
    extracted = ""
    ocr_status = "skipped"
    if is_supported(file.filename or ""):
        try:
            extracted = extract_text(storage_path)
            ocr_status = "complete"
        except Exception:
            ocr_status = "failed"

    attachment = Attachment(
        intake_id=intake_id,
        filename=file.filename or f"upload{ext}",
        content_type=file.content_type or "application/octet-stream",
        size_bytes=len(content),
        storage_path=storage_path,
        extracted_text=extracted,
        ocr_status=ocr_status,
        uploaded_by=staff.id,
    )
    db.add(attachment)
    await db.commit()
    await db.refresh(attachment)

    return {
        "id": str(attachment.id),
        "filename": attachment.filename,
        "sizeBytes": attachment.size_bytes,
        "extractedText": extracted,
        "ocrStatus": ocr_status,
    }


# ── Helpers ───────────────────────────────────────────────────

def _serialize_intake(i: Intake) -> dict:
    return {
        "id": str(i.id),
        "firstName": i.first_name,
        "lastName": i.last_name,
        "phone": i.phone,
        "email": i.email,
        "preferredContact": i.preferred_contact,
        "address": i.address,
        "state": i.state,
        "source": i.source,
        "category": i.category_id,
        "categoryLabel": i.category.label if i.category else None,
        "description": i.description,
        "urgency": i.urgency,
        "status": i.status,
        "assignedTo": str(i.assigned_to) if i.assigned_to else None,
        "assignedName": i.assigned_staff.name if i.assigned_staff else None,
        "createdBy": str(i.created_by) if i.created_by else None,
        "createdByName": i.created_by_staff.name if i.created_by_staff else None,
        "resolution": i.resolution,
        "createdAt": i.created_at.isoformat(),
        "updatedAt": i.updated_at.isoformat() if i.updated_at else None,
        "resolvedAt": i.resolved_at.isoformat() if i.resolved_at else None,
    }
