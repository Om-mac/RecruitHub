#!/bin/bash

# AWS EB Migration - Pre-Launch Verification Script
# Run this to verify everything is ready before launching

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

PASS=0
FAIL=0
WARN=0

# Helper functions
check_pass() {
    echo -e "${GREEN}✓ $1${NC}"
    ((PASS++))
}

check_fail() {
    echo -e "${RED}✗ $1${NC}"
    ((FAIL++))
}

check_warn() {
    echo -e "${YELLOW}⚠ $1${NC}"
    ((WARN++))
}

header() {
    echo ""
    echo -e "${BLUE}===================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}===================================${NC}"
}

# Start checks
header "AWS EB Migration - Pre-Launch Verification"

# 1. Git Status
header "1. Git Repository"
if [ -d ".git" ]; then
    check_pass "Git repository found"
    if git status | grep -q "nothing to commit"; then
        check_pass "All code committed"
    else
        check_fail "Uncommitted changes exist"
    fi
else
    check_fail "Git repository not found"
fi

# 2. AWS Tools
header "2. AWS Tools"
if command -v aws &> /dev/null; then
    check_pass "AWS CLI installed"
    aws_version=$(aws --version | cut -d' ' -f1)
    check_pass "AWS CLI version: $aws_version"
else
    check_fail "AWS CLI not installed"
fi

if command -v eb &> /dev/null; then
    check_pass "EB CLI installed"
    eb_version=$(eb --version | cut -d' ' -f1)
    check_pass "EB CLI version: $eb_version"
else
    check_fail "EB CLI not installed"
fi

# 3. AWS Credentials
header "3. AWS Credentials"
if aws sts get-caller-identity &> /dev/null; then
    check_pass "AWS credentials configured"
    aws_account=$(aws sts get-caller-identity --query Account --output text)
    aws_user=$(aws sts get-caller-identity --query Arn --output text)
    check_pass "AWS Account: $aws_account"
    check_pass "AWS User: $aws_user"
else
    check_fail "AWS credentials not configured or invalid"
fi

# 4. Project Structure
header "4. Project Structure"
if [ -d ".ebextensions" ]; then
    check_pass ".ebextensions directory found"
    if [ -f ".ebextensions/01_django.config" ]; then
        check_pass "Django configuration present"
    else
        check_fail "Django configuration missing"
    fi
else
    check_fail ".ebextensions directory not found"
fi

if [ -f "requirements.txt" ]; then
    check_pass "requirements.txt found"
    
    if grep -q "Django" requirements.txt; then
        check_pass "Django listed in requirements"
    else
        check_fail "Django not in requirements.txt"
    fi
    
    if grep -q "psycopg2" requirements.txt; then
        check_pass "psycopg2 listed in requirements"
    else
        check_fail "psycopg2 not in requirements.txt (needed for PostgreSQL)"
    fi
    
    if grep -q "gunicorn" requirements.txt; then
        check_pass "gunicorn listed in requirements"
    else
        check_fail "gunicorn not in requirements.txt (needed for EB)"
    fi
else
    check_fail "requirements.txt not found"
fi

# 5. Django Configuration
header "5. Django Configuration"
if [ -f "auth_project/settings.py" ]; then
    check_pass "Django settings file found"
    
    if grep -q "ALLOWED_HOSTS" auth_project/settings.py; then
        check_pass "ALLOWED_HOSTS configured"
    else
        check_warn "ALLOWED_HOSTS may need configuration"
    fi
    
    if grep -q "RDS_" auth_project/settings.py || grep -q "os.environ.get" auth_project/settings.py; then
        check_pass "Environment variables used for configuration"
    else
        check_warn "Database configuration may need RDS environment variables"
    fi
else
    check_fail "Django settings.py not found"
fi

if [ -f "manage.py" ]; then
    check_pass "Django manage.py found"
else
    check_fail "Django manage.py not found"
fi

# 6. Static Files
header "6. Static Files"
if python manage.py check &> /dev/null; then
    check_pass "Django check passed (no critical errors)"
else
    check_fail "Django check failed - review errors above"
fi

if [ -d "staticfiles" ] || [ -d "static" ]; then
    check_pass "Static files directory exists"
else
    check_warn "Static files directory not found (will be created during deploy)"
fi

# 7. Environment Configuration
header "7. Environment Configuration"
if [ -f ".env.prod.example" ]; then
    check_pass ".env.prod.example template found"
else
    check_warn ".env.prod.example not found"
fi

if [ -f ".env.prod" ]; then
    check_warn ".env.prod exists (should not be committed)"
    if git status | grep -q ".env.prod"; then
        check_fail ".env.prod is tracked by git (add to .gitignore)"
    else
        check_pass ".env.prod is properly ignored"
    fi
else
    check_warn ".env.prod not created yet (will need to create)"
fi

# 8. Database
header "8. Database"
read -p "Has RDS PostgreSQL been created? (y/n): " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    check_pass "RDS database created"
    read -p "Enter RDS endpoint (or skip): " RDS_HOST
    if [ ! -z "$RDS_HOST" ]; then
        if psql -h "$RDS_HOST" -U postgres -c "\l" &> /dev/null; then
            check_pass "Can connect to RDS database"
        else
            check_warn "Cannot connect to RDS (may need security group update)"
        fi
    fi
else
    check_warn "RDS database not yet created"
fi

# 9. Documentation
header "9. Documentation"
docs=("AWS_EB_MIGRATION_GUIDE.md" "ROUTE53_DNS_SETUP.md" "MIGRATION_CHECKLIST.md" "AWS_QUICK_REFERENCE.md" "AWS_EB_SUMMARY.md")
for doc in "${docs[@]}"; do
    if [ -f "$doc" ]; then
        check_pass "$doc found"
    else
        check_fail "$doc not found"
    fi
done

# 10. EB Status
header "10. Elastic Beanstalk"
if [ -d ".elasticbeanstalk" ]; then
    check_pass "EB initialized"
    
    if eb status &> /dev/null; then
        check_pass "EB environment accessible"
        env_status=$(eb status | grep "Status" | awk '{print $NF}')
        check_pass "EB Status: $env_status"
    else
        check_warn "EB environment not running yet"
    fi
else
    check_warn "EB not initialized yet (run: eb init)"
fi

# 11. Scripts
header "11. Deployment Scripts"
scripts=("aws_eb_deploy.sh" "set_eb_env_vars.sh" "migrate_db_render_to_rds.sh")
for script in "${scripts[@]}"; do
    if [ -f "$script" ]; then
        if [ -x "$script" ]; then
            check_pass "$script is executable"
        else
            check_warn "$script exists but not executable (run: chmod +x $script)"
        fi
    else
        check_warn "$script not found"
    fi
done

# 12. Security
header "12. Security Checks"
if [ -f ".gitignore" ] && grep -q ".env" .gitignore; then
    check_pass "Environment files are gitignored"
else
    check_warn "Ensure .env files are in .gitignore"
fi

if [ -f ".gitignore" ] && grep -q "*.sqlite3" .gitignore; then
    check_pass "Database files are gitignored"
else
    check_warn "Ensure database files are gitignored"
fi

if grep -q "DEBUG = False" auth_project/settings.py; then
    check_pass "DEBUG set to False for production"
elif grep -q "DEBUG = os.environ" auth_project/settings.py; then
    check_pass "DEBUG configured via environment variable"
else
    check_warn "DEBUG setting may be True in production"
fi

# Summary
header "VERIFICATION SUMMARY"
echo ""
echo -e "${GREEN}Passed:${NC} $PASS"
echo -e "${RED}Failed:${NC} $FAIL"
echo -e "${YELLOW}Warnings:${NC} $WARN"
echo ""

if [ $FAIL -eq 0 ]; then
    echo -e "${GREEN}✓ All critical checks passed!${NC}"
    echo ""
    echo "Next steps:"
    echo "1. Review warnings above"
    echo "2. Create .env.prod from .env.prod.example"
    echo "3. Run: ./aws_eb_deploy.sh"
    echo "4. Monitor: eb logs -z"
    echo ""
    exit 0
else
    echo -e "${RED}✗ Fix the failures above before proceeding${NC}"
    echo ""
    exit 1
fi
