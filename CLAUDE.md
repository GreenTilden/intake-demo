# intake-demo

A clean-room **demo** of a secure document-intake & chain-of-custody system for legal and
compliance workflows — intake, classification, status tracking, and audit trails. Self-hosted,
CPU-only, no cloud. **All data is synthetic** (fabricated firm "Northwind Legal Group"); there
is no real client data anywhere in this repository.

## Stack
- **Backend** — FastAPI (Python), async SQLAlchemy + asyncpg, magic-link auth.
- **Frontend** — Vue 3 + TypeScript + Vite SPA; calls the API same-origin at `/api`.
- **Database** — PostgreSQL 16; schema + synthetic seed load via `docker-entrypoint-initdb.d`.
- **Web tier** — nginx serves the built SPA and reverse-proxies `/api` to the backend.

## Run it
```
docker compose up -d --build      # postgres + api
make db-counts                    # sanity-check the synthetic corpus
```
The SPA opens behind a Cloudflare Turnstile "verify you're human" gate (an always-pass TEST
sitekey by default — swap `SITEKEY` in `frontend/src/App.vue` for a real one).

## Synthetic data
The corpus is generated deterministically by `database/seed/generate_seed.py` →
`database/migrations/002_synthetic_seed.sql` (staff, categories, ~72 intakes, notes,
attachments, audit log, magic-links). Names are deliberate parodies; contacts use
RFC-reserved `example.com` domains, the `555-01xx` reserved phone range, and RFC-5737
documentation IP ranges. Re-shape and re-emit with `python3 database/seed/generate_seed.py`.

Built by [DArnTech](https://darn-tech.com).
