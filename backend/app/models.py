"""SQLAlchemy models for the intake tracking system."""
import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    Column, String, Text, DateTime, Boolean, Integer, ForeignKey, Enum, Index,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import DeclarativeBase, relationship


def utcnow():
    return datetime.now(timezone.utc)


def new_id():
    return uuid.uuid4()


class Base(DeclarativeBase):
    pass


# ── Roles & Auth ──────────────────────────────────────────────

class Staff(Base):
    __tablename__ = "staff"

    id = Column(UUID(as_uuid=True), primary_key=True, default=new_id)
    email = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    role = Column(
        Enum("volunteer", "staff", "attorney", "admin", name="staff_role"),
        nullable=False,
        default="volunteer",
    )
    is_active = Column(Boolean, default=True)
    areas = Column(JSONB, default=list)  # list of category slugs they handle
    created_at = Column(DateTime(timezone=True), default=utcnow)

    # relationships
    intakes_created = relationship("Intake", back_populates="created_by_staff", foreign_keys="Intake.created_by", lazy="selectin")
    assigned_intakes = relationship("Intake", back_populates="assigned_staff", foreign_keys="Intake.assigned_to", lazy="selectin")


class MagicLink(Base):
    __tablename__ = "magic_links"

    id = Column(UUID(as_uuid=True), primary_key=True, default=new_id)
    token = Column(String(128), unique=True, nullable=False, index=True)
    staff_id = Column(UUID(as_uuid=True), ForeignKey("staff.id"), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    used = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), default=utcnow)


# ── Categories ────────────────────────────────────────────────

class Category(Base):
    __tablename__ = "categories"

    id = Column(String(50), primary_key=True)  # slug: "govt-surveillance", "housing", etc.
    label = Column(String(100), nullable=False)
    description = Column(Text, default="")
    sort_order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)


# ── Intake Requests ───────────────────────────────────────────

class Intake(Base):
    __tablename__ = "intakes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=new_id)

    # complainant info
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    phone = Column(String(30), default="")
    email = Column(String(255), default="")
    preferred_contact = Column(String(20), default="phone")  # phone, email, mail
    address = Column(Text, default="")
    state = Column(String(2), default="")

    # intake details
    source = Column(
        Enum("letter", "web", "email", "phone", "walk_in", name="intake_source"),
        default="web",
    )
    category_id = Column(String(50), ForeignKey("categories.id"), nullable=True)
    description = Column(Text, nullable=False)
    incident_date = Column(DateTime(timezone=True), nullable=True)
    urgency = Column(
        Enum("low", "normal", "high", "critical", name="urgency_level"),
        default="normal",
    )

    # workflow
    status = Column(
        Enum("new", "reviewed", "assigned", "in_progress", "resolved", "closed",
             name="intake_status"),
        default="new",
        index=True,
    )
    assigned_to = Column(UUID(as_uuid=True), ForeignKey("staff.id"), nullable=True)
    created_by = Column(UUID(as_uuid=True), ForeignKey("staff.id"), nullable=True)
    resolution = Column(Text, default="")

    # metadata
    metadata_ = Column("metadata", JSONB, default=dict)  # flexible extra fields
    created_at = Column(DateTime(timezone=True), default=utcnow, index=True)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)
    resolved_at = Column(DateTime(timezone=True), nullable=True)

    # relationships
    category = relationship("Category", lazy="selectin")
    assigned_staff = relationship("Staff", back_populates="assigned_intakes", foreign_keys=[assigned_to], lazy="selectin")
    created_by_staff = relationship("Staff", back_populates="intakes_created", foreign_keys=[created_by], lazy="selectin")
    notes = relationship("Note", back_populates="intake", order_by="Note.created_at", lazy="selectin")
    attachments = relationship("Attachment", back_populates="intake", lazy="selectin")

    __table_args__ = (
        Index("ix_intakes_status_created", "status", "created_at"),
        Index("ix_intakes_category", "category_id"),
    )


# ── Notes ─────────────────────────────────────────────────────

class Note(Base):
    __tablename__ = "notes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=new_id)
    intake_id = Column(UUID(as_uuid=True), ForeignKey("intakes.id"), nullable=False, index=True)
    author_id = Column(UUID(as_uuid=True), ForeignKey("staff.id"), nullable=False)
    text = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utcnow)

    intake = relationship("Intake", back_populates="notes", lazy="selectin")
    author = relationship("Staff", lazy="selectin")


# ── Attachments ───────────────────────────────────────────────

class Attachment(Base):
    __tablename__ = "attachments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=new_id)
    intake_id = Column(UUID(as_uuid=True), ForeignKey("intakes.id"), nullable=False, index=True)
    filename = Column(String(255), nullable=False)
    content_type = Column(String(100), default="application/octet-stream")
    size_bytes = Column(Integer, default=0)
    storage_path = Column(String(500), nullable=False)  # local file path
    extracted_text = Column(Text, default="")  # OCR output for scanned letters
    ocr_status = Column(
        Enum("pending", "complete", "failed", "skipped", name="ocr_status"),
        default="pending",
    )
    uploaded_by = Column(UUID(as_uuid=True), ForeignKey("staff.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), default=utcnow)

    intake = relationship("Intake", back_populates="attachments", lazy="selectin")
    uploader = relationship("Staff", lazy="selectin")


# ── Audit Log ─────────────────────────────────────────────────

class AuditLog(Base):
    __tablename__ = "audit_log"

    id = Column(UUID(as_uuid=True), primary_key=True, default=new_id)
    staff_id = Column(UUID(as_uuid=True), ForeignKey("staff.id"), nullable=True)
    action = Column(String(50), nullable=False)  # create, update, view, delete, login
    entity_type = Column(String(50), nullable=False)  # intake, note, staff
    entity_id = Column(String(50), nullable=True)
    details = Column(JSONB, default=dict)
    ip_address = Column(String(45), default="")
    created_at = Column(DateTime(timezone=True), default=utcnow, index=True)

    staff = relationship("Staff", lazy="selectin")
