# 🚀 Render + DynamoDB Deployment Checklist

## ✅ Pre-Deployment Checklist

### **1. AWS Setup**

- [ ] AWS account created
- [ ] IAM user created: `recruithub-render`
- [ ] Policies attached to IAM user:
  - [ ] `AmazonDynamoDBFullAccess`
  - [ ] `AmazonS3FullAccess`
- [ ] Access key generated and copied
- [ ] Secret access key saved securely
- [ ] S3 bucket created: `recruithub-media-prod`
- [ ] S3 bucket region matches `AWS_REGION`

### **2. GitHub Setup**

- [ ] Code committed to GitHub
- [ ] All SECRET files added to `.gitignore`
- [ ] `.env` file NOT committed (security!)
- [ ] requirements.txt updated (PynamoDB added)
- [ ] Procfile.dynamodb created

### **3. Code Changes**

- [ ] requirements.txt updated:
  - [ ] Removed `psycopg2-binary`
  - [ ] Removed `dj-database-url`
  - [ ] Added `pynamodb>=6.1.1`
  - [ ] Added `django-environ>=0.11.2`
- [ ] `core/dynamodb_models.py` created
- [ ] `core/management/commands/init_dynamodb.py` created
- [ ] auth_project/settings.py updated for DynamoDB
- [ ] All views updated to use DynamoDB models (if using them)

### **4. Render Setup**

- [ ] Project created in Render.com
- [ ] GitHub repository connected
- [ ] Environment variables added:

**CRITICAL Variables (these MUST be set):**

- [ ] `SECRET_KEY` = Generated value
- [ ] `DEBUG` = `False`
- [ ] `ALLOWED_HOSTS` = Your domain
- [ ] `AWS_ACCESS_KEY_ID` = From AWS IAM
- [ ] `AWS_SECRET_ACCESS_KEY` = From AWS IAM
- [ ] `AWS_REGION` = `us-east-1`
- [ ] `USE_DYNAMODB` = `True`
- [ ] `USE_S3` = `True`
- [ ] `AWS_STORAGE_BUCKET_NAME` = S3 bucket name
- [ ] `AWS_S3_REGION_NAME` = `us-east-1`

**RECOMMENDED Variables:**

- [ ] `DYNAMODB_TABLE_PREFIX` = `recruithub-prod-`
- [ ] `EMAIL_BACKEND` = Email provider
- [ ] `CSRF_TRUSTED_ORIGINS` = Your domain
- [ ] `ENABLE_RATE_LIMITING` = `True`

### **5. Build Configuration**

- [ ] Build command set: `pip install -r requirements.txt`
- [ ] Start command set: `gunicorn auth_project.wsgi:application --bind 0.0.0.0:$PORT`
- [ ] Procfile selected as Config: **Procfile.dynamodb**
- [ ] Runtime selected: **Python 3.11** or higher

### **6. Database Initialization**

- [ ] DynamoDB tables will auto-create on first deployment
- [ ] Superuser will auto-create from environment variables
- [ ] Static files will be collected automatically

---

## 📊 Architecture Diagram

```
┌─────────────────────────────────────────────────────┐
│                    USER BROWSER                     │
└────────────────────┬────────────────────────────────┘
                     │ HTTPS
                     ▼
┌─────────────────────────────────────────────────────┐
│                 RENDER.COM                          │
│                                                     │
│  ┌──────────────────────────────────────────────┐  │
│  │  Django Web App (gunicorn)                   │  │
│  │  - auth_project                              │  │
│  │  - core app                                  │  │
│  │  - Static files (WhiteNoise)                │  │
│  └───────────┬──────────────┬────────────────────┤  │
│              │              │                    │  │
└──────────────┼──────────────┼────────────────────┘  │
               │              │
        ┌──────▼──┐    ┌──────▼────────┐
        │   AWS   │    │    AWS S3     │
        │ DynamoDB│    │  (Media Files)│
        │ (Data)  │    │               │
        └─────────┘    └───────────────┘
```

---

## 🔐 Security Checklist

- [ ] `DEBUG=False` (no error traces exposed)
- [ ] `SECRET_KEY` is unique and secure
- [ ] AWS keys are from dedicated IAM user (not root)
- [ ] S3 bucket blocks all public access
- [ ] HTTPS enforced (`SECURE_SSL_REDIRECT=True`)
- [ ] CSRF protection enabled
- [ ] ALLOWED_HOSTS configured correctly
- [ ] Custom `ADMIN_URL_PATH` set (hard to guess)
- [ ] Email credentials are app-specific (not main password)
- [ ] No secrets in Git repository

---

## 🚀 Deployment Steps

### **Step 1: Click "Deploy"**
- Go to Render Dashboard
- Click "Deploy latest commit"
- Watch the logs

### **Step 2: Wait for Status**
- Building: downloading packages (5-10 min)
- Release phase: running `init_dynamodb` (1-2 min)
- Starting: waiting for app (1 min)
- Live: deployment complete ✅

### **Step 3: Test Your App**
1. Go to your Render app URL: `https://yourapp.onrender.com`
2. Try to access homepage
3. Try to sign up (test DynamoDB)
4. Try to upload profile photo (test S3)
5. Check admin panel (custom URL)

### **Step 4: Monitor**
- Check Render logs for errors
- Check CloudWatch for DynamoDB errors
- Monitor AWS usage (to understand costs)

---

## 🆘 If Deployment Fails

### **Error: "ModuleNotFoundError: No module named 'pynamodb'"**
✅ **Solution:** 
- Check `requirements.txt` includes `pynamodb>=6.1.1`
- Rebuild on Render (clear build cache if needed)

### **Error: "ConnectionError" to DynamoDB**
✅ **Solution:**
- Verify AWS credentials are correct in environment
- Check AWS_REGION is correct
- Verify IAM user has DynamoDBFullAccess policy

### **Error: "NoSuchBucket" for S3**
✅ **Solution:**
- Verify S3 bucket was created
- Check `AWS_STORAGE_BUCKET_NAME` matches exactly
- Verify bucket is in correct region

### **Error: "CRITICAL: SECRET_KEY required"**
✅ **Solution:**
- Add `SECRET_KEY` to Render environment variables

### **Error: Static files not loading**
✅ **Solution:**
- WhiteNoise should serve static files automatically
- Check `Procfile` includes `collectstatic` in release phase

### **App starts but page is blank**
✅ **Solution:**
- Check browser console for JavaScript errors
- Check Render logs for Python errors
- Verify views are updated to use DynamoDB models

---

## 📝 Post-Deployment Configuration

Once deployment is live:

### **1. Set Up Custom Domain**
- Go to Render Project Settings
- Add custom domain: `yourdomain.com`
- Render will provide DNS records to add

### **2. Configure S3 CORS** (for file uploads)
```json
[
  {
    "AllowedHeaders": ["*"],
    "AllowedMethods": ["GET", "PUT", "POST"],
    "AllowedOrigins": ["https://yourdomain.com"],
    "ExposeHeaders": ["ETag"],
    "MaxAgeSeconds": 3000
  }
]
```

### **3. Set Up Monitoring**
- Enable DynamoDB alarms in AWS CloudWatch
- Set up Render alerts for deployment failures
- Monitor S3 costs

### **4. Backup Strategy**
- Enable DynamoDB point-in-time recovery
- Consider daily exports to S3
- Keep monthly backups

---

## 💰 Cost Estimation

**Monthly costs (estimate):**

| Service | Details | Cost |
|---------|---------|------|
| Render | Web service + build minutes | ~$10 |
| DynamoDB | On-demand read/write | ~$15 |
| S3 | Storage + requests | ~$2 |
| Data transfer | Minimal | ~$1 |
| **Total** | | ~**$28/month** |

---

## 🎯 Success Indicators

✅ Deployment is successful if:

1. Site loads without errors
2. User can sign up and create profile
3. File uploads work (photos/resumes saved to S3)
4. Superuser account created automatically
5. Admin panel is accessible at custom URL
6. Logs show no critical errors
7. DynamoDB tables created automatically
8. CloudWatch shows successful requests

---

## 📞 Useful Resources

- **Render Docs:** https://render.com/docs
- **PynamoDB Docs:** https://pynamodb.readthedocs.io/
- **AWS DynamoDB Guide:** https://docs.aws.amazon.com/dynamodb/
- **Django Deployment:** https://docs.djangoproject.com/en/stable/howto/deployment/

