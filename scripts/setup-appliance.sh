#!/usr/bin/env bash
# ──────────────────────────────────────────────────────────────
# Northwind Legal - Intake System — Appliance Setup Script
#
# Run on a fresh Debian 12 minimal install:
#   bash setup-appliance.sh
#
# What it does:
#   1. Installs Docker + Docker Compose
#   2. Installs Tesseract OCR + poppler (PDF tools)
#   3. Clones the application
#   4. Generates secure credentials
#   5. Starts the full stack
#   6. Sets up automated daily backups
#   7. Enables unattended security updates
#
# After running: access http://<server-ip>:8910/health
# ──────────────────────────────────────────────────────────────
set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log()  { echo -e "${GREEN}[SETUP]${NC} $1"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
err()  { echo -e "${RED}[ERROR]${NC} $1" >&2; exit 1; }

# ── Check prerequisites ──────────────────────────────────────

[[ $EUID -eq 0 ]] || err "Run as root: sudo bash setup-appliance.sh"

log "Starting Northwind Legal - Intake System appliance setup..."
log "Debian version: $(cat /etc/debian_version)"

INSTALL_DIR="/opt/intake-demo"
BACKUP_DIR="/opt/intake-demo-backups"
DATA_DIR="/opt/intake-demo-data"

# ── 1. System updates + unattended upgrades ──────────────────

log "Updating system packages..."
apt-get update -y
apt-get upgrade -y
apt-get install -y \
    curl \
    git \
    unattended-upgrades \
    apt-listchanges \
    ufw

# Enable unattended security updates
log "Enabling unattended security updates..."
cat > /etc/apt/apt.conf.d/20auto-upgrades << 'EOF'
APT::Periodic::Update-Package-Lists "1";
APT::Periodic::Unattended-Upgrade "1";
APT::Periodic::AutocleanInterval "7";
EOF

# ── 2. Firewall (SSH + HTTP only) ────────────────────────────

log "Configuring firewall..."
ufw --force reset
ufw default deny incoming
ufw default allow outgoing
ufw allow ssh
ufw allow 80/tcp
ufw allow 443/tcp
ufw allow 8910/tcp  # API direct access (for initial setup)
ufw --force enable
log "Firewall: SSH, HTTP, HTTPS, 8910 allowed"

# ── 3. Install Docker ────────────────────────────────────────

if command -v docker &>/dev/null; then
    log "Docker already installed: $(docker --version)"
else
    log "Installing Docker..."
    curl -fsSL https://get.docker.com | bash
    systemctl enable docker
    systemctl start docker
    log "Docker installed: $(docker --version)"
fi

# Ensure docker compose plugin
if ! docker compose version &>/dev/null; then
    apt-get install -y docker-compose-plugin
fi
log "Docker Compose: $(docker compose version)"

# ── 4. Create directories ────────────────────────────────────

log "Creating application directories..."
mkdir -p "$INSTALL_DIR" "$BACKUP_DIR" "$DATA_DIR/uploads"

# ── 5. Copy or clone application ─────────────────────────────

if [[ -f "$INSTALL_DIR/docker-compose.yml" ]]; then
    log "Application already present at $INSTALL_DIR"
else
    # If running from the repo, copy local files
    SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
    REPO_DIR="$(dirname "$SCRIPT_DIR")"

    if [[ -f "$REPO_DIR/docker-compose.yml" ]]; then
        log "Copying application from $REPO_DIR..."
        cp -r "$REPO_DIR/backend" "$INSTALL_DIR/"
        cp "$REPO_DIR/docker-compose.yml" "$INSTALL_DIR/"
        cp "$REPO_DIR/Makefile" "$INSTALL_DIR/"
    else
        warn "No local repo found. Place application files in $INSTALL_DIR manually."
        warn "Required: backend/, docker-compose.yml"
    fi
fi

# ── 6. Generate credentials ──────────────────────────────────

ENV_FILE="$INSTALL_DIR/.env"
if [[ -f "$ENV_FILE" ]]; then
    log "Existing .env found, keeping it"
else
    log "Generating secure credentials..."
    POSTGRES_PW=$(openssl rand -hex 16)
    SECRET_KEY=$(openssl rand -hex 32)

    cat > "$ENV_FILE" << EOF
# Northwind Legal - Intake System — generated $(date -Iseconds)
POSTGRES_PASSWORD=$POSTGRES_PW
SECRET_KEY=$SECRET_KEY
PORT=8910
CORS_ORIGINS=http://localhost,http://$(hostname -I | awk '{print $1}')
UPLOAD_DIR=/opt/intake/uploads

# Email (configure for magic link auth)
SMTP_HOST=
SMTP_PORT=587
SMTP_USER=
SMTP_PASS=
FROM_EMAIL=noreply@intake-demo.local
EOF

    chmod 600 "$ENV_FILE"
    log "Credentials generated and saved to $ENV_FILE"
fi

# ── 7. Start the stack ───────────────────────────────────────

log "Starting application stack..."
cd "$INSTALL_DIR"
docker compose up -d --build

# Wait for postgres to be ready
log "Waiting for PostgreSQL..."
for i in {1..30}; do
    if docker compose exec -T postgres pg_isready -U intake &>/dev/null; then
        break
    fi
    sleep 1
done

# ── 8. Initialize database ───────────────────────────────────

log "Database is up. Run migrations when ready."
log "(Tables will be created on first API start via SQLAlchemy)"

# Seed default categories
sleep 3
if curl -sf -X POST http://localhost:8910/api/categories/seed &>/dev/null; then
    log "Default categories seeded"
else
    warn "Could not seed categories (API may still be starting)"
fi

# ── 9. Automated daily backup ────────────────────────────────

log "Setting up automated daily backups..."
cat > /etc/cron.d/intake-demo-backup << 'CRON'
# Daily backup at 2 AM — Northwind Legal - Intake System
0 2 * * * root cd /opt/intake-demo && docker compose exec -T postgres pg_dump -U intake intake | gzip > /opt/intake-demo-backups/intake-$(date +\%Y\%m\%d).sql.gz && find /opt/intake-demo-backups -name "*.sql.gz" -mtime +30 -delete
CRON

chmod 644 /etc/cron.d/intake-demo-backup
log "Daily backup configured: /opt/intake-demo-backups/ (30-day retention)"

# ── 10. Done ─────────────────────────────────────────────────

IP=$(hostname -I | awk '{print $1}')

echo ""
echo -e "${GREEN}════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}  Northwind Legal - Intake System — Setup Complete${NC}"
echo -e "${GREEN}════════════════════════════════════════════════════${NC}"
echo ""
echo -e "  API:      ${YELLOW}http://$IP:8910${NC}"
echo -e "  Health:   ${YELLOW}http://$IP:8910/health${NC}"
echo -e "  Backups:  ${YELLOW}/opt/intake-demo-backups/${NC} (daily at 2 AM)"
echo -e "  Logs:     ${YELLOW}cd $INSTALL_DIR && docker compose logs -f${NC}"
echo ""
echo -e "  ${RED}NEXT STEPS:${NC}"
echo -e "  1. Create first admin staff member via API"
echo -e "  2. Configure SMTP in $ENV_FILE for magic link emails"
echo -e "  3. Seed categories: curl -X POST http://$IP:8910/api/categories/seed"
echo ""
echo -e "${GREEN}════════════════════════════════════════════════════${NC}"
