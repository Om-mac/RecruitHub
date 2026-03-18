# 📧 All Services & Required Keys - Comprehensive Reference

## 🎯 Overview: All External Services Used

Your RecruitHub application uses several external services. Here's what you need for each one:

---

## 1️⃣ **EMAIL SERVICE** 📧

### **Option A: Resend (Recommended - Modern Email)**

**Best For:** Production, high deliverability, modern API

**What It Does:** 
- Sends all user emails (password resets, OTP, notifications)
- Professional email delivery with analytics

**Required Keys:**

```
RESEND_API_KEY=re_1234567890abcdefghijklmnopqrst
DEFAULT_FROM_EMAIL=noreply@yourdomain.com
```

**Where to Get:**
1. Go to: https://resend.com
2. Sign up (free account available)
3. Verify your email
4. Go to API Keys section
5. Create new API key
6. Copy the key (starts with `re_`)

**Setting in Render:**
```
RESEND_API_KEY=re_1234567890abcdefghijklmnopqrst
```

**Free Tier:**
- ✅ Up to 100 emails/day
- ✅ Full API access
- Perfect for starting out

**Cost:**
- $20/month for unlimited after free tier

---

### **Option B: Gmail SMTP (Free but Slower)**

**Best For:** Development, low volume

**What It Does:** Uses SMTP to send emails through Gmail

**Required Keys:**

```
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=xxxx xxxx xxxx xxxx
DEFAULT_FROM_EMAIL=your-email@gmail.com
```

**How to Get Gmail App Password:**

1. Go to: https://myaccount.google.com/apppasswords
2. Sign in to Gmail
3. Select "Mail" and "Windows Computer"
4. Google generates 16-character password
5. Copy it (with or without spaces)

**Example Password:** `abcd efgh ijkl mnop`

**Settings in Render:**
```
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=xxxx xxxx xxxx xxxx
```

**Cost:** FREE (if you have Gmail)

**Limitations:**
- Slower than Resend
- Can be rate limited
- Less reliable for production
- No analytics

---

### **Option C: Console Backend (Development Only)**

**Best For:** Local development, testing

**What It Does:** Prints emails to console instead of sending

**Required Keys:**
```
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
```

**Cost:** FREE

**Email Output:** Appears in terminal/logs

---

## 2️⃣ **AWS SERVICES** ☁️

### **AWS DynamoDB (Database)**

**What It Does:** Stores all application data (users, profiles, documents, etc.)

**Required Keys:**

```
AWS_ACCESS_KEY_ID=AKIA2XXXXXXXXXXXXXXXXXX
AWS_SECRET_ACCESS_KEY=Wr0nG+Xample+key+to+showformat
AWS_REGION=us-east-1
DYNAMODB_TABLE_PREFIX=recruithub-prod-
USE_DYNAMODB=True
```

**Where to Get:**
1. Go to: https://console.aws.amazon.com/iam/
2. Users → Create User
3. Name: `recruithub-render`
4. Attach policy: `AmazonDynamoDBFullAccess`
5. Create access key → Copy both

**Keys Explained:**

| Key | Type | Format | Example |
|-----|------|--------|---------|
| `AWS_ACCESS_KEY_ID` | Public | 20 chars, starts with AKIA | `AKIA2EXAMPLE123456` |
| `AWS_SECRET_ACCESS_KEY` | Secret | 40 random chars | `wJalrXUtnFEMI/K7MDENG+bPx...` |
| `AWS_REGION` | Config | Region code | `us-east-1` |
| `DYNAMODB_TABLE_PREFIX` | Config | any string + `-` | `recruithub-prod-` |

**Permissions Needed:**
- ✅ DynamoDB read/write
- ✅ Create tables (one-time)

**Cost:**
- On-demand pricing: ~$15/month (varies with usage)
- Free tier: 25 write units + 100 read units

---

### **AWS S3 (File Storage)**

**What It Does:** Stores user files (profile photos, resumes)

**Required Keys:**

```
AWS_ACCESS_KEY_ID=AKIA2XXXXXXXXXXXXXXXXXX           (same as DynamoDB)
AWS_SECRET_ACCESS_KEY=Wr0nG+Xample+key+to+showformat (same as DynamoDB)
USE_S3=True
AWS_STORAGE_BUCKET_NAME=recruithub-media-prod
AWS_S3_REGION_NAME=us-east-1
```

**Setup:**
1. Go to: https://s3.console.aws.amazon.com/
2. Create bucket: `recruithub-media-prod`
3. Region: Same as `AWS_REGION`
4. Block all public access ✅
5. Enable versioning (optional, for backups)

**IAM Permissions Needed:**
- ✅ s3:GetObject (read files)
- ✅ s3:PutObject (upload files)
- ✅ s3:DeleteObject (delete files)

**Cost:**
- Storage: $0.023 per GB/month
- Requests: ~$0.0004 per 10,000 requests
- Estimated: ~$2/month

---

### **AWS IAM (User Access Control)**

**What It Does:** Manages AWS credentials and permissions

**Required Keys:**
```
AWS_ACCESS_KEY_ID=AKIA2XXXXXXXXXXXXXXXXXX
AWS_SECRET_ACCESS_KEY=Wr0nG+Xample+key+to+showformat
```

**Setup:**
1. Go to: https://console.aws.amazon.com/iam/
2. Create dedicated user for Render
3. Attach minimal required policies:
   - AmazonDynamoDBFullAccess
   - AmazonS3FullAccess
4. Generate access keys
5. Save in Render environment

**Best Practices:**
- ✅ Use dedicated user (not root)
- ✅ Use minimal permissions
- ✅ Rotate keys every 6 months
- ✅ Never share keys

---

## 3️⃣ **DJANGO SECURITY KEYS** 🔐

### **SECRET_KEY**

**What It Does:** Encrypts Django sessions, CSRF tokens, password resets

**Required Keys:**
```
SECRET_KEY=3j-$d@_8#k$&$!m+9^!@p_#9$!@#$%^&*()_+{}:"<>?
```

**How to Generate:**
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

**Format:**
- 50+ random characters
- Mix of letters, numbers, symbols
- Unique per environment

**Cost:** FREE (it's just a string)

---

## 4️⃣ **DJANGO CORE CONFIG** ⚙️

### **DEBUG**

**What It Does:** Controls error page verbosity

**Required Keys:**
```
DEBUG=False
```

**Values:**
- `True` = Shows full errors (security risk!)
- `False` = Generic error page (production safe)

---

### **ALLOWED_HOSTS**

**What It Does:** Whitelists domains allowed to access app

**Required Keys:**
```
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com,recruithub.onrender.com
```

**Must Include:**
- Your main domain
- www version
- Render backup domain

---

## 5️⃣ **CSRF PROTECTION** 🛡️

### **CSRF_TRUSTED_ORIGINS**

**What It Does:** Prevents CSRF attacks on your domain

**Required Keys:**
```
CSRF_TRUSTED_ORIGINS=https://yourdomain.com,https://*.yourdomain.com
```

---

## 📊 COMPLETE ENVIRONMENT VARIABLES MATRIX

| Service | Variable | Type | Required? | Example | Cost |
|---------|----------|------|-----------|---------|------|
| **Email** | `RESEND_API_KEY` | Secret | ⚠️ Optional | `re_1234...` | $20/mo |
| **Email** | `DEFAULT_FROM_EMAIL` | Config | ⚠️ Optional | `noreply@domain.com` | FREE |
| **Database** | `AWS_ACCESS_KEY_ID` | Secret | ✅ YES | `AKIA2...` | FREE (key) |
| **Database** | `AWS_SECRET_ACCESS_KEY` | Secret | ✅ YES | `wJalr...` | FREE (key) |
| **Database** | `AWS_REGION` | Config | ✅ YES | `us-east-1` | FREE |
| **Database** | `DYNAMODB_TABLE_PREFIX` | Config | ✅ YES | `recruithub-prod-` | FREE |
| **Database** | `USE_DYNAMODB` | Boolean | ✅ YES | `True` | ~$15/mo |
| **Storage** | `AWS_STORAGE_BUCKET_NAME` | Config | ✅ YES | `recruithub-media-prod` | FREE (bucket) |
| **Storage** | `AWS_S3_REGION_NAME` | Config | ✅ YES | `us-east-1` | ~$2/mo |
| **Storage** | `USE_S3` | Boolean | ✅ YES | `True` | FREE |
| **Security** | `SECRET_KEY` | Secret | ✅ YES | 50+ chars | FREE |
| **Security** | `DEBUG` | Boolean | ✅ YES | `False` | FREE |
| **Security** | `ALLOWED_HOSTS` | Config | ✅ YES | domains | FREE |
| **Security** | `CSRF_TRUSTED_ORIGINS` | Config | ⚠️ Optional | https://domain | FREE |
| **Security** | `ADMIN_URL_PATH` | Config | ⚠️ Optional | `admin-xyz123` | FREE |

---

## 🚀 Quick Setup Checklist

### **Email Service**
- [ ] Choose provider (Resend recommended)
- [ ] Get API key
- [ ] Set in Render

### **AWS Account**
- [ ] Create AWS account
- [ ] Create IAM user
- [ ] Generate access keys
- [ ] Create DynamoDB tables (auto on first deploy)
- [ ] Create S3 bucket
- [ ] Attach permissions

### **Django Security**
- [ ] Generate SECRET_KEY
- [ ] Set DEBUG=False
- [ ] Set ALLOWED_HOSTS to your domain
- [ ] Set CSRF_TRUSTED_ORIGINS

### **Render Deployment**
- [ ] Add all environment variables
- [ ] Deploy app
- [ ] Test email sending
- [ ] Test file uploads

---

## 📋 Required Keys Summary

### **MUST HAVE (11 variables):**
```
SECRET_KEY=<generated>
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com,recruithub.onrender.com
AWS_ACCESS_KEY_ID=<from-iam>
AWS_SECRET_ACCESS_KEY=<from-iam>
AWS_REGION=us-east-1
USE_DYNAMODB=True
USE_S3=True
AWS_STORAGE_BUCKET_NAME=recruithub-media-prod
AWS_S3_REGION_NAME=us-east-1
DYNAMODB_TABLE_PREFIX=recruithub-prod-
```

### **SHOULD HAVE (Email - pick one):**

**Option A - Resend (Modern):**
```
RESEND_API_KEY=<from-resend>
DEFAULT_FROM_EMAIL=noreply@yourdomain.com
```

**Option B - Gmail (Free):**
```
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=<app-specific-password>
```

**Option C - Console (Dev only):**
```
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
```

### **NICE TO HAVE (optional):**
```
CSRF_TRUSTED_ORIGINS=https://yourdomain.com,https://*.yourdomain.com
ADMIN_URL_PATH=admin-randomstring123
ENABLE_RATE_LIMITING=True
```

---

## 💰 Total Monthly Cost Estimate

| Service | Cost |
|---------|------|
| AWS DynamoDB | ~$15 |
| AWS S3 | ~$2 |
| Resend Email | $20 (or $0 on free tier) |
| Render | ~$10 |
| **Total** | **~$47/month** |

*Note: Free tiers can reduce costs. Render free tier brings it to ~$27/month*

---

## 🆘 Troubleshooting by Service

### **Email Not Sending**

**Check these in order:**

1. Is email backend configured?
   ```python
   # In settings.py
   EMAIL_BACKEND = 'resend.django.backend.EmailBackend'
   ```

2. Is API key set?
   ```bash
   python -c "import os; print(os.environ.get('RESEND_API_KEY'))"
   ```

3. Is it a valid key?
   - Should start with `re_`
   - Should be 40+ characters

4. Check logs:
   ```bash
   # In Render logs
   # Look for "[RESEND-OPEN]" messages
   ```

### **DynamoDB Not Found**

**Check these:**

1. Is USE_DYNAMODB=True?
2. Are AWS credentials correct?
3. Did tables get created? (Check AWS console)
4. Is AWS_REGION matching?

### **S3 Upload Failing**

**Check these:**

1. Does bucket exist in same region?
2. Is USE_S3=True?
3. Are AWS credentials correct?
4. Are permissions set? (s3:PutObject required)
5. Does bucket block public access? (should be YES)

---

## 🔐 Security Reminders

✅ **DO:**
- Use environment variables for all secrets
- Never commit `.env` files
- Rotate AWS keys every 6 months
- Use dedicated IAM user (not root)
- Keep API keys secure
- Use strong SECRET_KEY

❌ **DON'T:**
- Hardcode secrets in code
- Commit credentials to Git
- Share API keys in chats
- Use weak SECRET_KEY
- Allow public S3 access
- Use DEBUG=True in production

---

## 📞 Quick Reference Links

| Service | Website |
|---------|---------|
| Resend | https://resend.com |
| AWS Console | https://console.aws.amazon.com |
| AWS IAM | https://console.aws.amazon.com/iam/ |
| S3 Buckets | https://s3.console.aws.amazon.com/ |
| Render Dashboard | https://dashboard.render.com |
| Gmail App Passwords | https://myaccount.google.com/apppasswords |
| Django Docs | https://docs.djangoproject.com |

---

## ✅ Final Verification

Before deploying, verify:

- [ ] All 11 CRITICAL variables set in Render
- [ ] Email service configured (any option)
- [ ] AWS credentials valid
- [ ] S3 bucket created
- [ ] DynamoDB enabled
- [ ] DEBUG=False
- [ ] SECRET_KEY is unique
- [ ] ALLOWED_HOSTS includes your domain
- [ ] Ran `python validate_env_vars.py` (passed)
- [ ] No secrets in Git repo

You're ready to deploy! 🚀

