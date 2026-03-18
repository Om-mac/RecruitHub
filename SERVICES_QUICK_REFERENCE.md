# 🔑 Services & Keys Quick Comparison Chart

## 📊 Visual Overview: What You Need for Each Service

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        RECRUITHUB SERVICES MAP                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────────────┐  ┌──────────────────┐  ┌──────────────────────┐  │
│  │   EMAIL SERVICE     │  │  AWS DYNAMODB    │  │   AWS S3 STORAGE     │  │
│  │  (User Emails)      │  │   (Database)     │  │   (File Storage)     │  │
│  │                     │  │                  │  │                      │  │
│  │ Option A:Resend     │  │ Required Keys:   │  │ Required Keys:       │  │
│  │ Option B:Gmail      │  │ • Access Key ID  │  │ • Access Key ID      │  │
│  │ Option C:Console    │  │ • Secret Key     │  │ • Secret Key         │  │
│  │                     │  │ • AWS_REGION     │  │ • Bucket Name        │  │
│  │ Keys: 1-2           │  │ • Table Prefix   │  │ • Region             │  │
│  │ Cost: FREE-$20/mo   │  │                  │  │                      │  │
│  │ Difficulty: Easy    │  │ Keys: 4          │  │ Keys: 2 (shared)     │  │
│  │                     │  │ Cost: ~$15/mo    │  │ Cost: ~$2/mo         │  │
│  │                     │  │ Difficulty: Med  │  │ Difficulty: Med      │  │
│  └─────────────────────┘  └──────────────────┘  └──────────────────────┘  │
│           │                       │                      │                 │
│           └───────────────────────┼──────────────────────┘                 │
│                                   │                                        │
│                          ┌────────▼────────┐                              │
│                          │   RENDER.COM    │                              │
│                          │  (Hosting App)  │                              │
│                          │                 │                              │
│                          │  Receives All   │                              │
│                          │  Keys via       │                              │
│                          │  Environment    │                              │
│                          │  Variables      │                              │
│                          └─────────────────┘                              │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 🔑 Email Service Options Comparison

### **Quick Decision Tree**

```
Would you like to send emails?
│
├─ YES, I want production-ready emails
│  └─ Use RESEND (Recommended)
│     Keys needed: 2
│     Cost: $20/month (or free tier up to 100/day)
│     Setup time: 5 minutes
│
├─ YES, but I want to use my existing email
│  └─ Use GMAIL SMTP
│     Keys needed: 4
│     Cost: FREE (if you have Gmail)
│     Setup time: 10 minutes
│
└─ NO, I just want to test locally
   └─ Use CONSOLE BACKEND
      Keys needed: 0
      Cost: FREE
      Setup time: 1 minute
```

---

## 📋 Email Service: Keys Comparison

### **Resend (Modern, Recommended ⭐⭐⭐)**

```
What you get:
✅ Professional email delivery
✅ Built-in analytics
✅ Webhook support
✅ Email templates
✅ Free tier (100 emails/day)
✅ Fast setup

Keys needed:          │ Format
──────────────────────┼──────────────────────────────────
RESEND_API_KEY        │ re_1a2b3c4d5e6f...
DEFAULT_FROM_EMAIL    │ noreply@yourdomain.com

Where to get them:
1. Visit: https://resend.com
2. Sign up (free)
3. Go to API Keys
4. Copy your key (starts with "re_")

Cost breakdown:
- Free tier: 100 emails/day
- Paid: $20/month for unlimited
- After 30 days: Still get 100/day free

Delivery speed: ⚡⚡⚡ (FAST)
Reliability: 🟢 Excellent
```

---

### **Gmail SMTP (Free, Well-Known)**

```
What you get:
✅ Free (no additional cost)
✅ Your existing Gmail account
✅ Works with Django out of box
❌ Can be slow
❌ Rate limited
❌ Less reliable than Resend

Keys needed:          │ Format
──────────────────────┼──────────────────────────────────
EMAIL_HOST            │ smtp.gmail.com
EMAIL_PORT            │ 587
EMAIL_HOST_USER       │ your-email@gmail.com
EMAIL_HOST_PASSWORD   │ xxxx xxxx xxxx xxxx (app password)
DEFAULT_FROM_EMAIL    │ your-email@gmail.com

Where to get them:
1. HOST: smtp.gmail.com (built-in)
2. PORT: 587 (built-in)
3. USER: your Gmail address
4. PASSWORD: https://myaccount.google.com/apppasswords
   - Select "Mail" and "Windows Computer"
   - Copy the generated password

Cost breakdown:
- FREE (uses your Gmail)
- No additional charges

Delivery speed: ⚡ (MODERATE)
Reliability: 🟡 Good but can be rate limited
```

---

### **Console Backend (Testing Only)**

```
What you get:
✅ Emails print to console/logs
✅ Perfect for local development
✅ No configuration needed
❌ Not for production
❌ Emails not actually sent

Keys needed:          │ Format
──────────────────────┼──────────────────────────────────
EMAIL_BACKEND         │ django.core.mail.backends.console.EmailBackend

Where to get them:
1. No external setup needed
2. Set in Render environment
3. Emails appear in logs

Cost breakdown:
- FREE

Delivery speed: ⚡⚡⚡ (INSTANT - console only)
Reliability: 🟢 Perfect for testing
```

---

## 📊 AWS Services: Keys Matrix

```
┌──────────────────────────────────────────────────────────────┐
│              AWS KEYS (Shared across services)               │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│ AWS_ACCESS_KEY_ID                                            │
│ ├─ Format: 20 characters                                     │
│ ├─ Starts with: AKIA                                         │
│ ├─ Example: AKIA2L5Z3LVXP5N7OXYVU                           │
│ ├─ Used by: DynamoDB + S3                                    │
│ └─ Where: https://console.aws.amazon.com/iam/               │
│                                                               │
│ AWS_SECRET_ACCESS_KEY                                        │
│ ├─ Format: 40 characters, random                             │
│ ├─ Example: wJalrXUtnFEMI/K7MDENG+bPxRfiCYEXAMPLEKEY       │
│ ├─ Used by: DynamoDB + S3                                    │
│ ├─ ⚠️ CAN'T BE REGENERATED - SAVE IT!                       │
│ └─ Where: https://console.aws.amazon.com/iam/               │
│                                                               │
│ AWS_REGION                                                   │
│ ├─ Format: region-code (us-east-1, eu-west-1, etc)         │
│ ├─ Used by: DynamoDB                                        │
│ ├─ Recommended: us-east-1 (cheapest)                        │
│ └─ Configure in: settings.py or environment                │
│                                                               │
├──────────────────────────────────────────────────────────────┤
│         DynamoDB-Specific Keys (Database)                    │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│ USE_DYNAMODB                 Must be: True                  │
│ DYNAMODB_TABLE_PREFIX        Must be: recruithub-prod-      │
│                                                               │
├──────────────────────────────────────────────────────────────┤
│         S3-Specific Keys (File Storage)                      │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│ USE_S3                       Must be: True                  │
│ AWS_STORAGE_BUCKET_NAME      Must be: <your-bucket-name>   │
│ AWS_S3_REGION_NAME           Must match: AWS_REGION        │
│                                                               │
└──────────────────────────────────────────────────────────────┘
```

---

## 🎯 Django Security Keys

```
┌──────────────────────────────────────────────────────────────┐
│           DJANGO CORE SECURITY KEYS                          │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│ SECRET_KEY                                                   │
│ ├─ Purpose: Encrypt sessions, CSRF tokens, password resets  │
│ ├─ Format: 50+ random characters                             │
│ ├─ Generate: python -c "from django.core.management...      │
│ ├─ Change in EVERY environment (dev ≠ prod)                │
│ └─ ⚠️ If compromised, regenerate immediately               │
│                                                               │
│ DEBUG                                                        │
│ ├─ Purpose: Show/hide error details                         │
│ ├─ Production: False  (NEVER True in production!)            │
│ ├─ Development: True                                         │
│ └─ ⚠️ False = hides sensitive info from errors             │
│                                                               │
│ ALLOWED_HOSTS                                               │
│ ├─ Purpose: Whitelist domains that can access app           │
│ ├─ Format: Comma-separated domains                          │
│ ├─ Example: yourdomain.com,www.yourdomain.com              │
│ └─ Must include: Render backup URL (*.onrender.com)        │
│                                                               │
│ CSRF_TRUSTED_ORIGINS                                        │
│ ├─ Purpose: Prevent CSRF attacks                            │
│ ├─ Format: https://yourdomain.com,https://*.yourdomain.com │
│ └─ Optional but recommended                                 │
│                                                               │
│ ADMIN_URL_PATH                                              │
│ ├─ Purpose: Hide admin panel from bots                      │
│ ├─ Example: admin-randomstring123                           │
│ ├─ Default (if not set): /admin/  (BAD!)                   │
│ └─ Optional but recommended for security                    │
│                                                               │
└──────────────────────────────────────────────────────────────┘
```

---

## 📊 Complete Checklist: What Keys to Set in Render

### **✅ CRITICAL (Must Set - 11 keys)**

```
☐ SECRET_KEY ...................... (Generate: python command)
☐ DEBUG ............................ (Set: False)
☐ ALLOWED_HOSTS .................... (Your domain)
☐ AWS_ACCESS_KEY_ID ................ (From AWS IAM)
☐ AWS_SECRET_ACCESS_KEY ............ (From AWS IAM - SAVE IMMEDIATELY!)
☐ AWS_REGION ....................... (us-east-1 recommended)
☐ USE_DYNAMODB ..................... (Set: True)
☐ USE_S3 ........................... (Set: True)
☐ AWS_STORAGE_BUCKET_NAME .......... (S3 bucket name)
☐ AWS_S3_REGION_NAME ............... (Same as AWS_REGION)
☐ DYNAMODB_TABLE_PREFIX ............ (recruithub-prod-)
```

### **📧 PICK ONE: Email Service (1-4 keys)**

**Option A: Resend**
```
☐ RESEND_API_KEY ................... (From resend.com)
☐ DEFAULT_FROM_EMAIL ............... (noreply@yourdomain.com)
```

**Option B: Gmail**
```
☐ EMAIL_BACKEND .................... (django.core.mail.backends.smtp.EmailBackend)
☐ EMAIL_HOST ....................... (smtp.gmail.com)
☐ EMAIL_PORT ....................... (587)
☐ EMAIL_HOST_USER .................. (your-email@gmail.com)
☐ EMAIL_HOST_PASSWORD .............. (App password from Google)
☐ DEFAULT_FROM_EMAIL ............... (your-email@gmail.com)
```

**Option C: Console (Dev only)**
```
☐ EMAIL_BACKEND .................... (django.core.mail.backends.console.EmailBackend)
```

### **🔐 OPTIONAL: Security (2 keys)**

```
☐ CSRF_TRUSTED_ORIGINS ............. (https://yourdomain.com)
☐ ADMIN_URL_PATH ................... (admin-randomstring)
```

---

## 🛠️ How to Setup: Step by Step

### **Step 1: Get AWS Credentials (20 minutes)**

```
1. Go to: https://console.aws.amazon.com/iam/
2. Create User:
   - Username: recruithub-render
   - Next
3. Attach Policies:
   ☐ AmazonDynamoDBFullAccess
   ☐ AmazonS3FullAccess
4. Create Access Key:
   - Copy AWS_ACCESS_KEY_ID (20 chars)
   - Copy AWS_SECRET_ACCESS_KEY (40 chars) ⚠️ SAVE NOW!
5. Create S3 Bucket:
   - Name: recruithub-media-prod
   - Region: us-east-1
   - Block all public access: ✅ YES
```

### **Step 2: Generate Django Keys (5 minutes)**

```bash
# Generate SECRET_KEY
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# Generate ADMIN_URL_PATH (optional)
python -c "import secrets; print('admin-' + secrets.token_hex(8))"
```

### **Step 3: Setup Email (5-15 minutes)**

**For Resend:**
```
1. Go to: https://resend.com
2. Sign up (free)
3. Verify email
4. API Keys → Copy API Key
```

**For Gmail:**
```
1. Go to: https://myaccount.google.com/apppasswords
2. Select "Mail" and "Windows Computer"
3. Copy generated password
```

### **Step 4: Add to Render (5 minutes)**

```
1. Go to: https://dashboard.render.com
2. Select your web service
3. Environment tab
4. Add each variable from checklist above
5. Save and deploy
```

---

## 💾 Sample Environment Variable Block

Copy & paste this, replace values with yours:

```
SECRET_KEY=<from-step-2-above>
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com,recruithub.onrender.com
AWS_ACCESS_KEY_ID=<from-aws-iam>
AWS_SECRET_ACCESS_KEY=<from-aws-iam>
AWS_REGION=us-east-1
USE_DYNAMODB=True
USE_S3=True
AWS_STORAGE_BUCKET_NAME=recruithub-media-prod
AWS_S3_REGION_NAME=us-east-1
DYNAMODB_TABLE_PREFIX=recruithub-prod-
RESEND_API_KEY=<from-resend.com>
DEFAULT_FROM_EMAIL=noreply@yourdomain.com
CSRF_TRUSTED_ORIGINS=https://yourdomain.com,https://*.yourdomain.com
ADMIN_URL_PATH=admin-<randomstring>
```

---

## ✅ Verification Before Deployment

Run this to verify all keys are set:

```bash
python validate_env_vars.py
```

Should show:
```
✓ All critical variables are set!
✅ VALIDATION PASSED - Ready for deployment!
```

---

## 🆘 Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| "RESEND_API_KEY not found" | Add to Render env vars, not local |
| "AWS credentials invalid" | Check format (AKIA... for key ID, 40 chars for secret) |
| "Bucket not found" | Create S3 bucket with exact name from env var |
| "Can't find SECRET_KEY" | Generate using python command above |
| Email not sending | Check EMAIL_BACKEND is set correctly |

---

## 📞 External Links

| Service | URL |
|---------|-----|
| AWS IAM Console | https://console.aws.amazon.com/iam/ |
| S3 Console | https://s3.console.aws.amazon.com/ |
| Resend | https://resend.com |
| Gmail App Passwords | https://myaccount.google.com/apppasswords |
| Render Dashboard | https://dashboard.render.com |

