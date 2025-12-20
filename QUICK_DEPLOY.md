# 🎯 QUICK START - Deployment in 5 Steps

## Step 1: Generate NEW SECRET_KEY ⚡

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

**Copy the output** (looks like: `k7a!8@2x%q9p...`)

---

## Step 2: Update Settings 📝

Edit `auth_project/settings.py`:

**Line 25** - Replace this:
```python
SECRET_KEY = "change-this-to-a-new-secret-key-generated-on-deployment"
```

With your generated key:
```python
SECRET_KEY = "k7a!8@2x%q9p..."  # Your generated key
```

**Line 30** - Update for your domain:
```python
# For Heroku:
ALLOWED_HOSTS = ['your-app-name.herokuapp.com']

# For DigitalOcean:
ALLOWED_HOSTS = ['your-app.ondigitalocean.app']

# For local:
ALLOWED_HOSTS = ['localhost', '127.0.0.1']
```

---

## Step 3: Collect Static Files 📦

```bash
python manage.py collectstatic --noinput
```

---

## Step 4: Test Locally 🧪

```bash
python manage.py runserver
```

Visit: `http://127.0.0.1:8000/admintapdiyaom/` - Should work!

---

## Step 5: Deploy 🚀

### Option A: Heroku
```bash
# Commit changes
git add .
git commit -m "Production deployment configuration"
git push origin main

# Deploy to Heroku
heroku create your-app-name
heroku config:set SECRET_KEY='your-generated-key'
heroku config:set DEBUG=False
git push heroku main
heroku run python manage.py migrate
```

### Option B: DigitalOcean (Recommended)
1. Go to https://cloud.digitalocean.com/apps
2. Click "Create App"
3. Connect GitHub (Om-mac/RecruitHub)
4. Set environment variables:
   - `SECRET_KEY` = your-generated-key
   - `DEBUG` = False
   - `DATABASE_URL` = postgres://...
5. Click Deploy!

### Option C: PythonAnywhere
1. Upload files to PythonAnywhere
2. Create virtual environment
3. Install requirements: `pip install -r requirements.txt`
4. Configure web app
5. Set environment variables

---

## ✅ After Deployment

### Create Admin Account
```bash
# On deployed server
python manage.py createsuperuser
```

### Create HR Account
```bash
python manage.py shell
```

Then paste:
```python
from django.contrib.auth.models import User
from core.models import HRProfile

user = User.objects.create_user(username='hr_admin', password='hr123456')
HRProfile.objects.create(user=user, company_name='Your Company')
```

---

## 🔐 Your Live URLs

```
Admin:     https://yourdomain.com/admintapdiyaom/
HR Login:  https://yourdomain.com/hr/login/
Student:   https://yourdomain.com/login/
```

---

## ⚠️ CRITICAL REMINDERS

- ✅ Generate NEW SECRET_KEY (don't use old one)
- ✅ Set DEBUG = False (already done)
- ✅ Update ALLOWED_HOSTS for your domain
- ✅ Run collectstatic
- ✅ Commit to GitHub
- ❌ Never commit `.env` or secret keys

---

**Ready to deploy? Follow these 5 steps! 🚀**
