#!/usr/bin/env python3
"""
Deterministic synthetic-seed generator for the intake-demo clean room.

Emits  database/migrations/002_synthetic_seed.sql  — a static, reviewable SQL
file that loads via Postgres' /docker-entrypoint-initdb.d sequence (after
001_initial_schema.sql).  Re-running this generator with the same code yields
byte-identical SQL (fixed RNG seed + uuid5 ids), so the corpus is reproducible.

ALL DATA IS SYNTHETIC.  Fabricated firm: Northwind Legal Group
(@northwind-legal.local).  Complainant contacts use RFC-reserved example.com /
example.net domains, the 555-01xx reserved phone range, obviously-fake street
names, and RFC-5737 documentation IP ranges (203.0.113.0/24, 198.51.100.0/24).
No real people, orgs, addresses, hosts, or paths are referenced.

Usage:  python3 database/seed/generate_seed.py
"""
import json
import random
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

# ── Determinism anchors ───────────────────────────────────────────────
RNG = random.Random(20260611)
NS = uuid.UUID("0d9f1c00-0000-4000-8000-000000000000")  # fixed uuid5 namespace
TODAY = datetime(2026, 6, 11, 17, 0, 0, tzinfo=timezone.utc)  # demo "now"

_counter = {"n": 0}


def uid(label: str) -> str:
    return str(uuid.uuid5(NS, label))


def auto_uid(prefix: str) -> str:
    _counter["n"] += 1
    return uid(f"{prefix}:{_counter['n']}")


# ── SQL literal helpers ───────────────────────────────────────────────
def sq(s: str) -> str:
    return "'" + str(s).replace("'", "''") + "'"


def ts(dt: datetime) -> str:
    return "'" + dt.astimezone(timezone.utc).strftime("%Y-%m-%d %H:%M:%S") + "+00'"


def jb(d: dict) -> str:
    return "'" + json.dumps(d, separators=(",", ":")).replace("'", "''") + "'::jsonb"


def nullable_uuid(u):
    return sq(u) if u else "NULL"


# ── Staff (9) ─────────────────────────────────────────────────────────
# role ∈ {volunteer, staff, attorney, admin}
STAFF = [
    # (key, name, email-local, role, title, areas)
    ("dana", "Dana Whitfield", "dwhitfield", "admin", "Executive Director",
     ["govt-surveillance", "police-misconduct", "discrimination", "immigration",
      "free-speech", "privacy", "housing", "voting", "prisoners", "other"]),
    ("ray", "Raymond Castellanos", "rcastellanos", "attorney", "Legal Director",
     ["police-misconduct", "free-speech", "prisoners"]),
    ("priya", "Priya Anand", "panand", "attorney", "Senior Staff Attorney",
     ["discrimination", "housing", "voting"]),
    ("elena", "Elena Marquez", "emarquez", "attorney", "Immigration Attorney",
     ["immigration", "discrimination"]),
    ("theo", "Theodore Park", "tpark", "staff", "Intake Coordinator",
     ["govt-surveillance", "privacy", "other"]),
    ("wanda", "Wanda Pierce", "wpierce", "staff", "Paralegal",
     ["privacy", "voting", "free-speech"]),
    ("owen", "Owen Bradley", "obradley", "staff", "Case Manager",
     ["prisoners", "govt-surveillance", "housing"]),
    ("greta", "Greta Lindholm", "glindholm", "volunteer", "Intake Volunteer",
     ["other"]),
    ("sam", "Samuel Boateng", "sboateng", "volunteer", "Law Student Volunteer",
     ["immigration", "free-speech"]),
]
STAFF_ID = {key: uid(f"staff:{key}") for key, *_ in STAFF}

# Routing pools
ATTORNEYS = ["ray", "priya", "elena"]
TRIAGERS = ["theo", "wanda", "owen"]  # non-volunteer staff who log/triage
VOLUNTEERS = ["greta", "sam"]
ASSIGNABLE = ATTORNEYS + TRIAGERS  # never auto-assign cases to volunteers
AREAS_BY_STAFF = {key: areas for key, *_rest, areas in STAFF}


def area_match(category_id):
    pool = [k for k in ASSIGNABLE if category_id in AREAS_BY_STAFF[k]]
    return pool or ASSIGNABLE


# ── Categories (the 10 ids seeded by 001 — re-stated so 002 is self-sufficient) ──
# (id, label, sort_order, description) — label/sort_order mirror 001_initial_schema.
CATEGORY_ROWS = [
    ("govt-surveillance", "Government Surveillance / Gangstalking", 1,
     "Reports of unwarranted government monitoring, tracking, or surveillance."),
    ("police-misconduct", "Police Misconduct", 2,
     "Excessive force, false arrest, or other law-enforcement misconduct."),
    ("discrimination", "Discrimination", 3,
     "Discrimination in employment, public services, or accommodations."),
    ("immigration", "Immigration", 4,
     "Detention, removal proceedings, and immigration-status matters."),
    ("free-speech", "Free Speech / First Amendment", 5,
     "First Amendment, protest rights, and expression-related complaints."),
    ("privacy", "Privacy / Data Rights", 6,
     "Data rights, records access, and unlawful disclosure of personal information."),
    ("housing", "Housing Discrimination", 7,
     "Housing discrimination, unlawful eviction, and tenant-rights matters."),
    ("voting", "Voting Rights", 8,
     "Voter suppression, ballot access, and election-administration complaints."),
    ("prisoners", "Prisoners' Rights", 9,
     "Conditions of confinement and the rights of incarcerated people."),
    ("other", "Other", 99,
     "Matters that do not fit an existing category; pending triage."),
]
CATEGORY_IDS = [r[0] for r in CATEGORY_ROWS]

# ── Synthetic complainant name pools (clearly invented combos) ────────
FIRST_NAMES = [
    "Aurelia", "Bram", "Cassidy", "Dorian", "Esme", "Finnian", "Galen", "Harlow",
    "Ingrid", "Jules", "Kiran", "Lourdes", "Mavis", "Niko", "Odette", "Percival",
    "Quill", "Rosalind", "Soren", "Tamsin", "Ulrich", "Verena", "Wendell", "Xanthe",
    "Yusuf", "Zinnia", "Calliope", "Dashiell", "Elowen", "Florian",
]
LAST_NAMES = [
    "Ashford", "Brightwater", "Cobblepot", "Driftwood", "Everhart", "Fernsby",
    "Goodwill", "Hollowell", "Inkpen", "Juniper", "Kettlewell", "Larkspur",
    "Marsh", "Nettleton", "Oldacre", "Pennywhistle", "Quaintance", "Ravenscroft",
    "Stillwater", "Thistlewood", "Underbough", "Vellacott", "Westmoreland",
    "Yarrow", "Ziegler", "Birchall", "Crowfoot", "Dunmore",
]
FAKE_STREETS = [
    "Nowhere Lane", "Example Avenue", "Placeholder Boulevard", "Fictional Road",
    "Sample Street", "Imaginary Court", "Mockingbird Synthetic Drive",
    "Testfield Way", "Pretendville Circle", "Notreal Terrace", "Make-Believe Loop",
]
FAKE_CITIES = [
    "Faketon", "Sampleburg", "Mock City", "Testville", "Examplestead",
    "Placeholm", "Notrealia", "Springmock",
]
STATES = ["IN", "IL", "OH", "MI", "KY", "WI", "MO", "CA", "NY", "TX"]
EMAIL_DOMAINS = ["example.com", "example.net", "example.org"]
CONTACT_PREFS = ["phone", "email", "mail"]


def synth_person(idx):
    first = RNG.choice(FIRST_NAMES)
    last = RNG.choice(LAST_NAMES)
    has_phone = RNG.random() < 0.85
    has_email = RNG.random() < 0.7
    phone = f"(555) 555-01{RNG.randint(0, 99):02d}" if has_phone else ""
    email = (f"{first.lower()}.{last.lower()}@{RNG.choice(EMAIL_DOMAINS)}"
             if has_email else "")
    addr = (f"{RNG.randint(1, 4999)} {RNG.choice(FAKE_STREETS)}, "
            f"{RNG.choice(FAKE_CITIES)}")
    if RNG.random() < 0.2:
        addr = ""  # some submissions omit address
    pref = RNG.choice(CONTACT_PREFS)
    if pref == "phone" and not has_phone:
        pref = "email" if has_email else "mail"
    return first, last, phone, email, pref, addr


# ── Description templates per category ────────────────────────────────
DESCRIPTIONS = {
    "govt-surveillance": [
        "Complainant reports an unmarked vehicle parked outside the residence on multiple consecutive nights and believes they are being monitored.",
        "Caller states they were followed from a public meeting and asks whether any agency has a record of surveillance on them.",
        "Submitter describes repeated, coordinated harassment they attribute to government tracking and is seeking a records review.",
        "Individual believes their phone metadata is being collected without a warrant after a workplace dispute.",
    ],
    "police-misconduct": [
        "Complainant alleges officers used excessive force during a traffic stop and refused to provide badge numbers.",
        "Report of an arrest with no stated cause; complainant was held overnight and released without charges.",
        "Witness describes officers entering a home without a warrant during a wellness check.",
        "Complainant states a use-of-force incident at a protest was not documented in the official report.",
    ],
    "discrimination": [
        "Employee alleges they were passed over for promotion and later terminated after disclosing a disability.",
        "Customer was refused service at a business and believes it was based on national origin.",
        "Complainant reports a hostile work environment with repeated derogatory remarks tied to religion.",
        "Tenant alleges a property manager treats applicants differently based on family status.",
    ],
    "immigration": [
        "Family member detained during a routine check-in; complainant is seeking information on the removal timeline.",
        "Asylum seeker reports being unable to access counsel before a credible-fear interview.",
        "Complainant's work-authorization renewal has been pending for months with no status update.",
        "Individual fears deportation after a paperwork error and is requesting an urgent consultation.",
    ],
    "free-speech": [
        "Organizer states a permit for a peaceful demonstration was denied without a stated reason.",
        "Student reports discipline for distributing flyers in a public area of campus.",
        "Complainant's social-media account was reported and they believe a public official requested removal of a post.",
        "Caller was told they could not record officers in a public space and was threatened with arrest.",
    ],
    "privacy": [
        "Complainant requested their own records from an agency and the request was ignored past the statutory deadline.",
        "Individual's personal information appears to have been disclosed publicly without consent.",
        "Submitter reports a data broker is selling profile information and refuses opt-out requests.",
        "Complainant believes a medical record was accessed by an unauthorized party.",
    ],
    "housing": [
        "Tenant received an eviction notice the day after filing a habitability complaint.",
        "Applicant with a housing voucher reports being told the unit 'isn't available' after disclosing the voucher.",
        "Resident alleges a landlord refuses reasonable accommodation for a mobility disability.",
        "Complainant reports utilities shut off by the landlord in an attempt to force them out.",
    ],
    "voting": [
        "Voter reports being turned away at the polls despite valid registration.",
        "Complainant could not access the polling place due to a lack of accessible entrances.",
        "Submitter's mail ballot was reportedly rejected for a signature mismatch with no notice to cure.",
        "Caller describes long lines and reduced polling hours in their precinct.",
    ],
    "prisoners": [
        "Family reports an incarcerated relative is being denied necessary medical care.",
        "Complainant alleges retaliation after filing an internal grievance about conditions.",
        "Submitter reports mail to an incarcerated person is being withheld without explanation.",
        "Caller describes prolonged solitary confinement and is requesting a conditions review.",
    ],
    "other": [
        "General inquiry that does not fit an existing category; awaiting triage and routing.",
        "Complainant describes a mix of concerns and is unsure which program applies.",
        "Referral from a partner clinic; details to be gathered during the intake call.",
        "Walk-in submission with limited detail; follow-up requested.",
    ],
}

SOURCES = ["letter", "web", "email", "phone", "walk_in"]
SOURCE_W = [0.18, 0.40, 0.18, 0.16, 0.08]
URGENCY = ["low", "normal", "high", "critical"]
URGENCY_W = [0.20, 0.55, 0.18, 0.07]
STATUSES = ["new", "reviewed", "assigned", "in_progress", "resolved", "closed"]

RESOLUTIONS = [
    "Resolved — referred to partner legal-aid clinic; complainant connected with counsel.",
    "Closed — outside the organization's jurisdiction; provided referral list.",
    "Resolved — letter sent to the responsible agency; matter addressed.",
    "Closed — complainant did not respond to follow-up after three attempts.",
    "Resolved — intake assessed, no further legal action warranted; advice provided.",
    "Closed — duplicate of an existing matter; merged into the open case file.",
]


def pick_created(rng):
    r = rng.random()
    if r < 0.62:
        days = rng.randint(0, 30)
    elif r < 0.82:
        days = rng.randint(31, 60)
    else:
        days = rng.randint(61, 90)
    secs = rng.randint(8 * 3600, 18 * 3600)
    return TODAY - timedelta(days=days, seconds=secs), days


def pick_status(age_days, rng):
    if age_days <= 7:
        return rng.choices(
            ["new", "reviewed", "assigned", "in_progress"],
            [0.45, 0.30, 0.15, 0.10])[0]
    if age_days <= 30:
        return rng.choices(
            ["new", "reviewed", "assigned", "in_progress", "resolved", "closed"],
            [0.05, 0.20, 0.22, 0.25, 0.15, 0.13])[0]
    return rng.choices(
        ["assigned", "in_progress", "resolved", "closed"],
        [0.10, 0.20, 0.35, 0.35])[0]


STATUS_RANK = {s: i for i, s in enumerate(STATUSES)}


# ── Build intakes ─────────────────────────────────────────────────────
N_INTAKES = 72
intakes = []
for i in range(N_INTAKES):
    iid = uid(f"intake:{i}")
    created_at, age = pick_created(RNG)
    category = RNG.choice(CATEGORY_IDS)
    source = RNG.choices(SOURCES, SOURCE_W)[0]
    urgency = RNG.choices(URGENCY, URGENCY_W)[0]
    status = pick_status(age, RNG)
    first, last, phone, email, pref, addr = synth_person(i)
    state = RNG.choice(STATES)
    desc = RNG.choice(DESCRIPTIONS[category])

    # incident date: 1-45 days before intake, ~80% of the time
    incident_date = None
    if RNG.random() < 0.8:
        incident_date = created_at - timedelta(days=RNG.randint(1, 45),
                                               seconds=RNG.randint(0, 80000))

    # who logged it
    if source in ("letter", "phone", "walk_in"):
        created_by = STAFF_ID[RNG.choice(TRIAGERS + VOLUNTEERS)]
    elif source == "email" and RNG.random() < 0.5:
        created_by = STAFF_ID[RNG.choice(TRIAGERS)]
    else:
        created_by = None  # self-submitted via web form

    assigned_to = None
    resolved_at = None
    resolution = ""
    if STATUS_RANK[status] >= STATUS_RANK["assigned"]:
        assigned_to = STAFF_ID[RNG.choice(area_match(category))]
    if status in ("resolved", "closed"):
        resolved_at = created_at + timedelta(days=RNG.randint(2, max(3, age)),
                                             seconds=RNG.randint(0, 80000))
        if resolved_at > TODAY:
            resolved_at = TODAY - timedelta(hours=RNG.randint(2, 72))
        resolution = RNG.choice(RESOLUTIONS)

    if status == "new":
        updated_at = created_at
    else:
        bump = resolved_at or (created_at + timedelta(days=RNG.randint(1, max(2, age)),
                                                      seconds=RNG.randint(0, 80000)))
        updated_at = min(bump, TODAY)

    metadata = {"synthetic": True, "intake_channel": source}
    if source == "web":
        metadata["language"] = RNG.choice(["en", "en", "es"])
    if urgency in ("high", "critical"):
        metadata["flagged"] = True

    intakes.append(dict(
        id=iid, first=first, last=last, phone=phone, email=email, pref=pref,
        addr=addr, state=state, source=source, category=category, desc=desc,
        incident_date=incident_date, urgency=urgency, status=status,
        assigned_to=assigned_to, created_by=created_by, resolution=resolution,
        metadata=metadata, created_at=created_at, updated_at=updated_at,
        resolved_at=resolved_at, age=age,
    ))


# ── Notes ─────────────────────────────────────────────────────────────
NOTE_TEMPLATES = {
    "triage": [
        "Initial submission reviewed; details appear consistent. Routing for assignment.",
        "Logged from {src} intake. Flagged category for confirmation during follow-up.",
        "Triaged — urgency set to {urg}. Added to the review queue.",
        "Contact information verified. Awaiting attorney availability.",
    ],
    "contact": [
        "Called complainant at the number on file; left a voicemail with a callback request.",
        "Spoke with complainant; gathered additional timeline details and noted them here.",
        "Sent an acknowledgement and the records-request checklist via the preferred channel.",
        "Complainant prefers contact by {pref}; updated the record accordingly.",
    ],
    "assign": [
        "Assigned to handling staff based on category match. Conflict check cleared.",
        "Reassigned for workload balancing; prior reviewer briefed.",
        "Attorney accepted the matter; opening a working file.",
    ],
    "progress": [
        "Requested supporting documents from the complainant.",
        "Drafted a demand letter to the responsible party for internal review.",
        "Reviewed attached materials; OCR text looks clean and on point.",
        "Scheduled a follow-up consultation for next week.",
        "Awaiting a response to the records request before next steps.",
    ],
    "resolve": [
        "Closing the matter — {res}",
        "Resolution recorded and complainant notified.",
        "No further action warranted; archiving the file.",
    ],
}


def staff_for_note(intake, bucket):
    if bucket == "triage":
        return intake["created_by"] or STAFF_ID[RNG.choice(TRIAGERS)]
    if bucket in ("assign", "progress", "resolve") and intake["assigned_to"]:
        return intake["assigned_to"]
    return STAFF_ID[RNG.choice(ASSIGNABLE)]


notes = []
for intake in intakes:
    buckets = []
    rank = STATUS_RANK[intake["status"]]
    if rank >= STATUS_RANK["reviewed"] and RNG.random() < 0.55:
        buckets.append("triage")
    if RNG.random() < 0.30:
        buckets.append("contact")
    if rank >= STATUS_RANK["assigned"] and RNG.random() < 0.5:
        buckets.append("assign")
    if rank >= STATUS_RANK["in_progress"] and RNG.random() < 0.65:
        buckets.append("progress")
    if intake["status"] in ("resolved", "closed") and RNG.random() < 0.8:
        buckets.append("resolve")

    last_t = intake["created_at"]
    for bucket in buckets:
        tmpl = RNG.choice(NOTE_TEMPLATES[bucket])
        text = tmpl.format(src=intake["source"], urg=intake["urgency"],
                           pref=intake["pref"],
                           res=intake["resolution"] or "matter resolved.")
        last_t = last_t + timedelta(days=RNG.randint(0, 4),
                                    seconds=RNG.randint(600, 70000))
        ub = intake["updated_at"]
        nt = min(last_t, ub if ub > intake["created_at"] else TODAY, TODAY)
        notes.append(dict(
            id=auto_uid("note"), intake_id=intake["id"],
            author_id=staff_for_note(intake, bucket), text=text, created_at=nt,
        ))


# ── Attachments ───────────────────────────────────────────────────────
ATTACH_FILES = [
    ("complaint_letter", "application/pdf", "pdf"),
    ("intake_form", "application/pdf", "pdf"),
    ("supporting_statement", "application/pdf", "pdf"),
    ("incident_report_scan", "application/pdf", "pdf"),
    ("correspondence_email", "application/pdf", "pdf"),
    ("witness_statement", "application/pdf", "pdf"),
    ("id_document_redacted", "application/pdf", "pdf"),
    ("medical_record_redacted", "application/pdf", "pdf"),
    ("photo_evidence_01", "image/jpeg", "img"),
    ("photo_evidence_02", "image/jpeg", "img"),
    ("screenshot_thread", "image/png", "img"),
    ("audio_transcript", "text/plain", "txt"),
    ("timeline_summary", "application/vnd.openxmlformats-officedocument.wordprocessingml.document", "doc"),
]
OCR_TEXT_SNIPPETS = [
    "To whom it may concern, I am writing to report an incident that occurred...",
    "On the date noted above, the following events took place in sequence...",
    "I am requesting assistance regarding the matter described in this letter...",
    "The attached statement summarizes my account of what happened...",
]


def file_ext(kind):
    return {"pdf": "pdf", "img": "jpg" if "jpeg" else "png", "txt": "txt", "doc": "docx"}[kind]


attachments = []
for intake in intakes:
    n_att = RNG.choices([0, 1, 2, 3], [0.22, 0.42, 0.26, 0.10])[0]
    if intake["source"] == "letter":
        n_att = max(1, n_att)
    chosen = RNG.sample(ATTACH_FILES, k=min(n_att, len(ATTACH_FILES)))
    for base, ctype, kind in chosen:
        aid = auto_uid("att")
        ext = {"pdf": "pdf", "img": "jpg", "txt": "txt", "doc": "docx"}[kind]
        if ctype == "image/png":
            ext = "png"
        datestr = intake["created_at"].strftime("%Y-%m-%d")
        filename = f"{base}_{datestr}.{ext}"
        size = RNG.randint(180_000, 4_200_000) if kind in ("pdf", "img", "doc") else RNG.randint(2_000, 40_000)
        if kind == "pdf":
            ocr = RNG.choices(["complete", "pending", "failed"], [0.78, 0.14, 0.08])[0]
        elif kind == "img":
            ocr = RNG.choices(["complete", "pending", "failed", "skipped"], [0.55, 0.2, 0.15, 0.1])[0]
        else:
            ocr = "skipped"
        extracted = RNG.choice(OCR_TEXT_SNIPPETS) if ocr == "complete" else ""
        att_at = intake["created_at"] + timedelta(seconds=RNG.randint(30, 6000))
        attachments.append(dict(
            id=aid, intake_id=intake["id"], filename=filename, content_type=ctype,
            size_bytes=size, storage_path=f"/opt/intake/uploads/{intake['id']}/{aid}_{filename}",
            extracted_text=extracted, ocr_status=ocr,
            uploaded_by=intake["created_by"] or STAFF_ID[RNG.choice(TRIAGERS)],
            created_at=min(att_at, TODAY),
        ))


# ── Audit log ─────────────────────────────────────────────────────────
def rand_ip():
    block = RNG.choice(["203.0.113", "198.51.100"])
    return f"{block}.{RNG.randint(2, 250)}"


audit = []


def add_audit(staff_id, action, etype, eid, details, when):
    audit.append(dict(
        id=auto_uid("audit"), staff_id=staff_id, action=action, entity_type=etype,
        entity_id=eid, details=details, ip_address=rand_ip(), created_at=min(when, TODAY),
    ))


# logins/logouts scattered across staff over the window
for key, *_ in STAFF:
    for _ in range(RNG.randint(1, 3)):
        when = TODAY - timedelta(days=RNG.randint(0, 88), seconds=RNG.randint(0, 80000))
        add_audit(STAFF_ID[key], "login", "auth", None, {"method": "magic_link"}, when)
        if RNG.random() < 0.5:
            add_audit(STAFF_ID[key], "logout", "auth", None, {}, when + timedelta(seconds=RNG.randint(900, 18000)))

# lifecycle events per intake
for intake in intakes:
    creator = intake["created_by"] or STAFF_ID[RNG.choice(TRIAGERS)]
    add_audit(creator, "create", "intake", intake["id"],
              {"category": intake["category"], "source": intake["source"]},
              intake["created_at"] + timedelta(seconds=10))
    rank = STATUS_RANK[intake["status"]]
    if rank >= STATUS_RANK["reviewed"] and RNG.random() < 0.5:
        add_audit(STAFF_ID[RNG.choice(TRIAGERS)], "update", "intake", intake["id"],
                  {"field": "status", "to": "reviewed"},
                  intake["created_at"] + timedelta(days=RNG.randint(0, 3), seconds=RNG.randint(0, 60000)))
    if intake["assigned_to"]:
        add_audit(STAFF_ID[RNG.choice(TRIAGERS + ["dana"])], "assign", "intake", intake["id"],
                  {"assigned_to": intake["assigned_to"]},
                  intake["created_at"] + timedelta(days=RNG.randint(0, 5), seconds=RNG.randint(0, 60000)))
    if rank >= STATUS_RANK["in_progress"] and RNG.random() < 0.7:
        add_audit(intake["assigned_to"], "update", "intake", intake["id"],
                  {"field": "status", "to": "in_progress"},
                  intake["created_at"] + timedelta(days=RNG.randint(1, max(2, intake["age"])), seconds=RNG.randint(0, 60000)))
    if intake["status"] in ("resolved", "closed"):
        add_audit(intake["assigned_to"] or creator, "update", "intake", intake["id"],
                  {"field": "status", "to": intake["status"]},
                  intake["resolved_at"] or intake["updated_at"])
    # occasional views
    if RNG.random() < 0.25:
        add_audit(STAFF_ID[RNG.choice(ASSIGNABLE)], "view", "intake", intake["id"], {},
                  intake["created_at"] + timedelta(days=RNG.randint(0, max(1, intake["age"])), seconds=RNG.randint(0, 70000)))

# note/upload audit echoes (sampled)
for note in RNG.sample(notes, k=min(len(notes), 16)):
    add_audit(note["author_id"], "note_added", "note", note["id"],
              {"intake_id": note["intake_id"]}, note["created_at"])
for att in RNG.sample(attachments, k=min(len(attachments), 14)):
    add_audit(att["uploaded_by"], "upload", "attachment", att["id"],
              {"filename": att["filename"], "intake_id": att["intake_id"]}, att["created_at"])

# a few exports by admins
for _ in range(RNG.randint(3, 6)):
    when = TODAY - timedelta(days=RNG.randint(0, 60), seconds=RNG.randint(0, 80000))
    add_audit(STAFF_ID[RNG.choice(["dana", "ray"])], "export", "intake", None,
              {"format": "csv", "count": RNG.randint(5, 40)}, when)


# ── Magic links (25) ──────────────────────────────────────────────────
magic_links = []
for i in range(25):
    key = RNG.choice([k for k, *_ in STAFF])
    # ~5 of 25 are fresh (issued in the last few hours) → still valid
    if i % 5 == 0:
        created = TODAY - timedelta(minutes=RNG.randint(2, 50))
        ttl = RNG.choice([15, 30, 60])
    else:
        created = TODAY - timedelta(days=RNG.randint(1, 80), seconds=RNG.randint(0, 80000))
        ttl = RNG.choice([15, 15, 30, 60, 1440])  # minutes
    expires = created + timedelta(minutes=ttl)
    used = False
    roll = RNG.random()
    if expires < TODAY:
        used = roll < 0.7  # most expired links were actually used before expiry
    else:
        used = roll < 0.35  # an active link may already be consumed (single-use)
    magic_links.append(dict(
        id=auto_uid("ml"), token=uuid.uuid5(NS, f"token:{i}").hex + uuid.uuid5(NS, f"token2:{i}").hex,
        staff_id=STAFF_ID[key], expires_at=expires, used=used, created_at=created,
    ))


# ── Emit SQL ──────────────────────────────────────────────────────────
def build_sql():
    out = []
    w = out.append
    w("-- ────────────────────────────────────────────────────────────────────")
    w("-- 002_synthetic_seed.sql  —  Northwind Legal Group (FABRICATED FIRM)")
    w("-- ")
    w("-- 100% SYNTHETIC demo corpus. No real people, orgs, addresses, phones,")
    w("-- hosts, or paths. Generated by database/seed/generate_seed.py")
    w("-- (deterministic: fixed RNG seed + uuid5 ids → reproducible).")
    w("-- ")
    w("-- Loads automatically after 001_initial_schema.sql via Postgres'")
    w("-- /docker-entrypoint-initdb.d sequence (see docker-compose.yml).")
    w("-- Idempotent: every row uses a fixed id + ON CONFLICT DO NOTHING.")
    w("-- ────────────────────────────────────────────────────────────────────")
    w("")
    w("BEGIN;")
    w("")

    # Categories (self-sufficient: full row + enrich description on conflict)
    w("-- ── Categories (10) — also seeded by 001; here with descriptions ─────")
    rows = []
    for cid, label, sort_order, desc in CATEGORY_ROWS:
        rows.append(f"    ({sq(cid)}, {sq(label)}, {sq(desc)}, {sort_order}, TRUE)")
    w("INSERT INTO categories (id, label, description, sort_order, is_active) VALUES")
    w(",\n".join(rows))
    w("ON CONFLICT (id) DO UPDATE SET")
    w("    label = EXCLUDED.label, description = EXCLUDED.description,")
    w("    sort_order = EXCLUDED.sort_order, is_active = EXCLUDED.is_active;")
    w("")

    # Staff
    w("-- ── Staff (9) ───────────────────────────────────────────────────────")
    rows = []
    base_created = TODAY - timedelta(days=180)
    for n, (key, name, local, role, title, areas) in enumerate(STAFF):
        created = base_created + timedelta(days=n * 3, hours=n)
        areas_json = {"areas": areas, "title": title}
        rows.append(
            f"    ({sq(STAFF_ID[key])}, {sq(local + '@northwind-legal.local')}, "
            f"{sq(name)}, {sq(role)}, TRUE, {jb(areas_json)}, {ts(created)})"
        )
    w("INSERT INTO staff (id, email, name, role, is_active, areas, created_at) VALUES")
    w(",\n".join(rows))
    w("ON CONFLICT (id) DO NOTHING;")
    w("")

    # Intakes
    w(f"-- ── Intakes ({len(intakes)}) ──────────────────────────────────────────────────")
    rows = []
    for it in intakes:
        rows.append(
            "    (" + ", ".join([
                sq(it["id"]), sq(it["first"]), sq(it["last"]), sq(it["phone"]),
                sq(it["email"]), sq(it["pref"]), sq(it["addr"]), sq(it["state"]),
                sq(it["source"]), sq(it["category"]), sq(it["desc"]),
                ts(it["incident_date"]) if it["incident_date"] else "NULL",
                sq(it["urgency"]), sq(it["status"]),
                nullable_uuid(it["assigned_to"]), nullable_uuid(it["created_by"]),
                sq(it["resolution"]), jb(it["metadata"]),
                ts(it["created_at"]), ts(it["updated_at"]),
                ts(it["resolved_at"]) if it["resolved_at"] else "NULL",
            ]) + ")"
        )
    w("INSERT INTO intakes (id, first_name, last_name, phone, email, preferred_contact,")
    w("    address, state, source, category_id, description, incident_date, urgency,")
    w("    status, assigned_to, created_by, resolution, metadata, created_at, updated_at,")
    w("    resolved_at) VALUES")
    w(",\n".join(rows))
    w("ON CONFLICT (id) DO NOTHING;")
    w("")

    # Notes
    w(f"-- ── Notes ({len(notes)}) ─────────────────────────────────────────────────────")
    rows = []
    for nt in notes:
        rows.append(
            "    (" + ", ".join([
                sq(nt["id"]), sq(nt["intake_id"]), sq(nt["author_id"]),
                sq(nt["text"]), ts(nt["created_at"]),
            ]) + ")"
        )
    w("INSERT INTO notes (id, intake_id, author_id, text, created_at) VALUES")
    w(",\n".join(rows))
    w("ON CONFLICT (id) DO NOTHING;")
    w("")

    # Attachments
    w(f"-- ── Attachments ({len(attachments)}) ─────────────────────────────────────────")
    rows = []
    for at in attachments:
        rows.append(
            "    (" + ", ".join([
                sq(at["id"]), sq(at["intake_id"]), sq(at["filename"]),
                sq(at["content_type"]), str(at["size_bytes"]), sq(at["storage_path"]),
                sq(at["extracted_text"]), sq(at["ocr_status"]),
                nullable_uuid(at["uploaded_by"]), ts(at["created_at"]),
            ]) + ")"
        )
    w("INSERT INTO attachments (id, intake_id, filename, content_type, size_bytes,")
    w("    storage_path, extracted_text, ocr_status, uploaded_by, created_at) VALUES")
    w(",\n".join(rows))
    w("ON CONFLICT (id) DO NOTHING;")
    w("")

    # Audit log
    w(f"-- ── Audit log ({len(audit)}) ──────────────────────────────────────────────")
    rows = []
    for a in audit:
        rows.append(
            "    (" + ", ".join([
                sq(a["id"]), nullable_uuid(a["staff_id"]), sq(a["action"]),
                sq(a["entity_type"]),
                sq(a["entity_id"]) if a["entity_id"] else "NULL",
                jb(a["details"]), sq(a["ip_address"]), ts(a["created_at"]),
            ]) + ")"
        )
    w("INSERT INTO audit_log (id, staff_id, action, entity_type, entity_id, details,")
    w("    ip_address, created_at) VALUES")
    w(",\n".join(rows))
    w("ON CONFLICT (id) DO NOTHING;")
    w("")

    # Magic links
    w(f"-- ── Magic links ({len(magic_links)}) ────────────────────────────────────────")
    rows = []
    for m in magic_links:
        rows.append(
            "    (" + ", ".join([
                sq(m["id"]), sq(m["token"]), sq(m["staff_id"]),
                ts(m["expires_at"]), "TRUE" if m["used"] else "FALSE",
                ts(m["created_at"]),
            ]) + ")"
        )
    w("INSERT INTO magic_links (id, token, staff_id, expires_at, used, created_at) VALUES")
    w(",\n".join(rows))
    w("ON CONFLICT (id) DO NOTHING;")
    w("")

    w("COMMIT;")
    w("")
    w("-- ── Seed summary ─────────────────────────────────────────────────────")
    w(f"-- staff={len(STAFF)}  categories={len(CATEGORY_IDS)}  intakes={len(intakes)}")
    w(f"-- notes={len(notes)}  attachments={len(attachments)}  audit_log={len(audit)}"
      f"  magic_links={len(magic_links)}")
    return "\n".join(out)


if __name__ == "__main__":
    sql = build_sql()
    target = Path(__file__).resolve().parents[1] / "migrations" / "002_synthetic_seed.sql"
    target.write_text(sql)
    print(f"Wrote {target}")
    print(f"  staff={len(STAFF)} categories={len(CATEGORY_IDS)} intakes={len(intakes)}")
    print(f"  notes={len(notes)} attachments={len(attachments)} "
          f"audit_log={len(audit)} magic_links={len(magic_links)}")
