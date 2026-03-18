# 🎯 Render + DynamoDB Deployment - Quick Start Guide

## ⚡ 5-Minute Overview

You're migrating from PostgreSQL to DynamoDB on Render. This requires:

1. **AWS Credentials** (for DynamoDB + S3)
2. **Updated Python packages** (added PynamoDB)
3. **New database models** (using PynamoDB instead of Django ORM)
4. **Environment variables** (11 critical keys)

---

## 🚀 Quick Deployment Path

### **Phase 1: Get AWS Credentials (15 min)**

**Create AWS IAM User:**
```bash
1. Go to: https://console.aws.amazon.com/iam/
2. Users → Create User → "recruithub-render"
3. Attach policies:
   - AmazonDynamoDBFullAccess
   - AmazonS3FullAccess
4. Create access key → Copy both keys
```

**Create S3 Bucket:**
```bash
1. Go to: https://s3.console.aws.amazon.com/
2. Create bucket → "recruithub-media-prod"
3. Block all public access ✅
4. Same region as AWS_REGION
```

---

### **Phase 2: Update Code (10 min)**

✅ Already done for you:
- `requirements.txt` - Updated with PynamoDB
- `core/dynamodb_models.py` - Created DynamoDB models
- `core/management/commands/init_dynamodb.py` - Database initialization
- Documentation files created

---

### **Phase 3: Configure Render (10 min)**

**Add 11 Environment Variables:**

```
SECRET_KEY=<generated-value>
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com,recruithub.onrender.com
AWS_ACCESS_KEY_ID=<from-aws>
AWS_SECRET_ACCESS_KEY=<from-aws>
AWS_REGION=us-east-1
USE_DYNAMODB=True
USE_S3=True
AWS_STORAGE_BUCKET_NAME=recruithub-media-prod
AWS_S3_REGION_NAME=us-east-1
DYNAMODB_TABLE_PREFIX=recruithub-prod-
```

---

## 📋 Complete Checklist

### **Before Deployment**

- [ ] AWS account created
- [ ] IAM user "recruithub-render" created with DynamoDB + S3 access
- [ ] Access key ID copied
- [ ] Secret access key saved securely
- [ ] S3 bucket created
- [ ] Code pushed to GitHub
- [ ] requirements.txt updated ✅
- [ ] DynamoDB models created ✅
- [ ] Settings updated for DynamoDB

### **Render Dashboard Setup**

- [ ] New web service created
- [ ] GitHub connected
- [ ] All 11 environment variables added
- [ ] Build command: `pip install -r requirements.txt`
- [ ] Start command: `gunicorn auth_project.wsgi:application --bind 0.0.0.0:$PORT`

### **After First Deployment**

- [ ] Check if DynamoDB tables were auto-created
- [ ] Verify superuser was auto-created
- [ ] Test signup (creates data in DynamoDB)
- [ ] Test profile photo upload (saves to S3)
- [ ] Check admin panel works

---

## 🔑 All Keys You Need

| Key | Where to Get | Example |
|-----|--------------|---------|
| `SECRET_KEY` | Generate: `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"` | 50+ random chars |
| `AWS_ACCESS_KEY_ID` | AWS IAM console | `AKIAIOSFODNN7EXAMPLE` |
| `AWS_SECRET_ACCESS_KEY` | AWS IAM console | 40 random chars |
| `AWS_REGION` | Choose | `us-east-1` |
| `AWS_STORAGE_BUCKET_NAME` | S3 bucket you create | `recruithub-media-prod` |

---

## ⚠️ Most Common Mistakes

1. **Typo in environment variable name** → App won't start
2. **AWS credentials wrong** → DynamoDB access denied
3. **DEBUG=True in production** → Security vulnerability
4. **S3 bucket blocks public access but shouldn't** → Files inaccessible (or vice versa)
5. **ALLOWED_HOSTS missing Render domain** → Site returns 400 error
6. **Forgot to create S3 bucket** → File uploads fail
7. **Django ORM migrations still in code** → Won't work with DynamoDB

---

## 📞 Getting Help

### **If deployment fails:**

1. **Check Render Logs:**
   - Your Render project → Logs tab
   - Look for red error messages

2. **Common errors:**
   - "ModuleNotFoundError: pynamodb" → Wait for rebuild
   - "AccessDenied DynamoDB" → Check AWS credentials
   - "NoSuchBucket S3" → Create S3 bucket with correct name
   - "CRITICAL: SECRET_KEY missing" → Add it to Render env vars

3. **Local testing before deployment:**
   ```bash
   # Test environment locally
   python validate_env_vars.py  # Check all vars
   ```

---

## 📚 Documentation Files Created

- `RENDER_DYNAMODB_DEPLOYMENT_GUIDE.md` - Detailed guide (📖 START HERE)
- `ENVIRONMENT_VARIABLES_COMPLETE.md` - How to get each key
- `REQUIRED_KEYS_AND_CREDENTIALS.md` - Key reference
- `RENDER_DEPLOYMENT_CHECKLIST.md` - Step-by-step checklist
- `DYNAMODB_SETTINGS_CONFIG.md` - Settings code to add
- `validate_env_vars.py` - Validation script

---

## 🎯 Your Next Steps

### **Step 1: Read Main Guide**
Open `RENDER_DYNAMODB_DEPLOYMENT_GUIDE.md` - it has everything

### **Step 2: Get AWS Credentials**
1. Create AWS IAM user (15 min)
2. Generate access keys
3. Create S3 bucket

### **Step 3: Add to Render**
1. Create Render web service
2. Connect GitHub
3. Add 11 environment variables
4. Deploy!

### **Step 4: Test**
1. Wait 5-10 minutes for deployment
2. Visit your app URL
3. Try signup
4. Upload profile photo

---

## 💰 Cost Breakdown

**AWS (per month):**
- DynamoDB: ~$15 (writes/reads)
- S3: ~$2 (storage + requests)
- Data transfer: ~$1

**Render (per month):**
- Web service: ~$10 (free tier available)

**Total: ~$28/month** (or free if using Render free tier)

---

## ✅ Success Indicators

✅ Deployment successful if:
1. Site loads without errors
2. User can sign up
3. Profile photo uploads to S3
4. Admin panel works at custom URL
5. DynamoDB tables created
6. Logs show no critical errors

---

## 🆘 Quick Troubleshooting

| Issue | Solution |
|-------|----------|
| Site won't load | Check if all 11 env vars are set |
| DynamoDB error | Verify AWS credentials in Render |
| S3 upload fails | Ensure S3 bucket exists and blocks public access only for Render IP |
| Admin panel 404 | Check if ADMIN_URL_PATH is set correctly |
| Static files not loaded | WhiteNoise handles this, should auto-work |
| Email not sending | Set EMAIL_BACKEND to at least console mode |

---

## 📝 Sample Render Environment Variables

Copy & paste into Render dashboard:

```
SECRET_KEY=test-key-replace-with-generated-key-123456789
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com,recruithub.onrender.com
AWS_ACCESS_KEY_ID=AKIA2EXAMPLE123456
AWS_SECRET_ACCESS_KEY=SecretKeyABCD1234567890EXAMPLE
AWS_REGION=us-east-1
USE_DYNAMODB=True
USE_S3=True
AWS_STORAGE_BUCKET_NAME=recruithub-media-prod
AWS_S3_REGION_NAME=us-east-1
DYNAMODB_TABLE_PREFIX=recruithub-prod-
```

---

## 🎓 Learn More

- PynamoDB: https://pynamodb.readthedocs.io/
- AWS DynamoDB: https://docs.aws.amazon.com/dynamodb/
- Render: https://render.com/docs
- Django Security: https://docs.djangoproject.com/demo/security/

