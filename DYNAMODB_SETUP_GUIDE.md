# DynamoDB + S3 Setup Guide for RecruitHub

## Architecture Overview

```
┌─────────────────────────────────────┐
│     Django Application              │
├─────────────────────────────────────┤
│  Profile Data (UserProfile, etc)    │  ──────────> DynamoDB (NoSQL)
│  HR Data (HRProfiles)               │
│  Notes & Documents metadata         │
├─────────────────────────────────────┤
│  Profile Photos & Resumes (Files)   │  ──────────> S3 (File Storage)
│  Documents (Files)                  │              (Save URLs in DynamoDB)
└─────────────────────────────────────┘
```

## Current Status

✅ **Already Configured:**
- DynamoDB models defined in `core/dynamodb_models.py`
- S3 storage configured in settings (`USE_S3` flag)
- File upload paths secured with UUID

⚠️ **Currently Using:**
- SQLite for development (local)
- Django ORM (SQL) for all data

## Step 1: AWS DynamoDB Setup

### 1.1 Create DynamoDB Tables

You need to create the following tables in AWS DynamoDB:

```
TABLE 1: recruithub-users
├─ Partition Key: user_id (String)
└─ Attributes: email, username, password_hash, first_name, etc.

TABLE 2: recruithub-user-profiles
├─ Partition Key: user_id (String)
└─ Attributes: profile_photo_url, resume_url, education, professional

TABLE 3: recruithub-hr-profiles
├─ Partition Key: user_id (String)
└─ Attributes: company_name, designation, is_approved, approval_token

TABLE 4: recruithub-documents
├─ Partition Key: user_id (String)
├─ Sort Key: document_id (String)
└─ Attributes: title, file_url, file_type, uploaded_at

TABLE 5: recruithub-notes
├─ Partition Key: user_id (String)
├─ Sort Key: note_id (String)
└─ Attributes: title, content, created_at

TABLE 6: recruithub-email-otps
├─ Partition Key: email (String)
└─ Attributes: otp, is_verified, created_at, attempts
```

### 1.2 Create Tables via AWS CLI

```bash
# User Table
aws dynamodb create-table \
  --table-name recruithub-users \
  --attribute-definitions AttributeName=user_id,AttributeType=S \
  --key-schema AttributeName=user_id,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST \
  --region us-east-1

# User Profile Table
aws dynamodb create-table \
  --table-name recruithub-user-profiles \
  --attribute-definitions AttributeName=user_id,AttributeType=S \
  --key-schema AttributeName=user_id,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST \
  --region us-east-1

# HR Profile Table
aws dynamodb create-table \
  --table-name recruithub-hr-profiles \
  --attribute-definitions AttributeName=user_id,AttributeType=S \
  --key-schema AttributeName=user_id,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST \
  --region us-east-1

# Documents Table
aws dynamodb create-table \
  --table-name recruithub-documents \
  --attribute-definitions \
    AttributeName=user_id,AttributeType=S \
    AttributeName=document_id,AttributeType=S \
  --key-schema \
    AttributeName=user_id,KeyType=HASH \
    AttributeName=document_id,KeyType=RANGE \
  --billing-mode PAY_PER_REQUEST \
  --region us-east-1

# Notes Table
aws dynamodb create-table \
  --table-name recruithub-notes \
  --attribute-definitions \
    AttributeName=user_id,AttributeType=S \
    AttributeName=note_id,AttributeType=S \
  --key-schema \
    AttributeName=user_id,KeyType=HASH \
    AttributeName=note_id,KeyType=RANGE \
  --billing-mode PAY_PER_REQUEST \
  --region us-east-1

# Email OTP Table
aws dynamodb create-table \
  --table-name recruithub-email-otps \
  --attribute-definitions AttributeName=email,AttributeType=S \
  --key-schema AttributeName=email,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST \
  --region us-east-1
```

## Step 2: Environment Configuration

Update your `.env` file:

```bash
# ===== DynamoDB Configuration =====
USE_DYNAMODB=True
AWS_ACCESS_KEY_ID=your_access_key_here
AWS_SECRET_ACCESS_KEY=your_secret_key_here
AWS_REGION=us-east-1
DYNAMODB_TABLE_PREFIX=recruithub-

# ===== S3 Configuration (for files) =====
USE_S3=True
AWS_STORAGE_BUCKET_NAME=your-recruithub-bucket
AWS_S3_REGION_NAME=us-east-1

# ===== Keep existing config =====
DEBUG=True
RESEND_API_KEY=re_Pf3zovwi_QQA8g55EAQ4kg7AnPnb1HtpX
DEFAULT_FROM_EMAIL=noreply@vakverse.com
```

## Step 3: Update Django Settings

Modify `auth_project/settings.py` to support DynamoDB:

```python
# At the end of settings.py, add:

# ===== DynamoDB Configuration =====
USE_DYNAMODB = os.environ.get('USE_DYNAMODB', 'False').lower() == 'true'

if USE_DYNAMODB:
    # DynamoDB models will be used instead of Django ORM
    # Update code to import from core.dynamodb_models
    DATABASES['default'] = {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',  # Keep for Django internals only (User auth)
    }
    
    DYNAMODB_CONFIG = {
        'region': os.environ.get('AWS_REGION', 'us-east-1'),
        'table_prefix': os.environ.get('DYNAMODB_TABLE_PREFIX', 'recruithub-'),
    }
```

## Step 4: Update Views to Use DynamoDB

**For now**, keep using SQLite locally, but prepare code for DynamoDB:

### Convert to DynamoDB-compatible queries

**Before (Django ORM):**
```python
# Get user profile
profile = UserProfile.objects.get(user=request.user)
profile.skills = "Python, Django"
profile.save()
```

**After (DynamoDB with pynamodb):**
```python
# Get user profile
from core.dynamodb_models import UserProfile as DDBUserProfile

profile = DDBUserProfile.get(request.user.id)
profile.professional.skills = ["Python", "Django"]
profile.save()
```

## Step 5: File Uploads with S3

Files (profile photos, resumes) are stored in S3. URLs are saved in DynamoDB:

```python
# Upload to S3 (happens automatically via Django)
user_profile.profile_photo = upload_file  # Django handles S3 upload

# In DynamoDB, store the S3 URL:
dynamodb_profile.profile_photo_url = user_profile.profile_photo.url
```

## Step 6: Local Development Options

### Option A: Use SQLite Locally + DynamoDB in Production
```
Development: SQLite (Django ORM)
Production: DynamoDB + S3
```

**Setup:**
- `.env`: `USE_DYNAMODB=False` (development)
- Keep current Django models
- Deploy with settings that enable DynamoDB

### Option B: Use DynamoDB Locally with LocalStack

LocalStack provides local DynamoDB for testing:

```bash
# Install LocalStack
pip install localstack localstack-cli

# Start LocalStack
localstack start

# Create tables pointing to local DynamoDB
export AWS_ENDPOINT_URL=http://localhost:4566
```

### Option C: Use AWS DynamoDB Cloud for Development
```bash
# Configure AWS credentials
aws configure

# Tables in cloud, but cheaper on-demand pricing
```

## Migration Strategy

### Phase 1: Keep Both (Current)
- Use SQLite + Django ORM
- Have DynamoDB models ready
- Store file URLs in S3

### Phase 2: Gradual Migration
- Start storing new profiles in DynamoDB
- Keep existing data in SQLite
- Add abstractions to switch backends

### Phase 3: Full Migration
- Migrate all data from SQLite to DynamoDB
- Remove Django ORM models (except User/auth)
- Use DynamoDB exclusively

## Implementation Timeline

**Week 1:**
1. Create DynamoDB tables
2. Configure AWS credentials
3. Test pynamodb connection

**Week 2:**
1. Update views to use DynamoDB models
2. Test profile creation/updates
3. Test file uploads to S3

**Week 3:**
1. Migrate existing data
2. Switch to DynamoDB in production
3. Monitor and optimize

## Files to Update

```
core/views.py              - Update to use DynamoDB models
core/forms.py              - Minor adjustments for DynamoDB
core/admin.py              - Update admin interface
auth_project/settings.py   - Add DynamoDB config
auth_project/urls.py       - No changes needed
core/models.py             - Keep for Django auth only
core/dynamodb_models.py    - READY TO USE
```

## Testing DynamoDB Connection

```python
# test_dynamodb.py
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'auth_project.settings')
sys.path.insert(0, '/Users/tapdiyaom/Desktop/recruit-hub/RecruitHub')

django.setup()

from core.dynamodb_models import User as DDBUser
from datetime import datetime
import uuid

# Test 1: Create a user
try:
    user = DDBUser(
        user_id=str(uuid.uuid4()),
        email="test@example.com",
        username="testuser",
        password_hash="hashed_password",
        first_name="Test",
        created_at=datetime.utcnow()
    )
    user.save()
    print("✅ User created successfully")
except Exception as e:
    print(f"❌ Error: {e}")

# Test 2: Retrieve user
try:
    user = DDBUser.get(user.user_id)
    print(f"✅ User retrieved: {user.username}")
except Exception as e:
    print(f"❌ Error: {e}")
```

## FAQ

**Q: Do I need to keep both SQLite and DynamoDB?**
A: Yes, initially. SQLite for Auth (User), DynamoDB for Profile data.

**Q: Can I store files in DynamoDB instead of S3?**
A: Not recommended. DynamoDB has item limits (400KB) and is expensive for large files.

**Q: How much will DynamoDB cost?**
A: On-demand pricing: $1.25/million reads, $1.25/million writes. Typically $5-20/month for small apps.

**Q: Is DynamoDB faster than SQLite?**
A: Yes. Consistent latency (ms), built-in scaling, global replication.

**Q: Can I revert to SQLite later?**
A: Yes, data migration tools exist. But DynamoDB is better for production.

## Next Steps

1. Create AWS account (if needed)
2. Set up DynamoDB tables using AWS CLI commands above
3. Configure `.env` with AWS credentials
4. Contact me to update views.py for DynamoDB operations

---

**Questions?** This guide covers the complete setup!
