# 🔐 Required Keys & Credentials - Complete Summary

## 📋 Quick Overview

To deploy RecruitHub on Render with DynamoDB, you need **2 main sets of credentials:**

1. **AWS Credentials** (for DynamoDB & S3)
2. **Django Settings** (for app security)

Total: **11 CRITICAL keys** + optional email keys

---

## 🔑 CRITICAL KEYS REQUIRED

### **1. AWS_ACCESS_KEY_ID** ✅ MUST HAVE

**What it is:** AWS account identifier  
**Format:** 20 characters, starts with `AKIA`  
**Example:** `AKIA2XXXXXXXXXXXXXXX`

**How to get it:**
1. Go to https://console.aws.amazon.com/iam/
2. Click Users → Create User
3. Name: `recruithub-render`
4. Attach policies:
   - `AmazonDynamoDBFullAccess`
   - `AmazonS3FullAccess`
5. Go to "Security credentials" → "Create access key"
6. Copy the **Access Key ID**

---

### **2. AWS_SECRET_ACCESS_KEY** ✅ MUST HAVE

**What it is:** AWS account password (secret)  
**Format:** 40 random characters  
**Example:** `wJalrXUtnFEMI/K7MDENG+bPxRfiCYEXAMPLEKEY`

**How to get it:** (Same steps as above, copy the **Secret Access Key**)

⚠️ **SAVE THIS IMMEDIATELY** - You can't view it again!  
If you lose it, delete the access key and create a new one.

---

### **3. SECRET_KEY** ✅ MUST HAVE

**What it is:** Django's master security key  
**Format:** 50+ random characters  
**Example:** `3j-$d@_8#k$&$!m+9^!@p_#9$!@#$%^&*()_+{}:"<>?`

**How to generate:**
```bash
# Run this on your computer:
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Or use this online tool (⚠️ less secure):
```
https://www.miniwebtool.com/django-secret-key-generator/
```

---

### **4. AWS_REGION** ✅ MUST HAVE

**What it is:** AWS region where your database lives  
**Format:** Region code  
**Options:**
```
us-east-1        (Virginia, USA) ← RECOMMENDED
us-west-2        (Oregon, USA)
eu-west-1        (Dublin, Ireland)
ap-south-1       (Mumbai, India)
```

**Recommended:** `us-east-1` (cheapest, fastest for US)

---

### **5. AWS_STORAGE_BUCKET_NAME** ✅ MUST HAVE

**What it is:** S3 bucket name for storing files (photos, resumes)  
**Format:** Lowercase letters, numbers, hyphens (must be globally unique)  
**Example:** `recruithub-media-prod-12345`

**How to create:**
1. Go to https://s3.console.aws.amazon.com/
2. Click "Create bucket"
3. Name: `recruithub-media-prod` (add suffix if taken)
4. Region: Same as `AWS_REGION`
5. Block all public access ✅
6. Click "Create"

---

### **6. AWS_S3_REGION_NAME** ✅ MUST HAVE

**What it is:** Region where your S3 bucket is located  
**Should match:** `AWS_REGION`  
**Example:** `us-east-1`

---

### **7. DEBUG** ✅ MUST HAVE

**What it is:** Django debug mode  
**Production value:** `False`  
**Why:** If `True`, shows sensitive error info to hackers

---

### **8. ALLOWED_HOSTS** ✅ MUST HAVE

**What it is:** Domains allowed to access your app  
**Format:** Comma-separated, no spaces  
**Example:** `yourdomain.com,www.yourdomain.com,recruithub.onrender.com`

**Should include:**
- Your main domain
- www version
- Render backup URL (always include!)

---

### **9. USE_DYNAMODB** ✅ MUST HAVE

**What it is:** Enable DynamoDB instead of PostgreSQL  
**Value:** `True`

---

### **10. USE_S3** ✅ MUST HAVE

**What it is:** Enable S3 for file storage  
**Value:** `True`

---

### **11. DYNAMODB_TABLE_PREFIX** ✅ MUST HAVE

**What it is:** Prefix for DynamoDB table names  
**Format:** String ending with `-`  
**Example:** `recruithub-prod-`

**Creates tables like:**
- `recruithub-prod-users`
- `recruithub-prod-user-profiles`
- `recruithub-prod-documents`

---

## 📧 OPTIONAL: Email Configuration

Choose ONE of these options:

### **Option A: Resend (Modern, Recommended)**

**Cost:** Free up to 100 emails/day  
**Setup:**

1. Go to https://resend.com
2. Sign up (free)
3. Verify email
4. Go to API Keys
5. Copy API key

**Environment variables:**
```
EMAIL_BACKEND=resend.django.backend.EmailBackend
RESEND_API_KEY=re_1234567890abcdef1234567890abcdef
```

### **Option B: Gmail SMTP**

**Cost:** Free (if you have Gmail)  
**Setup:**

1. Go to https://myaccount.google.com/apppasswords
2. Select "Mail" and "Windows Computer"
3. Google generates 16-character password
4. Copy it (NOT your Gmail password!)

**Environment variables:**
```
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=yourname@gmail.com
EMAIL_HOST_PASSWORD=xxxx xxxx xxxx xxxx
```

### **Option C: Console (Testing Only)**

**Cost:** Free, but emails print to console  
**Setup:** No keys needed

**Environment variable:**
```
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
```

---

## 🛡️ Optional: Security Settings

### **CSRF_TRUSTED_ORIGINS** (Recommended)

**What it does:** Prevent CSRF attacks on your domain

**Format:**
```
https://yourdomain.com,https://*.yourdomain.com
```

---

### **ADMIN_URL_PATH** (Recommended)

**What it does:** Hide admin panel from bots

**Example:** `admin-randomstring123`  
**Default:** `admin` (easy for hackers to find!)

**Generate random string:**
```bash
python -c "import secrets; print('admin-' + secrets.token_hex(8))"
```

---

## 📊 Summary Table

| Key | Generate? | Required? | Type | Notes |
|-----|-----------|-----------|------|-------|
| `AWS_ACCESS_KEY_ID` | AWS IAM | ✅ YES | Secret | 20 chars, starts with AKIA |
| `AWS_SECRET_ACCESS_KEY` | AWS IAM | ✅ YES | Secret | 40 chars, save immediately! |
| `AWS_REGION` | Choose | ✅ YES | String | `us-east-1` recommended |
| `AWS_STORAGE_BUCKET_NAME` | Create S3 | ✅ YES | String | Globally unique name |
| `AWS_S3_REGION_NAME` | Choose | ✅ YES | String | Same as `AWS_REGION` |
| `SECRET_KEY` | Python script | ✅ YES | Secret | 50+ random chars |
| `DEBUG` | Set manually | ✅ YES | String | `False` for production |
| `ALLOWED_HOSTS` | Set manually | ✅ YES | String | Your domains, comma-separated |
| `USE_DYNAMODB` | Set manually | ✅ YES | String | `True` |
| `USE_S3` | Set manually | ✅ YES | String | `True` |
| `DYNAMODB_TABLE_PREFIX` | Set manually | ✅ YES | String | `recruithub-prod-` |
| `RESEND_API_KEY` | Resend | ❌ NO | Secret | Only if using Resend |
| `EMAIL_HOST_PASSWORD` | Gmail | ❌ NO | Secret | Only if using Gmail |
| `CSRF_TRUSTED_ORIGINS` | Set manually | ❌ NO | String | Your domain for CSRF |
| `ADMIN_URL_PATH` | Generate | ❌ NO | String | Custom admin URL |

---

## 🚀 Quick Checklist: Create All Keys

```bash
# 1. Generate SECRET_KEY
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# 2. Generate ADMIN_URL_PATH
python -c "import secrets; print('admin-' + secrets.token_hex(8))"

# 3. Get AWS credentials
# - Go to AWS console
# - Create IAM user
# - Attach DynamoDB & S3 permissions
# - Generate access key

# 4. Create S3 bucket
# - Go to S3 console
# - Create bucket
# - Same region as AWS_REGION

# 5. Decide on email
# - Use Resend (easiest)
# - Use Gmail (free)
# - Skip for now (console mode)
```

---

## 📝 Sample .env File (for local testing)

**Create a file named `.env` in project root:**

```ini
# Django Settings
SECRET_KEY=<your-generated-secret-key>
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1,yourdomain.com,www.yourdomain.com,recruithub.onrender.com

# AWS Credentials
AWS_ACCESS_KEY_ID=<your-access-key-id>
AWS_SECRET_ACCESS_KEY=<your-secret-access-key>
AWS_REGION=us-east-1

# DynamoDB
USE_DYNAMODB=True
DYNAMODB_TABLE_PREFIX=recruithub-dev-

# S3
USE_S3=True
AWS_STORAGE_BUCKET_NAME=recruithub-media-dev
AWS_S3_REGION_NAME=us-east-1

# Email (choose one)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
# OR
# EMAIL_BACKEND=resend.django.backend.EmailBackend
# RESEND_API_KEY=re_xxxxx

# Optional
CSRF_TRUSTED_ORIGINS=https://yourdomain.com,https://*.yourdomain.com
ADMIN_URL_PATH=admin-randomstring123
ENABLE_RATE_LIMITING=True
```

⚠️ **NEVER COMMIT .env file to Git!** Add to `.gitignore`

---

## 🔒 Security Reminders

1. **Don't share access keys** - They're like passwords
2. **Use different keys for dev/prod** - Create separate AWS users
3. **Rotate keys every 6 months** - Delete old ones
4. **Use AWS key rotation policy** - Automatic rotation is better
5. **Monitor AWS usage** - Check CloudWatch for suspicious activity
6. **Enable 2FA on AWS account** - Use Google Authenticator
7. **Never hardcode secrets** - Always use environment variables
8. **Use custom admin URL** - `admin` is too obvious
9. **Keep ALLOWED_HOSTS specific** - Don't use wildcards all over
10. **Test locally before deploying** - Use local DynamoDB for testing

---

## 🆘 If You Lose a Key

### **Lost AWS Access Key?**
1. Go to IAM → Users → recruithub-render
2. Security credentials tab
3. Delete the old key
4. Create new access key
5. Update Render environment variables

### **Lost SECRET_KEY?**
1. Generate a new one (same command)
2. Update Render environment variable
3. Users will be logged out (session invalidation)

### **Lost Resend API Key?**
1. Go to Resend dashboard
2. Delete old key
3. Create new key

### **Lost S3 bucket?**
1. Go to S3 console
2. Create new bucket with different name
3. Update `AWS_STORAGE_BUCKET_NAME` in Render
4. Upload existing files to new bucket

---

## ✅ Final Validation

Before going live, verify:

- [ ] All CRITICAL keys generated/obtained (11 total)
- [ ] AWS credentials are from dedicated IAM user (not root)
- [ ] S3 bucket created and blocks public access
- [ ] `DEBUG=False` in production
- [ ] `ALLOWED_HOSTS` includes your domain
- [ ] `.env` file NOT in Git (check `.gitignore`)
- [ ] Keys are different for dev and production
- [ ] Email is configured (at least console mode)
- [ ] SECRET_KEY is secure and random
- [ ] You have a backup of all credentials

