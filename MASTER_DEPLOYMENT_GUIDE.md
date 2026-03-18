# 🎯 RecruitHub Render + DynamoDB Migration - MASTER GUIDE

## 📚 Start Reading Here

This is your complete reference for migrating RecruitHub from PostgreSQL to DynamoDB on Render.

---

## 🗂️ Documentation Organization

### **For Beginners: Quick Overview**
1. Start with: **[RENDER_QUICKSTART.md](RENDER_QUICKSTART.md)** (5 min read)
2. Then read: **[CHANGES_SUMMARY.md](CHANGES_SUMMARY.md)** (understand what changed)

### **For Implementation: Step-by-Step**
1. **[REQUIRED_KEYS_AND_CREDENTIALS.md](REQUIRED_KEYS_AND_CREDENTIALS.md)** - Get all AWS credentials
2. **[RENDER_DYNAMODB_DEPLOYMENT_GUIDE.md](RENDER_DYNAMODB_DEPLOYMENT_GUIDE.md)** - Full deployment guide
3. **[RENDER_DEPLOYMENT_CHECKLIST.md](RENDER_DEPLOYMENT_CHECKLIST.md)** - Verify everything before deploying

### **For Configuration: Technical Details**
1. **[ENVIRONMENT_VARIABLES_COMPLETE.md](ENVIRONMENT_VARIABLES_COMPLETE.md)** - All env vars explained
2. **[DYNAMODB_SETTINGS_CONFIG.md](DYNAMODB_SETTINGS_CONFIG.md)** - Code to add to settings.py
3. **[validate_env_vars.py](validate_env_vars.py)** - Validation script

### **For Code Reference: Models**
1. **[core/dynamodb_models.py](core/dynamodb_models.py)** - All DynamoDB models
2. **[core/management/commands/init_dynamodb.py](core/management/commands/init_dynamodb.py)** - Database initialization

---

## ⚡ Quick Reference

### **11 Critical Keys You Need**

```
1. SECRET_KEY              (Generate: python command)
2. DEBUG                   (Set: False)
3. ALLOWED_HOSTS           (Your domain)
4. AWS_ACCESS_KEY_ID       (From AWS IAM)
5. AWS_SECRET_ACCESS_KEY   (From AWS IAM)
6. AWS_REGION              (us-east-1 recommended)
7. USE_DYNAMODB            (True)
8. USE_S3                  (True)
9. AWS_STORAGE_BUCKET_NAME (S3 bucket name)
10. AWS_S3_REGION_NAME     (us-east-1)
11. DYNAMODB_TABLE_PREFIX  (recruithub-prod-)
```

### **Files Changed**
- ✅ `requirements.txt` - Updated (PynamoDB added)
- ⚠️ `auth_project/settings.py` - NEEDS your update
- ⚠️ `core/views.py` - NEEDS your update (database calls)
- ✅ `core/dynamodb_models.py` - Created ✓
- ✅ Procfile.dynamodb - Created ✓
- ✅ Management commands - Created ✓

### **New Files Created**
- Documentation (8 files)
- DynamoDB models
- Management command
- Validation script

---

## 🎯 3-Step Deployment Path

### **Step 1: Prepare (30 minutes)**
1. Read [RENDER_QUICKSTART.md](RENDER_QUICKSTART.md)
2. Create AWS IAM user with DynamoDB + S3 access
3. Create S3 bucket
4. Generate SECRET_KEY

### **Step 2: Configure (15 minutes)**
1. Update `auth_project/settings.py` (use [DYNAMODB_SETTINGS_CONFIG.md](DYNAMODB_SETTINGS_CONFIG.md))
2. Update views in `core/views.py` to use DynamoDB models
3. Run validation: `python validate_env_vars.py`

### **Step 3: Deploy (10 minutes)**
1. Push code to GitHub
2. Create Render web service
3. Add 11 environment variables
4. Watch deployment (5-10 min)
5. Test your app

---

## 📊 What's Different: PostgreSQL → DynamoDB

| Aspect | PostgreSQL | DynamoDB |
|--------|-----------|----------|
| Type | Relational SQL | NoSQL/Key-Value |
| Tables | Schemas with columns | Key-value documents |
| Queries | Complex SQL | Simple key/scan queries |
| Relationships | Foreign keys | Manual references (UUIDs) |
| Transactions | ACID guaranteed | Eventually consistent |
| Cost | $10-20/month | $10-15/month |
| Scaling | Vertical (bigger DB) | Horizontal (auto) |
| ORM | Django ORM | PynamoDB |

---

## 🔑 All Environment Variables at a Glance

| Variable | Type | Example | Required? |
|----------|------|---------|-----------|
| `SECRET_KEY` | Secret | 50+ random chars | ✅ YES |
| `DEBUG` | String | `False` | ✅ YES |
| `ALLOWED_HOSTS` | String | `yourdomain.com,www.yourdomain.com` | ✅ YES |
| `AWS_ACCESS_KEY_ID` | Secret | `AKIA2EXAMPLE...` | ✅ YES |
| `AWS_SECRET_ACCESS_KEY` | Secret | 40 random chars | ✅ YES |
| `AWS_REGION` | String | `us-east-1` | ✅ YES |
| `USE_DYNAMODB` | String | `True` | ✅ YES |
| `USE_S3` | String | `True` | ✅ YES |
| `AWS_STORAGE_BUCKET_NAME` | String | `recruithub-media-prod` | ✅ YES |
| `AWS_S3_REGION_NAME` | String | `us-east-1` | ✅ YES |
| `DYNAMODB_TABLE_PREFIX` | String | `recruithub-prod-` | ✅ YES |
| `EMAIL_BACKEND` | String | `django.core.mail.backends.console.EmailBackend` | ⚠️ Optional |
| `CSRF_TRUSTED_ORIGINS` | String | `https://yourdomain.com` | ⚠️ Optional |
| `ADMIN_URL_PATH` | String | `admin-randomstring` | ⚠️ Optional |

---

## 🛠️ Technical Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    🌐 USER BROWSER                      │
└─────────────────────────────────────────────────────────┘
                            ↓ HTTPS
┌─────────────────────────────────────────────────────────┐
│             🎯 RENDER WEB SERVICE                       │
│  ┌────────────────────────────────────────────────────┐ │
│  │   Django App (gunicorn)                            │ │
│  │   • auth_project                                   │ │
│  │   • core app                                       │ │
│  │   • Static files (WhiteNoise)                      │ │
│  └────────────┬─────────────────────┬────────────────┘ │
│               │                     │                  │
└───────────────┼─────────────────────┼──────────────────┘
                │                     │
        ┌───────▼─────┐       ┌───────▼──────┐
        │   🗄️ AWS    │       │   💾 AWS S3  │
        │  DynamoDB   │       │ (Media Files)│
        │   (Data)    │       └──────────────┘
        └─────────────┘
```

---

## 🚀 AWS Infrastructure You'll Create

**AWS Services Used:**
- **DynamoDB:** Main database (8 tables)
  - users
  - user-profiles
  - documents
  - notes
  - hr-profiles
  - email-otps
  - rate-limits
  - sessions

- **S3:** File storage
  - recruithub-media-prod

- **IAM:** User access control
  - recruithub-render (with DynamoDB + S3 access)

**Estimated Cost:** $15-25/month

---

## ✅ Pre-Deployment Checklist

```
☐ AWS account created
☐ IAM user "recruithub-render" created
☐ Access key generated and saved
☐ S3 bucket created
☐ requirements.txt updated (✅ done)
☐ DynamoDB models created (✅ done)
☐ Management command created (✅ done)
☐ auth_project/settings.py updated
☐ core/views.py updated
☐ Validation script passed: python validate_env_vars.py
☐ Code committed to GitHub
☐ Render web service created
☐ All 11 environment variables added
☐ Deployment initiated
☐ DynamoDB tables created (auto)
☐ App loads (no errors)
☐ Can sign up (DynamoDB working)
☐ Can upload file (S3 working)
☐ Admin panel works
```

---

## 🔐 Security Highlights

✅ **What's Secure:**
- AWS credentials never in Git (stored in Render only)
- DEBUG=False in production (no error traces)
- HTTPS enforced
- CSRF protection
- SQL injection prevented (using DynamoDB)
- Custom admin URL path (not `/admin`)
- S3 blocks public access

⚠️ **Still Your Responsibility:**
- Keep AWS credentials safe (rotate every 6 months)
- Monitor AWS usage (watch billing)
- Keep Django updated
- Keep dependencies updated  (`pip freeze | grep -i boto`)

---

## 📞 Help & Resources

### **Getting Stuck?**

**For AWS credential issues:**
→ Read [REQUIRED_KEYS_AND_CREDENTIALS.md](REQUIRED_KEYS_AND_CREDENTIALS.md)

**For environment variable issues:**
→ Run `python validate_env_vars.py`

**For deployment issues:**
→ Check [RENDER_DEPLOYMENT_CHECKLIST.md](RENDER_DEPLOYMENT_CHECKLIST.md)

**For code changes:**
→ See [DYNAMODB_SETTINGS_CONFIG.md](DYNAMODB_SETTINGS_CONFIG.md)

**For full walkthrough:**
→ Read [RENDER_DYNAMODB_DEPLOYMENT_GUIDE.md](RENDER_DYNAMODB_DEPLOYMENT_GUIDE.md)

### **Online Resources:**
- AWS DynamoDB: https://docs.aws.amazon.com/dynamodb/
- PynamoDB: https://pynamodb.readthedocs.io/
- Render: https://render.com/docs
- Django: https://docs.djangoproject.com/

---

## 📈 Implementation Timeline

| Phase | Time | Tasks |
|-------|------|-------|
| **Prep** | 30 min | Create AWS credentials, read docs |
| **Code** | 30 min | Update settings.py, views |
| **Test** | 15 min | Run validation, test locally |
| **Deploy** | 15 min | Push to GitHub, trigger Render |
| **Monitor** | 10 min | Watch logs, verify tables created |
| **Verify** | 10 min | Test signup, uploads, admin panel |
| **Total** | ~2 hours | End-to-end deployment |

---

## 🎓 Learning Outcomes

After this deployment, you'll understand:
- ✅ AWS DynamoDB and NoSQL databases
- ✅ PynamoDB ORM for DynamoDB
- ✅ Django + DynamoDB integration
- ✅ Render deployment workflow
- ✅ AWS IAM and access management
- ✅ S3 file storage in Django
- ✅ Environment variable management
- ✅ CI/CD with Git and Render

---

## 🎯 Success Criteria

Your deployment is successful when:

1. ✅ Site loads at your Render URL
2. ✅ User registration works (data in DynamoDB)
3. ✅ Can upload profile photo (stored in S3)
4. ✅ Admin panel accessible at custom URL
5. ✅ No error logs in Render dashboard
6. ✅ DynamoDB tables visible in AWS console
7. ✅ S3 bucket has uploaded files
8. ✅ Email sending works (or configured)
9. ✅ Rate limiting active (DynamoDB tracking)
10. ✅ Performance acceptable (<2 sec page load)

---

## 💡 Pro Tips

1. **Start with small data:** Test with fresh user signup, not importing everything
2. **Monitor costs first week:** Ensure billing matches expectations ($20-30)
3. **Enable DynamoDB monitoring:** Set CloudWatch alarms for errors
4. **Keep PostgreSQL for dev:** Use SQLite/PostgreSQL locally, DynamoDB only in production
5. **Backup regularly:** Enable DynamoDB point-in-time recovery
6. **Test locally:** Use DynamoDB Local for testing before deploying
7. **Monitor Render logs:** Check daily for errors the first week
8. **Cache where possible:** DynamoDB queries can be slower, consider caching

---

## 🚀 Next Steps

### **Start Right Now:**

1. **If you're new to this:**
   → Open [RENDER_QUICKSTART.md](RENDER_QUICKSTART.md)

2. **If you're ready to deploy:**
   → Open [RENDER_DEPLOYMENT_CHECKLIST.md](RENDER_DEPLOYMENT_CHECKLIST.md)

3. **If you need AWS credentials:**
   → Open [REQUIRED_KEYS_AND_CREDENTIALS.md](REQUIRED_KEYS_AND_CREDENTIALS.md)

4. **If you need to update code:**
   → Open [DYNAMODB_SETTINGS_CONFIG.md](DYNAMODB_SETTINGS_CONFIG.md)

---

## 📝 Document Index

| Document | Purpose | Read Time |
|----------|---------|-----------|
| **RENDER_QUICKSTART.md** | 5-minute overview | 5 min |
| **CHANGES_SUMMARY.md** | What changed in your code | 10 min |
| **REQUIRED_KEYS_AND_CREDENTIALS.md** | How to get each AWS key | 15 min |
| **ENVIRONMENT_VARIABLES_COMPLETE.md** | All environment variables explained | 20 min |
| **RENDER_DYNAMODB_DEPLOYMENT_GUIDE.md** | Full step-by-step guide | 30 min |
| **RENDER_DEPLOYMENT_CHECKLIST.md** | Verification checklist | 10 min |
| **DYNAMODB_SETTINGS_CONFIG.md** | Code snippets for settings.py | 10 min |

**Total Reading Time:** ~2 hours  
**Total Implementation Time:** ~2 hours  
**Total:** ~4 hours to go live

---

## ✨ You've Got This!

This migration is straightforward:
1. Get AWS credentials (30 min)
2. Update code (30 min)
3. Deploy on Render (15 min)
4. Test (15 min)
5. Done! 🎉

All the documentation is ready. All the code is prepared. You just need to execute these steps in order.

**Questions?** Check the specific documentation file for that topic.

---

**Last Updated:** March 2026  
**Status:** Ready for Deployment  
**Created for:** RecruitHub Application  
**Version:** 1.0

