# database/

Schema and synthetic seed for the **intake-demo** clean room.

> **All data here is 100% synthetic.** Fabricated firm: *Northwind Legal Group*
> (`@northwind-legal.local`). Complainant contacts use RFC-reserved
> `example.com/.net/.org` domains, the `555-01xx` reserved phone range,
> obviously-fake street/city names, and RFC-5737 documentation IP ranges
> (`203.0.113.0/24`, `198.51.100.0/24`). No real people, organizations,
> addresses, hosts, or paths are referenced.

## Files

| File | Purpose |
|------|---------|
| `migrations/001_initial_schema.sql` | Types, tables, indexes, default categories. |
| `migrations/002_synthetic_seed.sql` | Generated synthetic demo corpus (see below). |
| `seed/generate_seed.py` | Deterministic generator that emits `002_…`. |

## How it loads

The Postgres container mounts `database/migrations` at
`/docker-entrypoint-initdb.d` (see `docker-compose.yml`). On the **first init of
an empty data volume**, Postgres runs every `*.sql` there in filename order:

```
001_initial_schema.sql   →   002_synthetic_seed.sql
```

So a fresh `docker compose up -d` gives you schema **and** seed automatically.

### Re-seeding

The init hook only runs against an *empty* data volume. To rebuild from scratch:

```bash
make db-reset       # docker compose down -v && up -d postgres
# or load into an already-running, non-empty DB (idempotent):
make db-load
make db-counts      # row-count sanity check
```

`002_synthetic_seed.sql` is idempotent — every row has a fixed UUID and uses
`ON CONFLICT DO NOTHING`, so re-applying it is a safe no-op.

## Seeded corpus (approximate)

| Table | Rows | Notes |
|-------|------|-------|
| `staff` | 9 | 1 admin · 3 attorney · 3 staff · 2 volunteer |
| `categories` | 10 | govt-surveillance, police-misconduct, discrimination, immigration, free-speech, privacy, housing, voting, prisoners, other |
| `intakes` | 72 | all 6 statuses; most created in the last 30 days, some aged 60–90 days |
| `notes` | ~138 | staff review/contact/assignment/resolution comments |
| `attachments` | ~95 | `complaint_letter_2026-…​.pdf`, scans, photos; mixed OCR status |
| `audit_log` | ~291 | login/logout/create/update/assign/view/upload/export |
| `magic_links` | 25 | mix of active / expired / used |

## Regenerating the seed

The seed is deterministic (fixed RNG seed + `uuid5` ids), so regeneration is
byte-stable:

```bash
python3 database/seed/generate_seed.py
```

Edit the pools/counts in `seed/generate_seed.py` and re-run to reshape the
corpus.
