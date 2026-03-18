# 🚀 RecruitHub - Render Deployment with DynamoDB Guide

## ✅ Deployment Checklist

This guide covers everything needed to deploy RecruitHub on Render using DynamoDB instead of PostgreSQL.

---

## 📋 Table of Contents

1. [Current Setup](#current-setup)
2. [Changes Required](#changes-required)
3. [All Environment Variables Needed](#all-environment-variables-needed)
4. [Step-by-Step Deployment](#step-by-step-deployment)

---

## 📊 Current Setup

**Current Database:** PostgreSQL (relational) → `dj_database_url`  
**Current Hosting:** Render (compatible ✅)  
**Current Storage:** AWS S3 (media files)  
**Current Auth:** Django Auth + Custom models  

---

## ⚠️ Changes Required for DynamoDB

### **Issue:** Django ORM is built for SQL databases

Django's ORM expects:
- Tables/schemas
- SQL queries
- Foreign key relationships
- Transactions (ACID)

DynamoDB is:
- NoSQL (document-based)
- Key-value store
- Limited query capabilities
- Eventually consistent

### **Solution: Use PynamoDB**

**PynamoDB** is a Python library that provides a Django-like ORM interface for DynamoDB.

---

## 🔧 All Changes Needed

### 1. **Update requirements.txt**

Add DynamoDB support:

```bash
# Add these to requirements.txt:
pynamodb==6.1.1          # DynamoDB ORM for Python
django-environ==0.11.2   # Better environment variable handling
```

Remove:
```bash
psycopg2-binary>=2.9.10  # PostgreSQL driver (no longer needed)
dj-database-url>=2.1.0   # SQL database URL parser (no longer needed)
```

### 2. **Update settings.py**

Remove PostgreSQL configuration and simplify database settings:

```python
# OLD DATABASE CONFIG (REMOVE):
# DATABASES = {
#     'default': dj_database_url.config(...)
# }

# NEW CONFIG (ADD):
# For DynamoDB, we don't use Django's traditional DATABASES setting
# We'll manage DynamoDB connections via boto3/pynamodb separately
```

### 3. **Create DynamoDB Models**

Create a new file: `core/dynamodb_models.py`

This will replace Django ORM models with PynamoDB models.

### 4. **Update Views**

Change all views to use DynamoDB models instead of Django ORM.

### 5. **Update Middleware for Sessions**

Configure session storage to use AWS DynamoDB Tables.

---

## 🔐 ALL Environment Variables Required

### **CRITICAL - AWS Credentials** ⚠️

```
AWS_ACCESS_KEY_ID=AKIA...XXXXXXXXXX
AWS_SECRET_ACCESS_KEY=your-secret-access-key-here
AWS_REGION=us-east-1
```

**How to get these:**
1. Go to AWS Console → IAM → Users
2. Create a new user named `recruithub-render`
3. Attach policy: `AmazonDynamoDBFullAccess` + `S3FullAccess`
4. Generate Access Keys (copy both)

---

### **CRITICAL - Django Settings** ⚠️

```
SECRET_KEY=your-secure-random-key-here
DEBUG=False
ALLOWED_HOSTS=your-domain.com,www.your-domain.com,recruithub.onrender.com
```

---

### **CRITICAL - Database** ⚠️

```
USE_DYNAMODB=True
USING_AWS_DYNAMODB=True
```

---

### **Database Backup (Optional)** 

```
DYNAMODB_BACKUP_ENABLED=False  # Set to True to enable backups
AWS_DYNAMODB_TABLE_PREFIX=recruithub-prod-
```

---

### **OPTIONAL - Email Configuration**

```
EMAIL_BACKEND=resend.django.backend.EmailBackend
RESEND_API_KEY=re_your_resend_api_key

# Alternative: Gmail SMTP
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=app-specific-password
```

---

### **OPTIONAL - Security/Admin**

```
CSRF_TRUSTED_ORIGINS=https://your-domain.com,https://*.your-domain.com
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
ADMIN_URL_PATH=admin-randomstring123
```

---

### **OPTIONAL - Rate Limiting**

```
ENABLE_RATE_LIMITING=True
RATE_LIMIT_LOGIN_ENABLED=True
RATE_LIMIT_LOGIN_ATTEMPTS=5
RATE_LIMIT_LOGIN_WINDOW=900
RATE_LIMIT_REGISTRATION_ENABLED=True
RATE_LIMIT_REGISTRATION_ATTEMPTS=3
RATE_LIMIT_REGISTRATION_WINDOW=3600
RATE_LIMIT_OTP_ENABLED=True
RATE_LIMIT_OTP_ATTEMPTS=5
RATE_LIMIT_OTP_WINDOW=600
```

---

## 📝 Complete Environment Variables Summary

### **Render Dashboard: Add these as environment variables**

| Variable | Value | Required? | Type |
|----------|-------|-----------|------|
| `SECRET_KEY` | Random secure string | ✅ YES | Secret |
| `DEBUG` | `False` | ✅ YES | String |
| `ALLOWED_HOSTS` | `yourdomain.com,www.yourdomain.com,recruithub.onrender.com` | ✅ YES | String |
| `AWS_ACCESS_KEY_ID` | From AWS IAM | ✅ YES | Secret |
| `AWS_SECRET_ACCESS_KEY` | From AWS IAM | ✅ YES | Secret |
| `AWS_REGION` | `us-east-1` | ✅ YES | String |
| `USE_DYNAMODB` | `True` | ✅ YES | String |
| `USING_AWS_DYNAMODB` | `True` | ✅ YES | String |
| `USE_S3` | `True` | ✅ YES | String |
| `AWS_STORAGE_BUCKET_NAME` | Your S3 bucket name | ✅ YES | String |
| `AWS_S3_REGION_NAME` | `us-east-1` | ✅ YES | String |
| `EMAIL_HOST` | `smtp.gmail.com` | ❌ NO | String |
| `EMAIL_PORT` | `587` | ❌ NO | String |
| `EMAIL_HOST_USER` | Your email | ❌ NO | String |
| `EMAIL_HOST_PASSWORD` | App password | ❌ NO | Secret |
| `CSRF_TRUSTED_ORIGINS` | Your domain | ❌ NO | String |
| `ADMIN_URL_PATH` | Random path | ❌ NO | String |

---

## 🚀 Step-by-Step Deployment

### **Step 1: Prepare AWS Infrastructure**

1. **Create DynamoDB Tables:**
   ```bash
   # Tables needed:
   - recruithub-prod-users
   - recruithub-prod-user-profiles
   - recruithub-prod-documents
   - recruithub-prod-notes
   - recruithub-prod-hr-profiles
   - recruithub-prod-email-otps
   - recruithub-prod-rate-limits
   ```

2. **Create S3 Bucket:**
   ```bash
   # Bucket name: recruithub-media-prod
   # Enable CORS for media file uploads
   ```

3. **Create IAM User with Permissions:**
   - Go to AWS IAM console
   - Create user: `recruithub-render`
   - Attach policies:
     - `AmazonDynamoDBFullAccess`
     - `AmazonS3FullAccess`
   - Generate access keys

---

### **Step 2: Update Application Code**

1. Update `requirements.txt` (add PynamoDB, remove psycopg2)
2. Create `core/dynamodb_models.py` with PynamoDB models
3. Update `auth_project/settings.py` for DynamoDB
4. Update all views to use DynamoDB models
5. Update Procfile for DynamoDB initialization

---

### **Step 3: Configure Render**

1. Push code to GitHub
2. Go to Render.com
3. Create new Web Service
4. Connect GitHub repository
5. Configure environment variables (see table above)
6. Set build command: `pip install -r requirements.txt`
7. Set start command: `gunicorn auth_project.wsgi:application --bind 0.0.0.0:$PORT`

---

### **Step 4: Initialize DynamoDB Tables**

Create management command: `core/management/commands/init_dynamodb.py`

Run from Render Procfile release phase:
```
release: python manage.py init_dynamodb
```

---

## 🔑 Quick Reference: Generate Required Keys

### **SECRET_KEY** (Django Security)
```python
from django.core.management.utils import get_random_secret_key
print(get_random_secret_key())
```

### **AWS Keys** (from IAM Console)
- Visit: https://console.aws.amazon.com/iam/
- Create user → Generate access key

### **Email Password** (for Gmail)
- Visit: https://myaccount.google.com/apppasswords
- Generate app-specific password

---

## ⚡ Important Notes

### **Migration Strategy**

Since you're using DynamoDB (completely different from PostgreSQL):
1. You CANNOT use Django migrations (`manage.py migrate`)
2. You need to create DynamoDB tables separately
3. Export existing PostgreSQL data → Import to DynamoDB
4. Keep both databases during transition (if needed)

### **Rate Limiting in DynamoDB**

Instead of `IPRateLimit` model (SQL), use DynamoDB table:
```
Table: recruithub-rate-limits
- Key: IP address
- Attributes: attempt count, timestamp, endpoint
```

### **Sessions in DynamoDB**

Configure Django sessions to use DynamoDB:
```python
SESSION_ENGINE = 'core.dynamodb_session_backend'
SESSION_DYNAMODB_TABLE = 'recruithub-sessions'
```

---

## 📊 DynamoDB Pricing

- **Per month (estimate):**
  - Write capacity: 25 units → ~$13
  - Read capacity: 100 units → ~$13
  - Storage: 100GB → ~$25
  - **Total: ~$51/month** (smallest tier)

Render free tier does NOT include DynamoDB - you pay AWS separately.

---

## 🧪 Testing Before Deployment

1. **Local testing with DynamoDB local:**
   ```bash
   # Install DynamoDB local
   # Test models locally
   python manage.py shell
   from core.dynamodb_models import User
   # Create test records
   ```

2. **Test with AWS DynamoDB (test tables):**
   - Create duplicate tables with `-test` suffix
   - Run full test suite
   - Verify all CRUD operations work

---

## 🆘 Troubleshooting

| Issue | Solution |
|-------|----------|
| "InvalidAttributeType" error | DynamoDB attribute type mismatch - check schema |
| "AccessDenied" from AWS | Verify IAM user has correct permissions |
| Slow reads/writes | Provision higher read/write capacity units |
| Data not persisting | Check if table exists in correct region |

---

## ✅ Final Checklist

Before deploying to Render:

- [ ] AWS account created
- [ ] DynamoDB tables created
- [ ] S3 bucket created with CORS enabled
- [ ] IAM user created with AWS keys
- [ ] requirements.txt updated
- [ ] settings.py updated for DynamoDB
- [ ] DynamoDB models created
- [ ] All views updated to use DynamoDB models
- [ ] Environment variables configured in Render
- [ ] git push to GitHub
- [ ] Render deployment triggered
- [ ] Test all user flows (signup, profile, documents)
- [ ] Verify S3 uploads working
- [ ] Check CloudWatch logs for errors

---

## 📞 Need Help?

See these files for more info:
- [AWS_EB_MIGRATION_GUIDE.md](AWS_EB_MIGRATION_GUIDE.md) - AWS migration reference
- [ENVIRONMENT_VARIABLES.md](ENVIRONMENT_VARIABLES.md) - Detailed env var docs
- [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) - General deployment guide

