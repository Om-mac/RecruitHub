#!/bin/bash

# Migrate database from Render to RDS
# Usage: ./migrate_db_render_to_rds.sh

set -e

echo "Database Migration: Render → AWS RDS"
echo "===================================="
echo ""

read -p "Enter Render DB host: " RENDER_HOST
read -p "Enter Render DB user: " RENDER_USER
read -p "Enter Render DB name: " RENDER_DB
read -sp "Enter Render DB password: " RENDER_PASSWORD
echo ""

read -p "Enter RDS endpoint: " RDS_HOST
read -p "Enter RDS username: " RDS_USER
read -p "Enter RDS database name: " RDS_DB
read -sp "Enter RDS password: " RDS_PASSWORD
echo ""

BACKUP_FILE="render_to_rds_$(date +%Y%m%d_%H%M%S).sql"

echo ""
echo "Step 1: Exporting from Render..."
PGPASSWORD="$RENDER_PASSWORD" pg_dump \
    -h "$RENDER_HOST" \
    -U "$RENDER_USER" \
    -d "$RENDER_DB" \
    --verbose \
    > "$BACKUP_FILE"

echo "✓ Backup saved to: $BACKUP_FILE"
echo "  File size: $(du -h "$BACKUP_FILE" | cut -f1)"

echo ""
echo "Step 2: Importing to RDS..."
PGPASSWORD="$RDS_PASSWORD" psql \
    -h "$RDS_HOST" \
    -U "$RDS_USER" \
    -d "$RDS_DB" \
    --verbose \
    < "$BACKUP_FILE"

echo ""
echo "✓ Migration complete!"
echo ""
echo "Step 3: Verification..."

TABLE_COUNT=$(PGPASSWORD="$RDS_PASSWORD" psql \
    -h "$RDS_HOST" \
    -U "$RDS_USER" \
    -d "$RDS_DB" \
    -tc "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='public';")

echo "Tables in RDS: $TABLE_COUNT"

echo ""
echo "Migration Summary:"
echo "  Source: $RENDER_HOST/$RENDER_DB"
echo "  Target: $RDS_HOST/$RDS_DB"
echo "  Backup: $BACKUP_FILE"
echo ""
echo "Next steps:"
echo "  1. Update Django settings with RDS credentials"
echo "  2. Set environment variables in EB"
echo "  3. Deploy application: eb deploy"
echo "  4. Test: eb open"
