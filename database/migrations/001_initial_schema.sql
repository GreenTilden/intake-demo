-- Northwind Legal - Intake System — Initial Schema
-- Run against PostgreSQL 16+

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Staff roles enum
CREATE TYPE staff_role AS ENUM ('volunteer', 'staff', 'attorney', 'admin');

-- Intake source enum
CREATE TYPE intake_source AS ENUM ('letter', 'web', 'email', 'phone', 'walk_in');

-- Urgency levels
CREATE TYPE urgency_level AS ENUM ('low', 'normal', 'high', 'critical');

-- Intake status workflow
CREATE TYPE intake_status AS ENUM ('new', 'reviewed', 'assigned', 'in_progress', 'resolved', 'closed');

-- OCR processing status
CREATE TYPE ocr_status AS ENUM ('pending', 'complete', 'failed', 'skipped');

-- ── Staff ────────────────────────────────────────────────────

CREATE TABLE staff (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    role staff_role NOT NULL DEFAULT 'volunteer',
    is_active BOOLEAN DEFAULT TRUE,
    areas JSONB DEFAULT '[]'::jsonb,
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX ix_staff_email ON staff(email);

-- ── Magic Links ──────────────────────────────────────────────

CREATE TABLE magic_links (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    token VARCHAR(128) UNIQUE NOT NULL,
    staff_id UUID NOT NULL REFERENCES staff(id),
    expires_at TIMESTAMPTZ NOT NULL,
    used BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX ix_magic_links_token ON magic_links(token);

-- ── Categories ───────────────────────────────────────────────

CREATE TABLE categories (
    id VARCHAR(50) PRIMARY KEY,
    label VARCHAR(100) NOT NULL,
    description TEXT DEFAULT '',
    sort_order INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE
);

-- ── Intakes ──────────────────────────────────────────────────

CREATE TABLE intakes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- Complainant
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    phone VARCHAR(30) DEFAULT '',
    email VARCHAR(255) DEFAULT '',
    preferred_contact VARCHAR(20) DEFAULT 'phone',
    address TEXT DEFAULT '',
    state VARCHAR(2) DEFAULT '',

    -- Details
    source intake_source DEFAULT 'web',
    category_id VARCHAR(50) REFERENCES categories(id),
    description TEXT NOT NULL,
    incident_date TIMESTAMPTZ,
    urgency urgency_level DEFAULT 'normal',

    -- Workflow
    status intake_status DEFAULT 'new',
    assigned_to UUID REFERENCES staff(id),
    created_by UUID REFERENCES staff(id),
    resolution TEXT DEFAULT '',

    -- Metadata
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now(),
    resolved_at TIMESTAMPTZ
);

CREATE INDEX ix_intakes_status_created ON intakes(status, created_at);
CREATE INDEX ix_intakes_category ON intakes(category_id);
CREATE INDEX ix_intakes_created_at ON intakes(created_at);

-- ── Notes ────────────────────────────────────────────────────

CREATE TABLE notes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    intake_id UUID NOT NULL REFERENCES intakes(id),
    author_id UUID NOT NULL REFERENCES staff(id),
    text TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX ix_notes_intake ON notes(intake_id);

-- ── Attachments ──────────────────────────────────────────────

CREATE TABLE attachments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    intake_id UUID NOT NULL REFERENCES intakes(id),
    filename VARCHAR(255) NOT NULL,
    content_type VARCHAR(100) DEFAULT 'application/octet-stream',
    size_bytes INTEGER DEFAULT 0,
    storage_path VARCHAR(500) NOT NULL,
    extracted_text TEXT DEFAULT '',
    ocr_status ocr_status DEFAULT 'pending',
    uploaded_by UUID REFERENCES staff(id),
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX ix_attachments_intake ON attachments(intake_id);

-- ── Audit Log ────────────────────────────────────────────────

CREATE TABLE audit_log (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    staff_id UUID REFERENCES staff(id),
    action VARCHAR(50) NOT NULL,
    entity_type VARCHAR(50) NOT NULL,
    entity_id VARCHAR(50),
    details JSONB DEFAULT '{}'::jsonb,
    ip_address VARCHAR(45) DEFAULT '',
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX ix_audit_log_created ON audit_log(created_at);

-- ── Seed default categories ──────────────────────────────────

INSERT INTO categories (id, label, sort_order) VALUES
    ('govt-surveillance', 'Government Surveillance / Gangstalking', 1),
    ('police-misconduct', 'Police Misconduct', 2),
    ('discrimination', 'Discrimination', 3),
    ('immigration', 'Immigration', 4),
    ('free-speech', 'Free Speech / First Amendment', 5),
    ('privacy', 'Privacy / Data Rights', 6),
    ('housing', 'Housing Discrimination', 7),
    ('voting', 'Voting Rights', 8),
    ('prisoners', 'Prisoners'' Rights', 9),
    ('other', 'Other', 99)
ON CONFLICT (id) DO NOTHING;
