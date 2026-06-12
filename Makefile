.PHONY: dev setup deploy seed health backup db-reset db-load db-counts

# Local development
DEV_PORT = 8910
FRONTEND_PORT = 5012

# Production (appliance or remote)
PROD_HOST ?= root@intake-demo.local
PROD_DIR  = /opt/intake-demo
PROD_URL  = http://localhost:8910

dev:
	cd backend && ../.venv/bin/uvicorn app.main:app --reload --port $(DEV_PORT)

setup:
	python3 -m venv .venv
	.venv/bin/pip install -r backend/requirements.txt
	@echo "Run: make dev"

up:
	docker compose up -d --build

down:
	docker compose down

logs:
	docker compose logs -f api

seed:
	@curl -sf -X POST http://localhost:$(DEV_PORT)/api/categories/seed | python3 -m json.tool

# ── Database schema + synthetic seed ─────────────────────────────────
# 001_initial_schema.sql + 002_synthetic_seed.sql auto-run (in filename
# order) on the FIRST init of an empty postgres data volume — see the
# docker-entrypoint-initdb.d mount in docker-compose.yml.

# Drop the data volume and re-run schema + synthetic seed from scratch.
db-reset:
	docker compose down -v
	docker compose up -d postgres
	@echo "Schema + synthetic seed loaded into a fresh volume."

# Load schema + seed into an already-running postgres (non-empty volume,
# where the initdb hook will NOT re-run). Idempotent: ON CONFLICT DO NOTHING.
db-load:
	docker compose exec -T postgres psql -U intake -d intake < database/migrations/001_initial_schema.sql || true
	docker compose exec -T postgres psql -U intake -d intake < database/migrations/002_synthetic_seed.sql

# Quick row-count sanity check of the seeded corpus.
db-counts:
	@docker compose exec -T postgres psql -U intake -d intake -At -c "\
	  SELECT 'staff', count(*) FROM staff \
	  UNION ALL SELECT 'categories', count(*) FROM categories \
	  UNION ALL SELECT 'intakes', count(*) FROM intakes \
	  UNION ALL SELECT 'notes', count(*) FROM notes \
	  UNION ALL SELECT 'attachments', count(*) FROM attachments \
	  UNION ALL SELECT 'audit_log', count(*) FROM audit_log \
	  UNION ALL SELECT 'magic_links', count(*) FROM magic_links;"

health:
	@curl -sf http://localhost:$(DEV_PORT)/health | python3 -m json.tool || echo "DOWN"

backup:
	docker compose exec postgres pg_dump -U intake intake > backup-$$(date +%Y%m%d).sql
	@echo "Backup saved: backup-$$(date +%Y%m%d).sql"

deploy:
	rsync -av --exclude='__pycache__' --exclude='.venv' --exclude='.git' \
		--exclude='*.pyc' --exclude='node_modules' \
		backend docker-compose.yml Makefile scripts \
		$(PROD_HOST):$(PROD_DIR)/
	ssh $(PROD_HOST) 'cd $(PROD_DIR) && docker compose up -d --build'
	@sleep 3 && ssh $(PROD_HOST) 'curl -sf http://localhost:8910/health' | python3 -m json.tool

appliance:
	@echo "Run on fresh Debian 12:"
	@echo "  bash scripts/setup-appliance.sh"
