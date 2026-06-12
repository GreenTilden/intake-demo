# intake-demo — Memory

## Project Identity
Clean-room public **demo** of a secure document-intake & chain-of-custody system for legal /
compliance workflows. **Synthetic data only** — fabricated firm "Northwind Legal Group", no
real client data. Stack: FastAPI + async SQLAlchemy + Vue 3/Vite SPA + PostgreSQL 16, with an
nginx web tier that serves the SPA and proxies `/api`. Built by DArnTech.

## Session Status
- **Status**: complete and running as a gated demo. `docker compose up -d --build` loads the
  schema + synthetic seed automatically; the SPA opens behind a Cloudflare Turnstile gate.
- **Architecture & Patterns**: SPA calls the API same-origin at `/api` (cookie auth, no CORS);
  PostgreSQL seeds via `docker-entrypoint-initdb.d` in filename order (`001` schema → `002`
  synthetic seed); the corpus is regenerated deterministically by
  `database/seed/generate_seed.py`.
- **Next steps** (optional): a public demo-login / seeded session so visitors can tour the
  data without the app's magic-link email step.
