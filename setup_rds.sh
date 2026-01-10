#!/bin/bash

# Setup script for AWS RDS Database
# Run this AFTER RDS instance is created in AWS Console

set -e

echo "AWS RDS Setup Script"
echo "===================="

read -p "Enter RDS endpoint (e.g., recruithub-db.xxxxx.us-east-1.rds.amazonaws.com): " RDS_HOST
read -p "Enter RDS username (default: postgres): " RDS_USER
RDS_USER=${RDS_USER:-postgres}
read -sp "Enter RDS master password: " RDS_PASSWORD
echo ""
read -p "Enter database name (default: recruithub): " RDS_DB_NAME
RDS_DB_NAME=${RDS_DB_NAME:-recruithub}

echo ""
echo "Connecting to RDS..."

# Create database if it doesn't exist
psql -h "$RDS_HOST" -U "$RDS_USER" -w <<EOF
$RDS_PASSWORD
CREATE DATABASE IF NOT EXISTS "$RDS_DB_NAME";
EOF

echo "Database created/verified."

# Backup from Render (if needed)
read -p "Export from Render first? (y/n): " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    read -p "Enter Render DB host: " RENDER_HOST
    read -p "Enter Render DB user: " RENDER_USER
    read -p "Enter Render DB name: " RENDER_DB
    read -sp "Enter Render DB password: " RENDER_PASSWORD
    echo ""
    
    echo "Exporting from Render..."
    PGPASSWORD="$RENDER_PASSWORD" pg_dump -h "$RENDER_HOST" -U "$RENDER_USER" -d "$RENDER_DB" > render_backup.sql
    
    echo "Importing to RDS..."
    PGPASSWORD="$RDS_PASSWORD" psql -h "$RDS_HOST" -U "$RDS_USER" -d "$RDS_DB_NAME" < render_backup.sql
fi

echo ""
echo "RDS setup complete!"
echo ""
echo "Store these credentials in AWS Secrets Manager or EB environment:"
echo "  RDS_HOSTNAME=$RDS_HOST"
echo "  RDS_USERNAME=$RDS_USER"
echo "  RDS_PASSWORD=***"
echo "  RDS_DB_NAME=$RDS_DB_NAME"
echo "  RDS_PORT=5432"
