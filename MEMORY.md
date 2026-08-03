# intake-demo — Memory

## Project Identity
Clean-room public **demo** of a secure document-intake & chain-of-custody system for legal /
compliance workflows. **Synthetic data only** — fabricated firm "Northwind Legal Group", no
real client data. Stack: FastAPI + async SQLAlchemy + Vue 3/Vite SPA + PostgreSQL 16, with an
nginx web tier that serves the SPA and proxies `/api`. Built by DArnTech.

## Session Status
- **Status**: complete and running as a gated demo (parody-named synthetic data, no real
  client data). Most recent change was a mechanical dependency audit-fix (`9be6f2c`,
  2026-08-01, lockfile-only). No feature work since 2026-06-12.
- **Current Focus**: none active — the demo is feature-complete; the item below is an
  optional, not-yet-scheduled improvement.
- **Blockers**: none.
- **Next Steps** (optional): a public demo-login / seeded session so visitors can tour the
  data without the app's magic-link email step.
- **Last Updated**: 2026-08-02
- **Prior status note**: complete and running as a gated demo. `docker compose up -d --build`
  loads the schema + synthetic seed automatically; the SPA opens behind a Cloudflare Turnstile
  gate.

## Architecture & Patterns
- SPA calls the API same-origin at `/api` (cookie auth, no CORS); PostgreSQL seeds via
  `docker-entrypoint-initdb.d` in filename order (`001` schema → `002` synthetic seed); the
  corpus is regenerated deterministically by `database/seed/generate_seed.py`.
- Web tier (nginx) serves the built Vue SPA and reverse-proxies `/api` to the FastAPI backend
  — one container, one origin, no CORS to reason about.
- Auth is magic-link (no passwords); the SPA gate itself sits behind a Cloudflare Turnstile
  "verify you're human" check (test sitekey by default in `frontend/src/App.vue`).

## Decisions
- Clean-room fork with fully synthetic data — fabricated firm name, parody staff names
  (SNL hosts + musical acts), `example.com`/`555-01xx`/RFC-5737 contact info — so nothing in
  the repo can be mistaken for a real client's data (commit `71cec73`, `3359b86`, `44a6cb6`).
- Demo is anonymous-public (Turnstile-gated, not Authelia) since it's a portfolio/sales demo,
  not an internal tool.

## Dependencies
- PostgreSQL 16 (seeded automatically at container start — no external DB dependency).
- Cloudflare Turnstile for the human-check gate (test sitekey by default; swap for a real one
  to actually enforce it in prod).
- No dependency on any other DArnTech repo/service — self-contained demo stack.

## Deployment Targets
- Local/dev: `docker compose up -d --build` (postgres + api + nginx web tier serving the SPA),
  health-checked via `make health` (port per `docker-compose.yml`).
- `make deploy` rsyncs `backend`/`docker-compose.yml`/`Makefile`/`scripts` to `$(PROD_HOST):
  $(PROD_DIR)` (defaults are placeholders — `root@intake-demo.local` / `/opt/intake-demo` —
  not a confirmed live host); no evidence in this repo of an actual production hostname
  currently in use, so treat `make deploy` as a template until the operator confirms a target.
