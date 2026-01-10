# AWS Elastic Beanstalk Migration Guide

## Overview
Migrating from Render → AWS Elastic Beanstalk (EC2 + ALB + RDS + Route 53)

```
Current (Render):
├─ Render Django Render Django App
 ├─ Render PostgreSQL
 ├─ Render Env Vars
 └─ Render Domain
        ↓
AWS Elastic Beanstalk
 ├─ EC2 + ALB (managed)
 ├─ Amazon RDS (PostgreSQL)
 ├─ EB Environment Variables
 └─ Route 53 / DNS → vakverse.comApp
├─ Render PostgreSQL
├─ Render Env Vars
└─ Render Domain

Target (AWS EB):
├─ EC2 + ALB (Auto Scaling)
├─ Amazon RDS PostgreSQL
├─ EB Environment Variables
└─ Route 53 / DNS (vakverse.com)
```

---

## Phase 1: AWS Account & Prerequisite Setup

### 1.1 AWS Account Requirements
- [ ] AWS Account created
- [ ] Billing enabled
- [ ] IAM user with programmatic access (AWS CLI credentials)
- [ ] EC2 key pair created (for SSH access)

### 1.2 Install AWS CLI & EB CLI
```bash
# Install AWS CLI v2
curl "https://awscli.amazonaws.com/awscli-exe-macos.pkg" -o "AWSCLIV2.pkg"
sudo installer -pkg AWSCLIV2.pkg -target /

# Verify installation
aws --version

# Install EB CLI
brew install aws-elasticbeanstalk/tap/aws-elasticbeanstalk

# Verify installation
eb --version
```

### 1.3 Configure AWS Credentials
```bash
aws configure

# You'll be prompted for:
# AWS Access Key ID: [your-key]
# AWS Secret Access Key: [your-secret]
# Default region: us-east-1 (or preferred region)
# Default output format: json
```

---

## Phase 2: Database Migration (RDS PostgreSQL)

### 2.1 Create RDS PostgreSQL Instance
```bash
# Via AWS Console:
# 1. Go to RDS Dashboard
# 2. Create Database → PostgreSQL
# 3. Settings:
#    - DB Instance Identifier: recruithub-db
#    - Master Username: postgres
#    - Master Password: [STRONG-PASSWORD]
#    - DB Instance Class: db.t3.micro (free tier eligible)
#    - Storage: 20 GB (General Purpose SSD)
#    - VPC: Default VPC
#    - Publicly Accessible: No (EB will access internally)
#    - Backup: Enabled (7 days retention)
#    - Multi-AZ: No (for now, can enable later)
# 4. Create Database (takes 5-10 minutes)
```

### 2.2 Security Group Configuration
```bash
# After RDS instance is created:
# 1. Note the RDS Endpoint: recruithub-db.xxxxx.us-east-1.rds.amazonaws.com:5432
# 2. Go to RDS → Databases → recruithub-db
# 3. Under "Connectivity & security" → VPC security groups
# 4. Edit Inbound Rules:
#    - Add Rule: PostgreSQL (5432) from EB security group
#    - Or allow: 0.0.0.0/0 during testing (restrict later)
```

### 2.3 Migrate Existing Database
```bash
# Export from Render PostgreSQL
pg_dump -h [render-db-host] -U [render-db-user] -d [render-db-name] > recruithub_backup.sql

# Import to RDS
psql -h [rds-endpoint] -U postgres -d postgres -c "CREATE DATABASE recruithub;"
psql -h [rds-endpoint] -U postgres -d recruithub < recruithub_backup.sql

# Verify tables
psql -h [rds-endpoint] -U postgres -d recruithub -c "\dt"
```

---

## Phase 3: Prepare Django App for EB

### 3.1 Create `.ebextensions` Configuration
Create directory: `.ebextensions/`

**File: `.ebextensions/01_django.config`**
```yaml
option_settings:
  aws:elasticbeanstalk:container:python:
    WSGIPath: auth_project.wsgi:application
    PYTHONPATH: /var/app/current:$PYTHONPATH
  
  aws:elasticbeanstalk:application:environment:
    PYTHONUNBUFFERED: "1"
    DJANGO_SETTINGS_MODULE: auth_project.settings
  
  aws:autoscaling:launchconfiguration:
    IamInstanceProfile: aws-elasticbeanstalk-ec2-role

commands:
  01_migrate:
    command: "source /var/app/venv/*/bin/activate && python manage.py migrate"
    leader_only: true
  02_collectstatic:
    command: "source /var/app/venv/*/bin/activate && python manage.py collectstatic --noinput"
```

### 3.2 Update Django Settings

**File: `auth_project/settings.py`**

```python
# Add/Update these settings:

import os
from pathlib import Path

# Allowed Hosts
ALLOWED_HOSTS = [
    'vakverse.com',
    'www.vakverse.com',
    '*.elasticbeanstalk.com',
    'localhost',
    '127.0.0.1',
]

# Database Configuration
if 'RDS_DB_NAME' in os.environ:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.environ.get('RDS_DB_NAME'),
            'USER': os.environ.get('RDS_USERNAME'),
            'PASSWORD': os.environ.get('RDS_PASSWORD'),
            'HOST': os.environ.get('RDS_HOSTNAME'),
            'PORT': os.environ.get('RDS_PORT', '5432'),
        }
    }
else:
    # Fallback for local development
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# Static Files (S3 Configuration - if using)
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Media Files (if needed)
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Security Settings for Production
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_SECURITY_POLICY = {
        'default-src': ("'self'",),
    }
```

### 3.3 Create `requirements.txt` (if not already complete)
```bash
pip freeze > requirements.txt

# Ensure these are included:
# Django
# psycopg2-binary (for PostgreSQL)
# gunicorn (EB uses this)
# python-decouple (for env vars)
# boto3 (if using S3)
```

### 3.4 Create Python version file

**File: `.python-version`**
```
3.11.0
```

### 3.5 Create Procfile

**File: `Procfile`**
```
web: gunicorn auth_project.wsgi:application
```

---

## Phase 4: Deploy to Elastic Beanstalk

### 4.1 Initialize EB Application
```bash
cd /Users/tapdiyaom/Desktop/RecruitHub

# Initialize EB (run from project root)
eb init -p python-3.11 recruithub-app --region us-east-1

# When prompted:
# - Enter Application Name: recruithub
# - Enter Environment Name: recruithub-prod
# - Select: Load Balanced Environment
```

### 4.2 Create EB Environment
```bash
# Create and deploy
eb create recruithub-prod \
  --instance-type t3.micro \
  --scale 1

# Monitor deployment (takes 5-10 minutes)
eb status
eb logs
```

### 4.3 Set Environment Variables
```bash
# Option 1: Via EB CLI
eb setenv \
  DEBUG=False \
  SECRET_KEY='[your-django-secret-key]' \
  RDS_DB_NAME=recruithub \
  RDS_USERNAME=postgres \
  RDS_PASSWORD='[your-rds-password]' \
  RDS_HOSTNAME=[rds-endpoint] \
  RDS_PORT=5432 \
  AWS_STORAGE_BUCKET_NAME='[if-using-s3]' \
  EMAIL_BACKEND='[your-email-backend]'

# Option 2: Create `.env.prod` and upload via console
# Then use: eb setenv < .env.prod
```

### 4.4 Deploy Application
```bash
# Deploy current code
eb deploy

# Monitor deployment
eb logs -all
```

---

## Phase 5: DNS Configuration (Route 53)

### 5.1 Transfer Domain to Route 53 (Optional)
```bash
# Or keep domain at current registrar and just use Route 53 for DNS

# Go to AWS Console → Route 53:
# 1. Click "Create hosted zone"
# 2. Enter domain: vakverse.com
# 3. Copy the 4 nameservers provided
```

### 5.2 Configure Route 53 Records
```bash
# In Route 53 Console, create these records:

# Record 1: Alias for www
# Name: www.vakverse.com
# Type: A (IPv4 address)
# Alias: Yes
# Alias target: [EB ALB DNS name]
#   (found in EB console → Environment → Load Balancer)
# Routing policy: Simple

# Record 2: Alias for root domain
# Name: vakverse.com
# Type: A (IPv4 address)
# Alias: Yes
# Alias target: [EB ALB DNS name]
# Routing policy: Simple

# Record 3: CNAME for email (if needed)
# Name: mail.vakverse.com
# Type: CNAME
# Value: [email-service-endpoint]
```

### 5.3 Update Domain Registrar Nameservers
```bash
# At your domain registrar (Namecheap, GoDaddy, etc.):
# 1. Go to Domain Management
# 2. Change Nameservers to Route 53 nameservers:
#    ns-123.awsdns-45.com
#    ns-456.awsdns-78.net
#    ns-789.awsdns-01.org
#    ns-012.awsdns-34.com

# Wait 24-48 hours for DNS propagation
# Check: nslookup vakverse.com
```

---

## Phase 6: SSL/TLS Certificate (AWS Certificate Manager)

### 6.1 Request SSL Certificate
```bash
# Via AWS Console → Certificate Manager:
# 1. Click "Request certificate"
# 2. Domain name: vakverse.com, www.vakverse.com
# 3. Validation method: DNS validation
# 4. Add CNAME records to Route 53 (AWS auto-suggests)
# 5. Wait for validation (usually 5-30 minutes)
```

### 6.2 Attach Certificate to ALB
```bash
# Via AWS Console → EC2 → Load Balancers:
# 1. Select EB's ALB
# 2. Listeners → Edit Listener (port 443)
# 3. Select SSL Certificate
# 4. Add HTTP→HTTPS redirect
```

---

## Phase 7: Health & Monitoring

### 7.1 Configure Auto Scaling
```bash
# Via EB Console → Configuration → Auto Scaling:
# Min instances: 1
# Max instances: 3
# Metric: Average CPU (>70% to scale up)
# Cool down: 300 seconds
```

### 7.2 Enable CloudWatch Monitoring
```bash
eb monitoring enable
```

### 7.3 Configure Health Check
```bash
# Via EB Console → Configuration → Load Balancer:
# Health check path: /health/  (or your health check endpoint)
# Healthy threshold: 3
# Unhealthy threshold: 5
# Interval: 30 seconds
# Timeout: 5 seconds
```

---

## Phase 8: Verification & Testing

### 8.1 Test Application
```bash
# Get EB environment URL
eb open

# Test endpoints
curl https://vakverse.com
curl https://www.vakverse.com

# Check admin panel
https://vakverse.com/admin
```

### 8.2 Check Logs
```bash
# Stream real-time logs
eb logs -z

# View specific log files
eb logs --all
```

### 8.3 Database Verification
```bash
# SSH into EC2 instance
eb ssh

# Connect to RDS
psql -h [rds-endpoint] -U postgres -d recruithub -c "SELECT COUNT(*) FROM core_userprofile;"
```

---

## Phase 9: Cleanup & Decommission Render

### 9.1 Backup from Render (if not already done)
```bash
# One final backup
pg_dump -h [render-db-host] -U [render-db-user] -d [render-db-name] > final_backup.sql
```

### 9.2 Decommission Render
```bash
# In Render Dashboard:
# 1. Stop Django web service
# 2. Destroy PostgreSQL database (after confirming all data migrated)
# 3. Remove domain binding
# 4. Delete the project
```

---

## Phase 10: Post-Migration Optimization

### 10.1 Configure Automated Backups
```bash
# In RDS Console:
# 1. Select DB instance
# 2. Modify → Backup retention period: 30 days
# 3. Enable automated backups
# 4. Enable Enhanced monitoring
```

### 10.2 Setup Application Monitoring
```bash
# Create CloudWatch Alarms:
# - CPU > 80%
# - Disk space low
# - Failed deployments
# - Error rate spike
```

### 10.3 Configure Email Service
```bash
# Option 1: AWS SES
# - Verify sending domain in SES Console
# - Update EMAIL_BACKEND in settings.py
# - Request production access (if in sandbox)

# Option 2: Keep third-party (Sendgrid, etc.)
# - Set SMTP credentials in EB environment variables
```

---

## Troubleshooting

### Deployment Fails
```bash
# Check logs
eb logs --all

# Diagnose
eb health

# SSH and check
eb ssh
tail -f /var/log/eb-activity.log
```

### Database Connection Issues
```bash
# Verify RDS security group
# Check EB security group has access to RDS security group
# Verify environment variables are set correctly
eb printenv | grep RDS
```

### Domain Not Resolving
```bash
# Check DNS propagation
nslookup vakverse.com
dig vakverse.com

# Verify Route 53 records are correct
# Check nameserver update at registrar (can take 24-48 hours)
```

### Static Files Not Loading
```bash
# Ensure STATIC_ROOT is set correctly
# Run on EC2:
python manage.py collectstatic --noinput

# Check ALB listener rules for /static/ paths
```

---

## Cost Estimation (Monthly)

| Service | Tier | Est. Cost |
|---------|------|-----------|
| EC2 (t3.micro) | 1 instance | $5-10 |
| RDS (t3.micro) | PostgreSQL | $10-15 |
| ALB | Application LB | $15-20 |
| Data Transfer | Out | $0-10 |
| Route 53 | DNS | $0.50 |
| **TOTAL** | | **$30-55** |

*vs Render: typically $7-12/month for basic tier*

---

## Rollback Plan

If anything goes wrong:
```bash
# Scale down EB
eb scale 0

# Revert to Render temporarily
# Update Route 53 to point to Render's address
# Keep RDS backups for recovery
```

---

## Checklist for Go-Live

- [ ] RDS database created and populated
- [ ] Django settings updated for RDS
- [ ] EB application initialized and deployed
- [ ] Environment variables set in EB
- [ ] SSL certificate created in ACM
- [ ] Route 53 records created
- [ ] Nameservers updated at registrar
- [ ] DNS propagation verified (48 hours)
- [ ] Application tested at vakverse.com
- [ ] Health checks passing
- [ ] Backups configured in RDS
- [ ] CloudWatch monitoring enabled
- [ ] Render resources decommissioned
