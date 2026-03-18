# 🔑 Services & Keys - Quick Lookup Table

## 📊 All Keys at a Glance

### **Email Service Keys**

#### **Option 1: Resend (Recommended)**

| Key Name | Value | Required | Type | Where to Get |
|----------|-------|----------|------|--------------|
| `RESEND_API_KEY` | `re_1a2b3c4d5e6f...` | ✅ | Secret | https://resend.com/api-keys |
| `DEFAULT_FROM_EMAIL` | `noreply@yourdomain.com` | ✅ | String | Your domain |

**Total Keys: 2**  
**Cost: FREE tier (100/day) or $20/month**  
**Setup Time: 5 minutes**

---

#### **Option 2: Gmail SMTP**

| Key Name | Value | Required | Type | Where to Get |
|----------|-------|----------|------|--------------|
| `EMAIL_BACKEND` | `django.core.mail.backends.smtp.EmailBackend` | ✅ | String | Built-in |
| `EMAIL_HOST` | `smtp.gmail.com` | ✅ | String | Built-in |
| `EMAIL_PORT` | `587` | ✅ | Integer | Built-in |
| `EMAIL_HOST_USER` | `your-email@gmail.com` | ✅ | String | Your Gmail |
| `EMAIL_HOST_PASSWORD` | `xxxx xxxx xxxx xxxx` | ✅ | Secret | https://myaccount.google.com/apppasswords |
| `DEFAULT_FROM_EMAIL` | `your-email@gmail.com` | ✅ | String | Your Gmail |

**Total Keys: 6**  
**Cost: FREE**  
**Setup Time: 10 minutes**

---

#### **Option 3: Console (Development Only)**

| Key Name | Value | Required | Type | Where to Get |
|----------|-------|----------|------|--------------|
| `EMAIL_BACKEND` | `django.core.mail.backends.console.EmailBackend` | ✅ | String | Built-in |

**Total Keys: 1**  
**Cost: FREE**  
**Setup Time: 1 minute**

---

### **AWS Services Keys**

#### **DynamoDB (Database)**

| Key Name | Value | Required | Type | Where to Get | Format |
|----------|-------|----------|------|--------------|--------|
| `AWS_ACCESS_KEY_ID` | `AKIA2XXXXXXXXXXXXX` | ✅ | Secret | https://console.aws.amazon.com/iam/ | 20 chars, starts with AKIA |
| `AWS_SECRET_ACCESS_KEY` | `wJalrXUtnFEMI/K7MDENGbPxRfiCYEX...` | ✅ | Secret | https://console.aws.amazon.com/iam/ | 40 chars, random, SAVE IMMEDIATELY |
| `AWS_REGION` | `us-east-1` | ✅ | String | Configure | Region code (us-east-1, eu-west-1, etc) |
| `DYNAMODB_TABLE_PREFIX` | `recruithub-prod-` | ✅ | String | Configure | Any string ending with `-` |
| `USE_DYNAMODB` | `True` | ✅ | Boolean | Configure | `True` or `False` |

**Total Keys: 5**  
**Cost: ~$15/month**  
**Setup Time: 20 minutes**

---

#### **S3 (File Storage)**

| Key Name | Value | Required | Type | Where to Get | Notes |
|----------|-------|----------|------|--------------|-------|
| `AWS_ACCESS_KEY_ID` | (same as DynamoDB) | ✅ | Secret | https://console.aws.amazon.com/iam/ | Shared with DynamoDB |
| `AWS_SECRET_ACCESS_KEY` | (same as DynamoDB) | ✅ | Secret | https://console.aws.amazon.com/iam/ | Shared with DynamoDB |
| `AWS_STORAGE_BUCKET_NAME` | `recruithub-media-prod` | ✅ | String | https://s3.console.aws.amazon.com/ | Create bucket first |
| `AWS_S3_REGION_NAME` | `us-east-1` | ✅ | String | Configure | Should match AWS_REGION |
| `USE_S3` | `True` | ✅ | Boolean | Configure | `True` or `False` |

**Total Keys: 5 (but 2 shared with DynamoDB)**  
**Cost: ~$2/month**  
**Setup Time: 10 minutes**

---

### **Django Security Keys**

| Key Name | Value | Required | Type | Where to Get | Format |
|----------|-------|----------|------|--------------|--------|
| `SECRET_KEY` | `3j-$d@_8#k$&$!m+9^!@p_#9...` | ✅ | Secret | Generate with Python | 50+ random characters |
| `DEBUG` | `False` | ✅ | Boolean | Configure | ALWAYS `False` in production |
| `ALLOWED_HOSTS` | `yourdomain.com,www.yourdomain.com,recruithub.onrender.com` | ✅ | String | Configure | Comma-separated domains |
| `CSRF_TRUSTED_ORIGINS` | `https://yourdomain.com,https://*.yourdomain.com` | ⚠️ | String | Configure | Recommended for security |
| `ADMIN_URL_PATH` | `admin-randomstring123` | ⚠️ | String | Generate with Python | Optional but recommended |

**Total Keys: 5 (3 critical, 2 optional)**  
**Cost: FREE**  
**Setup Time: 5 minutes**

---

## 📈 Total Keys Required

### **Minimum Setup (Email + AWS)**

```
11 CRITICAL KEYS (Always needed):
├─ 2 Django security: SECRET_KEY, DEBUG
├─ 2 Django config: ALLOWED_HOSTS, (1 more)
├─ 2 AWS general: AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY
├─ 1 AWS DynamoDB: AWS_REGION
├─ 1 DynamoDB config: DYNAMODB_TABLE_PREFIX
├─ 2 DynamoDB control: USE_DYNAMODB, USE_S3
└─ (plus S3 bucket config but uses AWS keys)

PLUS pick ONE email option:
├─ Option A (Resend): 2 keys
├─ Option B (Gmail): 6 keys
└─ Option C (Console): 1 key

OPTIONAL (Recommended):
├─ CSRF_TRUSTED_ORIGINS: 1 key
└─ ADMIN_URL_PATH: 1 key
```

### **Complete Count by Service**

| Service | Keys Needed | Keys Total | Shared Keys |
|---------|-------------|-----------|-------------|
| Django Security | 3 | 3 | None |
| Email (Resend) | 2 | 2 | None |
| Email (Gmail) | 6 | 6 | None |
| Email (Console) | 1 | 1 | None |
| AWS Identity | 2 | 2 | Shared with DynamoDB & S3 |
| DynamoDB | 3 | 3 | Shares 2 with AWS Identity |
| S3 | 3 | 3 | Shares 2 with AWS Identity |
| **Total (with Resend)** | | **17** | -2 (shared) = **15 unique** |
| **Total (with Gmail)** | | **21** | -2 (shared) = **19 unique** |
| **Total (with Console)** | | **12** | -2 (shared) = **10 unique** |

---

## 🎯 Key Decision Matrix

### **Which Email Should I Choose?**

```
┌─────────────────────────────────────────────────────────────┐
│                  WHICH EMAIL SERVICE?                       │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  CHOOSE RESEND IF:                                          │
│  ✅ You want professional email delivery                    │
│  ✅ You want built-in analytics                            │
│  ✅ You want webhooks support                              │
│  ✅ You want the fastest setup                             │
│  ✅ You don't mind paying $20/month (or use free tier)    │
│                                                              │
│  CHOOSE GMAIL IF:                                           │
│  ✅ You already have Gmail account                         │
│  ✅ You want to send emails for FREE                       │
│  ✅ You don't need analytics                               │
│  ✅ You have low email volume                              │
│  ⚠️ Emails might be slow or rate-limited                   │
│                                                              │
│  CHOOSE CONSOLE IF:                                         │
│  ✅ You're just testing/developing                         │
│  ✅ You're not ready to send real emails yet               │
│  ✅ You want to see emails in logs instead                 │
│  ❌ NOT for production                                      │
│  ❌ NOT for real users                                      │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 📋 Rendering Setup: Exact Environment Variables

### **Copy This Template**

```env
# DJANGO CORE (3 critical)
SECRET_KEY=<FROM-PYTHON-GENERATE-COMMAND>
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com,recruithub.onrender.com

# AWS (2 from IAM - SHARED)
AWS_ACCESS_KEY_ID=AKIA2XXXXXXXXXXXXXXXXXX
AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG+bPxRfiCYEX...

# DYNAMODB (3 config)
AWS_REGION=us-east-1
DYNAMODB_TABLE_PREFIX=recruithub-prod-
USE_DYNAMODB=True

# S3 (2 config + 2 AWS shared above)
USE_S3=True
AWS_STORAGE_BUCKET_NAME=recruithub-media-prod
AWS_S3_REGION_NAME=us-east-1

# EMAIL - Choose ONE block below:

# OPTION A: Resend (Recommended)
RESEND_API_KEY=re_1a2b3c4d5e6f...
DEFAULT_FROM_EMAIL=noreply@yourdomain.com

# OPTION B: Gmail
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=xxxx xxxx xxxx xxxx
DEFAULT_FROM_EMAIL=your-email@gmail.com

# OPTION C: Console (Dev only)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend

# OPTIONAL: Security
CSRF_TRUSTED_ORIGINS=https://yourdomain.com,https://*.yourdomain.com
ADMIN_URL_PATH=admin-<RANDOM-STRING>
```

---

## 🆘 Which Keys Are Critical?

### **You CANNOT deploy without these (11 keys):**

```
1. SECRET_KEY                    ← Django security
2. DEBUG                         ← Security setting
3. ALLOWED_HOSTS                 ← Host validation
4. AWS_ACCESS_KEY_ID             ← AWS auth
5. AWS_SECRET_ACCESS_KEY         ← AWS auth
6. AWS_REGION                    ← AWS config
7. DYNAMODB_TABLE_PREFIX         ← DB config
8. USE_DYNAMODB                  ← Enable DB
9. AWS_STORAGE_BUCKET_NAME       ← S3 config
10. AWS_S3_REGION_NAME            ← S3 config
11. USE_S3                         ← Enable S3
```

### **You SHOULD set one of these (email - pick 1 option):**

**Option A:**
```
- RESEND_API_KEY
- DEFAULT_FROM_EMAIL
```

**Option B:**
```
- EMAIL_BACKEND
- EMAIL_HOST
- EMAIL_PORT
- EMAIL_HOST_USER
- EMAIL_HOST_PASSWORD
- DEFAULT_FROM_EMAIL
```

**Option C:**
```
- EMAIL_BACKEND
```

### **Nice to have (2 keys):**

```
- CSRF_TRUSTED_ORIGINS     ← Recommended for security
- ADMIN_URL_PATH           ← Recommended for security
```

---

## 🔄 Where Each Key is Used

```
┌─────────────────────────────────────┐
│      WHERE KEYS ARE USED            │
├─────────────────────────────────────┤
│                                     │
│  SECRET_KEY                         │
│  └─ Django: sessions, CSRF, auth   │
│                                     │
│  ALLOWED_HOSTS                      │
│  └─ Django: request validation      │
│                                     │
│  AWS_ACCESS_KEY_ID + SECRET         │
│  ├─ DynamoDB: connect & read/write  │
│  ├─ S3: upload/download files       │
│  └─ IAM: verify identity            │
│                                     │
│  AWS_REGION                         │
│  └─ DynamoDB: locate tables         │
│                                     │
│  DYNAMODB_TABLE_PREFIX              │
│  └─ DynamoDB: name all tables       │
│                                     │
│  AWS_STORAGE_BUCKET_NAME            │
│  └─ S3: locate bucket               │
│                                     │
│  EMAIL_* (Resend or Gmail)          │
│  └─ Email: send all emails          │
│                                     │
│  CSRF_TRUSTED_ORIGINS               │
│  └─ Django: CSRF protection         │
│                                     │
│  ADMIN_URL_PATH                     │
│  └─ Django: custom admin URL        │
│                                     │
└─────────────────────────────────────┘
```

---

## ⏱️ Time Estimate to Get All Keys

| Task | Time |
|------|------|
| Generate SECRET_KEY | 1 min |
| Generate ADMIN_URL_PATH | 1 min |
| Create AWS account | 5 min |
| Create IAM user | 5 min |
| Generate AWS keys | 2 min |
| Create S3 bucket | 5 min |
| Setup email (Resend) | 5 min |
| **Total with Resend** | **24 min** |
| Setup email (Gmail) | 10 min |
| **Total with Gmail** | **29 min** |
| Setup email (Console) | 0 min |
| **Total with Console** | **19 min** |

---

## ✅ Final Checklist

Before deploying, have ready:

```
Email Service:
☐ Chosen email option (Resend/Gmail/Console)
☐ Got all keys for that option

AWS (DynamoDB + S3):
☐ AWS account created
☐ IAM user created
☐ AWS_ACCESS_KEY_ID copied
☐ AWS_SECRET_ACCESS_KEY saved securely
☐ S3 bucket created
☐ S3 bucket blocks public access

Django:
☐ SECRET_KEY generated
☐ DEBUG set to False
☐ ALLOWED_HOSTS set to your domain
☐ Optional: CSRF_TRUSTED_ORIGINS configured
☐ Optional: ADMIN_URL_PATH generated

Render:
☐ 11 critical keys entered in Environment tab
☐ Email keys (1 option) entered
☐ Optional security keys entered
☐ No typos in key names
☐ All secret values (AccessKey, APIKey, Secret) set

Ready to Deploy? ✅
```

