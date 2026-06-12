.PHONY: dev setup deploy seed health backup

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
