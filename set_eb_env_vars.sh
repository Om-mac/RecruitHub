#!/bin/bash

# Set environment variables in Elastic Beanstalk
# Usage: ./set_eb_vars.sh

set -e

echo "Setting Elastic Beanstalk Environment Variables"
echo "=============================================="

# Read from .env file if it exists
if [ -f .env.prod ]; then
    echo "Loading from .env.prod..."
    export $(cat .env.prod | xargs)
fi

# Ask for variables if not set
read -p "Django SECRET_KEY: " SECRET_KEY
read -p "DEBUG mode (False/True): " DEBUG
DEBUG=${DEBUG:-False}
read -p "RDS Hostname: " RDS_HOSTNAME
read -p "RDS Username: " RDS_USERNAME
read -sp "RDS Password: " RDS_PASSWORD
echo ""
read -p "RDS Database Name (default: recruithub): " RDS_DB_NAME
RDS_DB_NAME=${RDS_DB_NAME:-recruithub}
read -p "RDS Port (default: 5432): " RDS_PORT
RDS_PORT=${RDS_PORT:-5432}
read -p "Email Backend: " EMAIL_BACKEND
read -p "Email Host: " EMAIL_HOST
read -p "Email Port: " EMAIL_PORT
read -p "Email User: " EMAIL_USER
read -sp "Email Password: " EMAIL_PASSWORD
echo ""

echo ""
echo "Setting variables in EB..."

eb setenv \
  DEBUG="$DEBUG" \
  SECRET_KEY="$SECRET_KEY" \
  RDS_HOSTNAME="$RDS_HOSTNAME" \
  RDS_USERNAME="$RDS_USERNAME" \
  RDS_PASSWORD="$RDS_PASSWORD" \
  RDS_DB_NAME="$RDS_DB_NAME" \
  RDS_PORT="$RDS_PORT" \
  EMAIL_BACKEND="$EMAIL_BACKEND" \
  EMAIL_HOST="$EMAIL_HOST" \
  EMAIL_PORT="$EMAIL_PORT" \
  EMAIL_USER="$EMAIL_USER" \
  EMAIL_PASSWORD="$EMAIL_PASSWORD" \
  ALLOWED_HOSTS="vakverse.com,www.vakverse.com,*.elasticbeanstalk.com"

echo ""
echo "✓ Environment variables set!"
echo ""
echo "Verifying..."
eb printenv
