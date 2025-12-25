# 📋 Pre-Deployment Checklist for RecruitHub

## ✅ Changes Made So Far

### 1. ✓ Admin URL Changed
```
OLD: /admin/
NEW: /admintapdiyaom/
```
Updated in `auth_project/urls.py`

---

## 🔒 Security Changes Needed

### 1. **Change SECRET_KEY** (CRITICAL!)

In `auth_project/settings.py`, line 25:

**Current:**
```python
SECRET_KEY = "django-insecure-!8#rn*8@i9$h=#8+4g!)v(7#gz7ph84yqf0onvzo0eqz&^x+pn"
```

**Generate new one:**
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

**Replace with output like:**
```python
SECRET_KEY = "your-newly-generated-secret-key-here"
```

---

### 2. **Set DEBUG = False** (CRITICAL!)

In `auth_project/settings.py`, line 28:

**Change from:**
```python
DEBUG = True
```

**To:**
```python
DEBUG = False
```

---

### 3. **Update ALLOWED_HOSTS**

In `auth_project/settings.py`, line 30:

**Change from:**
```python
ALLOWED_HOSTS = []
```

**To (if deploying locally for testing):**
```python
ALLOWED_HOSTS = ['127.0.0.1', 'localhost', 'vakverse.com', 'www.vakverse.com']
```

**Or for DigitalOcean:**
```python
ALLOWED_HOSTS = ['your-app.ondigitalocean.app', 'yourdomain.com']
```

---

### 4. **Add Static Files Configuration**

In `auth_project/settings.py`, after `MEDIA_ROOT` (around line 119):

```python
# Static files (CSS, JavaScript, Images)
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"  # Add this line

# For production, ensure this is set
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

# Security Settings for Production
SECURE_SSL_REDIRECT = not DEBUG
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_SECURITY_POLICY = {
    "default-src": ("'self'",),
}
```

---

### 5. **Update Database (For Production)**

**Option A: Keep SQLite (Simpler)**
```python
# Already configured, but ensure DATABASES is set properly
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}
```

**Option B: Use PostgreSQL (Recommended for Production)**

First, add to `requirements.txt`:
```
psycopg2-binary==2.9.9
dj-database-url==2.0.0
python-decouple==3.8
```

Then in settings:
```python
import dj_database_url
from decouple import config

DATABASES = {
    'default': dj_database_url.config(
        default='sqlite:///db.sqlite3',
        conn_max_age=600
    )
}
```

---

## 📦 Dependencies for Production

Update `requirements.txt`:

```bash
pip install gunicorn psycopg2-binary python-decouple dj-database-url
pip freeze > requirements.txt
```

**Final requirements.txt should include:**
```
Django==6.0.0
Pillow==10.0.0
django-filter==23.1
sqlparse==0.4.4
asgiref==3.7.1
gunicorn==21.2.0
psycopg2-binary==2.9.9
dj-database-url==2.0.0
python-decouple==3.8
```

---

## 🚀 Platform-Specific Files

### If Deploying to Heroku

Create `Procfile` in project root:
```
web: gunicorn auth_project.wsgi
```

Create `runtime.txt` in project root:
```
python-3.11.9
```

---

### If Deploying to DigitalOcean

Create `.do/app.yaml` in project root:
```yaml
name: recruitapp
services:
- name: web
  github:
    repo: Om-mac/RecruitHub
    branch: main
  build_command: pip install -r requirements.txt && python manage.py collectstatic
  run_command: gunicorn auth_project.wsgi:application
  environment_slug: python
```

---

### If Using Docker

Create `Dockerfile` in project root:
```dockerfile
FROM python:3.11

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
RUN python manage.py collectstatic --noinput
EXPOSE 8000
CMD ["gunicorn", "auth_project.wsgi:application", "--bind", "0.0.0.0:8000"]
```

---

## 📝 Environment Variables (For Production)

Create `.env` file (Never commit to git!):

```
SECRET_KEY=your-generated-secret-key-here
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
DATABASE_URL=postgresql://user:password@db-server:5432/recruitdb
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

Add to `.gitignore`:
```
.env
.env.local
*.pem
*.key
```

---

## ✅ Final Pre-Deployment Checklist

### Security
- [ ] Change SECRET_KEY to generated value
- [ ] Set DEBUG = False
- [ ] Update ALLOWED_HOSTS with your domain
- [ ] Add security middleware settings
- [ ] Add CSRF and SSL settings
- [ ] Update CORS settings if using API

### Database
- [ ] Choose database (SQLite or PostgreSQL)
- [ ] Test database connection
- [ ] Ensure all migrations are applied

### Static Files
- [ ] Configure STATIC_ROOT
- [ ] Run `python manage.py collectstatic`
- [ ] Test static file serving

### Dependencies
- [ ] Update requirements.txt
- [ ] Install gunicorn
- [ ] Install psycopg2-binary (if using PostgreSQL)
- [ ] Install python-decouple (for environment variables)

### Platform Files
- [ ] Create Procfile (for Heroku)
- [ ] Create runtime.txt (for Heroku)
- [ ] Or create appropriate files for your platform

### Git
- [ ] Add .env to .gitignore
- [ ] Commit all changes
- [ ] Push to GitHub

### Testing
- [ ] Test locally with DEBUG=False
- [ ] Test admin panel at /admintapdiyaom/
- [ ] Test student login
- [ ] Test HR login
- [ ] Verify static files load

### Post-Deployment
- [ ] Create superuser
- [ ] Create HR admin account
- [ ] Test live application
- [ ] Check error logs
- [ ] Setup monitoring

---

## 🔑 Quick Commands

```bash
# Generate new SECRET_KEY
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# Collect static files
python manage.py collectstatic --noinput

# Run tests locally with DEBUG=False
DEBUG=False python manage.py runserver

# Test specific deployment
python manage.py check --deploy

# Create superuser
python manage.py createsuperuser

# Create migrations (if needed)
python manage.py makemigrations
python manage.py migrate
```

---

## 📊 Settings.py Changes Summary

```python
# Line 25 - CHANGE THIS
SECRET_KEY = "django-insecure-..." → SECRET_KEY = "your-new-key-here"

# Line 28 - CHANGE THIS
DEBUG = True → DEBUG = False

# Line 30 - CHANGE THIS
ALLOWED_HOSTS = [] → ALLOWED_HOSTS = ['yourdomain.com', 'localhost']

# After line 119 - ADD THESE
STATIC_ROOT = BASE_DIR / "staticfiles"
SECURE_SSL_REDIRECT = not DEBUG
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG
```

---

## 🎯 Next Steps

1. **Update settings.py** with all security changes
2. **Generate new SECRET_KEY** and replace old one
3. **Update requirements.txt** with production dependencies
4. **Create deployment files** (Procfile, etc.)
5. **Test locally** with DEBUG=False
6. **Commit changes** to GitHub
7. **Deploy to your chosen platform**

---

## ⚠️ CRITICAL

**Do NOT deploy with:**
- ❌ DEBUG = True
- ❌ Old SECRET_KEY
- ❌ Empty ALLOWED_HOSTS
- ❌ SQLite for production (use PostgreSQL)

---

**Ready to proceed? Let me know once you've made these changes!** ✅
