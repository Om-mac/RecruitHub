# 🎯 Backend (Render) + Frontend (GitHub Pages) + NameCheap Domain Setup

## 📋 Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Your Domain (NameCheap)                  │
│                    youromain.com                             │
└────────────────┬────────────────────────────┬────────────────┘
                 │                            │
        ┌────────▼────────┐          ┌───────▼──────────┐
        │  Render Backend  │          │  GitHub Pages    │
        │  (Django API)    │          │  (Frontend)      │
        │  api.domain.com  │          │  www.domain.com  │
        └──────────────────┘          └──────────────────┘
```

---

## ✅ Step 1: Push Current Backend to GitHub

### A. Add all deployment files

```bash
cd /Users/tapdiyaom/Desktop/Authentication

# Check what's ready to push
git status

# Stage all changes
git add .

# Commit
git commit -m "Configure for production deployment - Render backend setup"

# Push to GitHub
git push origin main
```

### B. Verify Push

```bash
git log --oneline -5
```

You should see your commit at the top!

---

## 🚀 Step 2: Deploy Backend to Render

### A. Create Render Account

1. Go to https://render.com
2. Sign up with GitHub
3. Connect your GitHub account

### B. Create New Web Service

1. Click "New +" → Select "Web Service"
2. Connect your GitHub repository (Om-mac/RecruitHub)
3. Choose branch: `main`

### C. Configure Service

**Name:** `recruitapp-backend`

**Environment:** Python 3

**Build Command:**
```bash
pip install -r requirements.txt && python manage.py migrate && python manage.py collectstatic --noinput
```

**Start Command:**
```bash
gunicorn auth_project.wsgi:application
```

### D. Set Environment Variables

Click "Environment" and add:

```
SECRET_KEY=ciamvzsh2g=nsy4e3iv--k-(uprh_hltzc%gd9_s0%sa@^pt6l3
DEBUG=False
ALLOWED_HOSTS=api.yourdomain.com,localhost
DATABASE_URL=postgresql://...  (if using PostgreSQL)
```

### E. Deploy

Click "Deploy" button. Render will build and deploy automatically!

**Your backend URL:** `https://recruitapp-backend.onrender.com`

---

## 🌐 Step 3: Setup Frontend (Optional - if separating frontend)

### Option A: Keep Backend with Frontend (Current Setup - RECOMMENDED)

RecruitHub serves both frontend (templates) and backend from same Django instance:
- No changes needed
- Simpler to manage
- Domain points to Render backend

### Option B: Separate Frontend to GitHub Pages

**Only do this if you want pure REST API backend:**

1. Create separate React/Vue frontend repository
2. Build frontend to `docs/` folder
3. Deploy to GitHub Pages

---

## 🎯 Step 4: Configure NameCheap Domain

### A. Get Your Render Backend URL

After deployment, Render gives you: `https://recruitapp-backend.onrender.com`

### B. Login to NameCheap

1. Go to https://www.namecheap.com/myaccount/login/
2. Login to your account

### C. Configure DNS Records

1. Go to **Dashboard** → Click your domain
2. Click **Manage** next to your domain
3. Go to **Advanced DNS** tab
4. Add the following records:

**For Option 1 (Recommended - Keep Both Together):**

| Type | Host | Value | TTL |
|------|------|-------|-----|
| CNAME | @ | `recruitapp-backend.onrender.com` | 3600 |
| CNAME | www | `yourdomain.com` | 3600 |

**For Option 2 (Separate API and Frontend):**

| Type | Host | Value | TTL |
|------|------|-------|-----|
| CNAME | @ | `recruit-pages.github.io` | 3600 |
| CNAME | www | `yourdomain.com` | 3600 |
| CNAME | api | `recruitapp-backend.onrender.com` | 3600 |

### D. Wait for DNS Propagation

DNS can take 24-48 hours to fully propagate.
Check status: https://www.whatsmydns.net/

---

## 📝 Update Django Settings for Domain

Edit `auth_project/settings.py` line 30:

```python
ALLOWED_HOSTS = ['yourdomain.com', 'www.yourdomain.com', 'api.yourdomain.com', 'recruitapp-backend.onrender.com']
```

Then push to GitHub:

```bash
git add auth_project/settings.py
git commit -m "Update ALLOWED_HOSTS for NameCheap domain"
git push origin main
```

Render will auto-redeploy!

---

## ✅ Test Your Setup

### Before DNS Propagates (Use Render URL)

```bash
# Test backend API
curl https://recruitapp-backend.onrender.com/
curl https://recruitapp-backend.onrender.com/hr/login/
curl https://recruitapp-backend.onrender.com/login/
```

### After DNS Propagates (Use Your Domain)

```bash
# Test with your domain
curl https://yourdomain.com/
curl https://yourdomain.com/<YOUR_ADMIN_PATH>/
curl https://yourdomain.com/hr/login/
```

---

## 🔐 Access Your App

### URLs After DNS Setup

```
Main App:        https://yourdomain.com
Admin Panel:     https://yourdomain.com/<YOUR_ADMIN_PATH>/
HR Portal:       https://yourdomain.com/hr/login/
Student Portal:  https://yourdomain.com/login/
API:             https://api.yourdomain.com/  (if separated)
```

---

## 📊 Architecture with Your Domain

```
yourdomain.com (NameCheap)
    ↓
    ├─→ www.yourdomain.com → Render Backend
    ├─→ api.yourdomain.com → Render Backend (separate subdomain)
    └─→ yourdomain.com → Render Backend
```

---

## 🚨 Troubleshooting

### Issue: Domain not connecting

**Solution:**
- Wait 24-48 hours for DNS propagation
- Check DNS records in NameCheap
- Verify ALLOWED_HOSTS includes your domain

### Issue: 404 on domain but works on Render URL

**Solution:**
- Check if domain is added to ALLOWED_HOSTS
- Restart Render service
- Check Render logs: Dashboard → Your Service → Logs

### Issue: Static files not loading

**Solution:**
- Ensure `collectstatic` ran successfully
- Check STATIC_ROOT and STATIC_URL in settings
- Restart Render service

---

## 🔄 Updating Your App

When you make changes:

```bash
# 1. Make changes locally
# 2. Test locally
# 3. Push to GitHub
git add .
git commit -m "Your update message"
git push origin main

# 4. Render auto-deploys from GitHub!
# Check Render dashboard to see build progress
```

---

## 💡 Performance Tips

1. **Enable Render's Redis** for caching
2. **Use PostgreSQL** instead of SQLite
3. **Setup monitoring** in Render dashboard
4. **Enable auto-scaling** if needed
5. **Setup email** for notifications

---

## 📞 Support Links

- **Render Docs:** https://render.com/docs
- **NameCheap DNS Guide:** https://www.namecheap.com/support/knowledgebase/
- **Django Deployment:** https://docs.djangoproject.com/en/6.0/howto/deployment/

---

## 🎯 Summary

### Current Setup (RECOMMENDED)

✅ Backend: Render  
✅ Frontend: Served by Django (same as backend)  
✅ Domain: NameCheap pointing to Render  

### Timeline

1. **Now:** Push to GitHub ✅
2. **5 minutes:** Deploy to Render
3. **1 hour:** Configure DNS in NameCheap
4. **24-48 hours:** DNS propagates
5. **Done:** App live on yourdomain.com!

---

**Ready to go live? Let's do this! 🚀**
