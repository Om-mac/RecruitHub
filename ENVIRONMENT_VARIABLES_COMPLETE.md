# 🔑 Complete Environment Variables Reference

## ✅ All Variables Needed for Render + DynamoDB Deployment

### **Copy This Table to Render Dashboard**

| Variable Name | Value | Required? | Type | Notes |
|---------------|-------|-----------|------|-------|
| **SECRET_KEY** | `<random-secure-key>` | ✅ CRITICAL | Secret | See: Generate SECRET_KEY below |
| **DEBUG** | `False` | ✅ CRITICAL | String | Always `False` in production |
| **ALLOWED_HOSTS** | `yourdomain.com,www.yourdomain.com,recruithub.onrender.com` | ✅ CRITICAL | String | Comma-separated, no spaces |
| **AWS_ACCESS_KEY_ID** | From AWS IAM | ✅ CRITICAL | Secret | 20 chars, starts with AKIA |
| **AWS_SECRET_ACCESS_KEY** | From AWS IAM | ✅ CRITICAL | Secret | 40 random chars |
| **AWS_REGION** | `us-east-1` | ✅ CRITICAL | String | Where DynamoDB tables exist |
| **USE_DYNAMODB** | `True` | ✅ CRITICAL | String | Enable DynamoDB for models |
| **USE_S3** | `True` | ✅ CRITICAL | String | Enable S3 for file storage |
| **AWS_STORAGE_BUCKET_NAME** | `recruithub-media-prod` | ✅ YES | String | Your S3 bucket name |
| **AWS_S3_REGION_NAME** | `us-east-1` | ✅ YES | String | S3 bucket region |
| **DYNAMODB_TABLE_PREFIX** | `recruithub-prod-` | ❌ Optional | String | Prefix for table names |
| **EMAIL_BACKEND** | `resend.django.backend.EmailBackend` | ❌ Optional | String | Or `django.core.mail.backends.smtp.EmailBackend` |
| **RESEND_API_KEY** | From Resend.com | ❌ Optional | Secret | Only if using Resend for emails |
| **EMAIL_HOST** | `smtp.gmail.com` | ❌ Optional | String | Only if using Gmail |
| **EMAIL_PORT** | `587` | ❌ Optional | String | Gmail SMTP port |
| **EMAIL_HOST_USER** | `your-email@gmail.com` | ❌ Optional | String | Gmail address |
| **EMAIL_HOST_PASSWORD** | App-specific password | ❌ Optional | Secret | NOT your Gmail password |
| **CSRF_TRUSTED_ORIGINS** | `https://yourdomain.com,https://*.yourdomain.com` | ❌ Optional | String | Your domain(s) |
| **ADMIN_URL_PATH** | `admin-random-string` | ❌ Optional | String | Custom admin URL |
| **ENABLE_RATE_LIMITING** | `True` | ❌ Optional | String | Enable DDoS protection |
| **RATE_LIMIT_LOGIN_ENABLED** | `True` | ❌ Optional | String | Rate limit login attempts |
| **RATE_LIMIT_LOGIN_ATTEMPTS** | `5` | ❌ Optional | String | Max login attempts |
| **RATE_LIMIT_LOGIN_WINDOW** | `900` | ❌ Optional | String | Time window in seconds (15 min) |

---

## 🚀 Step-by-Step: Get Each Value

### 1️⃣ **SECRET_KEY** (Django Security Key)

**What it does:** Encrypts sessions, password resets, CSRF tokens

**Generate it:**
```bash
# On your local machine, run:
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

**Example output:**
```
3j-$d@_8#k$&$!m+9^!@p_#9$!@#$%^&*()_+{}:"<>?
```

**Copy this exact value to Render as `SECRET_KEY`**

---

### 2️⃣ **AWS_ACCESS_KEY_ID & AWS_SECRET_ACCESS_KEY**

**What they do:** Allow your app to access DynamoDB and S3

**How to get them:**

1. Go to: https://console.aws.amazon.com/iam/
2. Click "Users" → "Create User"
3. Username: `recruithub-render`
4. Click "Next" → "Attach policies directly"
5. **Search for and select:**
   - `AmazonDynamoDBFullAccess`
   - `AmazonS3FullAccess`
6. Click "Create User"
7. Click on the user → "Security credentials" tab
8. Click "Create access key"
9. Select "Command Line Interface (CLI)" 
10. Copy both keys:
    - `Access Key ID` → Set as `AWS_ACCESS_KEY_ID` in Render
    - `Secret Access Key` → Set as `AWS_SECRET_ACCESS_KEY` in Render

⚠️ **Important:** Save these immediately! You cannot view secret key again.

---

### 3️⃣ **AWS_REGION**

**What it does:** Tell AWS which region your DynamoDB tables are in

**Most common values:**
```
us-east-1        # US East (Virginia) - Default, cheapest
us-west-2        # US West (Oregon)
eu-west-1        # Europe (Ireland)
ap-south-1       # Asia (Mumbai)
```

**Recommendation:** Use `us-east-1` (default, lowest cost)

---

### 4️⃣ **AWS_STORAGE_BUCKET_NAME**

**What it does:** Tells S3 where to store user files (photos, resumes)

**Steps to create:**

1. Go to: https://s3.console.aws.amazon.com/
2. Click "Create bucket"
3. Bucket name: `recruithub-media-prod` (must be globally unique!)
4. Region: Same as `AWS_REGION` (usually `us-east-1`)
5. Block all public access: ✅ ENABLED (security!)
6. Click "Create bucket"
7. Your bucket name → Use as `AWS_STORAGE_BUCKET_NAME`

---

### 5️⃣ **ALLOWED_HOSTS**

**What it does:** Tell Django which domains can access your app

**Example format:**
```
yourdomain.com,www.yourdomain.com,recruithub.onrender.com
```

**Replace with YOUR domains:**
- `yourdomain.com` → Your main domain
- `www.yourdomain.com` → With www prefix
- `recruithub.onrender.com` → Render's backup URL (keep this!)

---

### 6️⃣ **Email Configuration** (OPTIONAL)

#### **Option A: Using Resend (Recommended)**

1. Go to: https://resend.com
2. Sign up (free tier available)
3. Get API Key from dashboard
4. Set:
   - `EMAIL_BACKEND=resend.django.backend.EmailBackend`
   - `RESEND_API_KEY=<your-api-key>`

#### **Option B: Using Gmail**

1. Go to: https://myaccount.google.com/apppasswords
2. Sign in to your Gmail
3. Select "Mail" and "Windows Computer"
4. Google will generate a 16-character password
5. Set:
   - `EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend`
   - `EMAIL_HOST=smtp.gmail.com`
   - `EMAIL_PORT=587`
   - `EMAIL_HOST_USER=your-email@gmail.com`
   - `EMAIL_HOST_PASSWORD=<16-char-password>`

---

## 📋 Complete Variables to Add in Render Dashboard

### **Copy & Paste into Render Environment:**

```
SECRET_KEY=<from-step-1>
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com,recruithub.onrender.com

AWS_ACCESS_KEY_ID=<from-step-2-access-key>
AWS_SECRET_ACCESS_KEY=<from-step-2-secret-key>
AWS_REGION=us-east-1
USE_DYNAMODB=True
USE_S3=True
AWS_STORAGE_BUCKET_NAME=recruithub-media-prod
AWS_S3_REGION_NAME=us-east-1

DYNAMODB_TABLE_PREFIX=recruithub-prod-

EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend

CSRF_TRUSTED_ORIGINS=https://yourdomain.com,https://*.yourdomain.com

ENABLE_RATE_LIMITING=True
RATE_LIMIT_LOGIN_ENABLED=True
RATE_LIMIT_LOGIN_ATTEMPTS=5
RATE_LIMIT_LOGIN_WINDOW=900
```

---

## 🆘 Troubleshooting

### **Error: "CRITICAL: SECRET_KEY environment variable is required"**
✅ **Solution:** Add `SECRET_KEY` to Render environment variables

### **Error: "AccessDenied" when accessing DynamoDB**
✅ **Solution:** Verify AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY are correct

### **Error: "NoSuchBucket" for S3**
✅ **Solution:** Create S3 bucket matching `AWS_STORAGE_BUCKET_NAME`

### **Email not sending**
✅ **Solution:** 
- Check `EMAIL_BACKEND` is set correctly
- If using Gmail, ensure you generated app-specific password (not regular password)
- Check RESEND_API_KEY if using Resend

### **Site doesn't load after deployment**
✅ **Solution:**
- Add your Render domain to `ALLOWED_HOSTS`
- Check CloudWatch logs in AWS console
- Ensure all CRITICAL variables are set

---

## 📝 Render Dashboard Setup

1. Go to: https://render.com
2. Create new "Web Service"
3. Connect GitHub repository
4. In "Environment" tab:
   - Click "Add Environment Variable"
   - For each variable in the table above, paste:
     - **Key:** Variable name
     - **Value:** Its value
     - For Secret values, check "Secret" checkbox
5. **Important:** Set build command:
   ```bash
   pip install -r requirements.txt
   ```
6. **Important:** Set start command:
   ```bash
   gunicorn auth_project.wsgi:application --bind 0.0.0.0:$PORT
   ```

---

## ✅ Verification Checklist

Before clicking "Deploy":

- [ ] All CRITICAL variables are set (13 variables)
- [ ] `DEBUG=False`
- [ ] AWS keys are valid (from IAM user)
- [ ] S3 bucket exists with correct name  
- [ ] DynamoDB tables exist (or will be auto-created)
- [ ] ALLOWED_HOSTS includes your domain
- [ ] EMAIL_BACKEND is set (even if just console)
- [ ] No typos in environment variable names

---

## 🔐 Security Best Practices

1. **Never commit secrets to Git** - Always use Render environment variables
2. **Use different AWS keys for dev/prod** - Create separate IAM user for Render
3. **Minimize IAM permissions** - Use specific policies, not `AdministratorAccess`
4. **Rotate access keys** - Change them every 6-12 months
5. **Use custom ADMIN_URL_PATH** - Harder for bots to find admin panel
6. **Enable CSRF protection** - Set CSRF_TRUSTED_ORIGINS correctly
7. **Use HTTPS only** - SECURE_SSL_REDIRECT=True (automatic in production)

