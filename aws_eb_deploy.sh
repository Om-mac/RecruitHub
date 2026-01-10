#!/bin/bash

# AWS Elastic Beanstalk Deployment Helper Script
# Usage: chmod +x aws_eb_deploy.sh && ./aws_eb_deploy.sh

set -e

echo "================================"
echo "RecruitHub AWS EB Deployment"
echo "================================"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check prerequisites
echo -e "${YELLOW}[1/7] Checking prerequisites...${NC}"
if ! command -v eb &> /dev/null; then
    echo -e "${RED}EB CLI not found. Install with: brew install aws-elasticbeanstalk${NC}"
    exit 1
fi

if ! command -v aws &> /dev/null; then
    echo -e "${RED}AWS CLI not found. Install with: curl https://awscli.amazonaws.com/awscli-exe-macos.pkg${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Prerequisites OK${NC}"

# Check AWS credentials
echo -e "${YELLOW}[2/7] Verifying AWS credentials...${NC}"
if ! aws sts get-caller-identity &> /dev/null; then
    echo -e "${RED}AWS credentials not configured. Run: aws configure${NC}"
    exit 1
fi

echo -e "${GREEN}✓ AWS credentials OK${NC}"

# Clean up
echo -e "${YELLOW}[3/7] Cleaning up old files...${NC}"
rm -rf dist/ build/ *.egg-info
python manage.py collectstatic --noinput --clear

echo -e "${GREEN}✓ Cleanup complete${NC}"

# Generate requirements.txt
echo -e "${YELLOW}[4/7] Generating requirements.txt...${NC}"
pip freeze > requirements.txt

echo -e "${GREEN}✓ requirements.txt generated${NC}"

# Check EB initialization
echo -e "${YELLOW}[5/7] Checking EB initialization...${NC}"
if [ ! -d ".elasticbeanstalk" ]; then
    echo -e "${YELLOW}   Initializing EB application...${NC}"
    eb init -p python-3.11 recruithub --region us-east-1
fi

echo -e "${GREEN}✓ EB initialized${NC}"

# Deploy
echo -e "${YELLOW}[6/7] Deploying to Elastic Beanstalk...${NC}"
eb deploy

echo -e "${GREEN}✓ Deployment complete${NC}"

# Verify
echo -e "${YELLOW}[7/7] Verifying deployment...${NC}"
sleep 10

if eb health | grep -q "Green"; then
    echo -e "${GREEN}✓ Application is healthy!${NC}"
    echo ""
    echo -e "${GREEN}================================${NC}"
    echo -e "${GREEN}Deployment Successful!${NC}"
    echo -e "${GREEN}================================${NC}"
    echo ""
    eb open
else
    echo -e "${YELLOW}⚠ Application health unclear. Check with:${NC}"
    echo "  eb health"
    echo "  eb logs"
fi
