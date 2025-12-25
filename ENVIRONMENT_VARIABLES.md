# 🔐 Environment Variables - RecruitHub Deployment Guide

## ✅ Successfully Pushed to GitHub!

Your deployment files are now on GitHub at: https://github.com/Om-mac/RecruitHub

---

## 📋 What Are Environment Variables?

Environment variables are **secure configuration values** that:
- ✅ Should NOT be committed to Git
- ✅ Are set on the deployment server
- ✅ Contain sensitive information (keys, passwords, URLs)
- ✅ Change between development and production

---

## 🔑 Required Environment Variables for Render

When deploying to Render, add these variables in the Render dashboard:

### CRITICAL - Must Have

#### 1. **SECRET_KEY** ⚠️ CRITICAL

**What it is:** Django's security key for cryptographic operations

**Current value in settings.py:**
```
ciamvzsh2g=nsy4e3iv--k-(uprh_hltzc%gd9_s0%sa@^pt6l3
```

**Usage:**
- Django uses this to sign sessions, CSRF tokens, and password reset links
- If compromised, all sessions are compromised

**Set on Render:**
```
SECRET_KEY = ciamvzsh2g=nsy4e3iv--k-(uprh_hltzc%gd9_s0%sa@^pt6l3
```

---

#### 2. **DEBUG**

**What it is:** Controls whether Django shows error details

**Value for Production:**
```
DEBUG = False
```

**Why?**
- `True` = Shows full error pages with sensitive info (security risk)
- `False` = Shows generic error page (secure)

**Set on Render:**
```
DEBUG = False
```

---

#### 3. **ALLOWED_HOSTS**

**What it is:** Domains allowed to access your app

**Value for your setup:**
```
ALLOWED_HOSTS = yourdomain.com,www.yourdomain.com,recruitapp-backend.onrender.com
```

**Domains to include:**
- Your main domain: `vakverse.com`
- WWW version: `www.vakverse.com`
- Render backup URL: `recruitapp-backend.onrender.com`

**Set on Render:**
```
ALLOWED_HOSTS = yourdomain.com,www.yourdomain.com,recruitapp-backend.onrender.com
```

---

### OPTIONAL - For Database (If Using PostgreSQL)

#### 4. **DATABASE_URL**

**What it is:** Connection string to PostgreSQL database

**Format:**
```
DATABASE_URL = postgresql://username:password@hostname:5432/databasename
```

**Example:**
```
DATABASE_URL = postgresql://recruit_user:secure_password@localhost:5432/recruitdb
```

**Where to get it:**
- Render provides this when you add PostgreSQL database
- Copy from Render dashboard

**Note:** Currently using SQLite (included), but PostgreSQL recommended for production

---

## 📝 Optional - Email Configuration (For Notifications)

#### 5. **EMAIL_HOST** 

**What it is:** SMTP server for sending emails

**Value:**
```
EMAIL_HOST = smtp.gmail.com
```

---

#### 6. **EMAIL_PORT**

**Value:**
```
EMAIL_PORT = 587
```

---

#### 7. **EMAIL_HOST_USER**

**What it is:** Email address to send from

**Example:**
```
EMAIL_HOST_USER = your-email@gmail.com
```

---

#### 8. **EMAIL_HOST_PASSWORD**

**What it is:** App-specific password (NOT your Gmail password)

**How to generate:**
1. Go to https://myaccount.google.com/apppasswords
2. Create app password
3. Copy and paste here

**Example:**
```
EMAIL_HOST_PASSWORD = abcd efgh ijkl mnop
```

---

## 🎯 How to Set Environment Variables on Render

### Step-by-Step

1. **Go to Render Dashboard**
   - https://dashboard.render.com

2. **Select Your Web Service**
   - Click "recruitapp-backend"

3. **Go to "Environment" Tab**
   - Top menu bar

4. **Add Environment Variables**
   - Click "Add Variable"
   - Key: `SECRET_KEY`
   - Value: `ciamvzsh2g=nsy4e3iv--k-(uprh_hltzc%gd9_s0%sa@^pt6l3`
   - Click "Save"

5. **Repeat for Each Variable**

### Quick Copy-Paste Template

```
SECRET_KEY = ciamvzsh2g=nsy4e3iv--k-(uprh_hltzc%gd9_s0%sa@^pt6l3
DEBUG = False
ALLOWED_HOSTS = yourdomain.com,www.yourdomain.com,recruitapp-backend.onrender.com
```

---

## 📊 Environment Variables Summary Table

| Variable | Required? | Example Value | Where Used |
|----------|-----------|---------------|-----------|
| SECRET_KEY | ✅ YES | `ciamvzsh2g=...` | Django security |
| DEBUG | ✅ YES | `False` | Error pages |
| ALLOWED_HOSTS | ✅ YES | `vakverse.com` | Host validation |
| DATABASE_URL | ❌ Optional | `postgresql://...` | Database connection |
| EMAIL_HOST | ❌ Optional | `smtp.gmail.com` | Email sending |
| EMAIL_PORT | ❌ Optional | `587` | Email port |
| EMAIL_HOST_USER | ❌ Optional | `your@gmail.com` | Email account |
| EMAIL_HOST_PASSWORD | ❌ Optional | `app-password` | Email auth |

---

## 🔒 Local Development (.env file)

For local testing, create `.env` file in project root:

```env
SECRET_KEY=ciamvzsh2g=nsy4e3iv--k-(uprh_hltzc%gd9_s0%sa@^pt6l3
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1,vakverse.com
```

**Important:** Add `.env` to `.gitignore` (already done!)

```bash
# Don't commit this!
echo ".env" >> .gitignore
```

---

## 🚀 Deployment Steps with Environment Variables

### 1. On Render Dashboard

Go to your service settings → Environment tab

Add these 3 variables:

```
SECRET_KEY = ciamvzsh2g=nsy4e3iv--k-(uprh_hltzc%gd9_s0%sa@^pt6l3
DEBUG = False
ALLOWED_HOSTS = yourdomain.com,www.yourdomain.com,recruitapp-backend.onrender.com
```

### 2. Click "Save" Button

Render will auto-redeploy with new variables!

### 3. Verify Deployment

Check Render logs to confirm it deployed successfully

---

## ✅ Security Best Practices

### DO ✅
- ✅ Use environment variables for secrets
- ✅ Never commit `.env` files
- ✅ Change SECRET_KEY before production
- ✅ Use strong, unique values
- ✅ Rotate secrets regularly

### DON'T ❌
- ❌ Hardcode secrets in settings.py (already fixed)
- ❌ Commit .env files to Git
- ❌ Share secrets in messages
- ❌ Reuse secrets across projects
- ❌ Use weak/simple values

---

## 🔍 Where Variables Are Used in Code

### In settings.py

```python
import os
from decouple import config

SECRET_KEY = config('SECRET_KEY')
DEBUG = config('DEBUG', default=False, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost').split(',')
```

**How it works:**
- `config('SECRET_KEY')` reads from environment
- If not found, uses default (if provided)
- `cast=bool` converts string to boolean

---

## 📞 Troubleshooting

### Issue: "DisallowedHost" Error

**Cause:** Domain not in ALLOWED_HOSTS

**Solution:** Add your domain to ALLOWED_HOSTS variable

```
ALLOWED_HOSTS = yourdomain.com,www.yourdomain.com
```

### Issue: Secret Key Compromised

**Solution:** Generate new key and update on Render

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Then update SECRET_KEY on Render dashboard

### Issue: Email Not Sending

**Cause:** EMAIL_HOST variables not set

**Solution:** Add email variables to Render

```
EMAIL_HOST = smtp.gmail.com
EMAIL_PORT = 587
EMAIL_HOST_USER = your@gmail.com
EMAIL_HOST_PASSWORD = app-password
```

---

## 🎯 Next Steps

1. **Go to Render Dashboard**
   - https://dashboard.render.com

2. **Add Environment Variables**
   - Use the template above

3. **Deploy**
   - Render auto-deploys on variable change

4. **Test Your App**
   - Visit: https://vakverse.com

---

## 📚 Reference

- [Django Settings](https://docs.djangoproject.com/en/6.0/ref/settings/)
- [Render Environment Variables](https://render.com/docs/environment-variables)
- [Python Decouple](https://github.com/henriquebastos/python-decouple)

---

**Ready to deploy? Add these environment variables to Render! 🚀**
