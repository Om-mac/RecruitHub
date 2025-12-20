# 🚀 RecruitHub - Complete Deployment Guide

## Deployment Options

Choose one of the following platforms to deploy your RecruitHub application.

---

## 📋 Pre-Deployment Checklist

Before deploying to any platform:

- [ ] Update `SECRET_KEY` in `auth_project/settings.py`
- [ ] Set `DEBUG = False` in settings
- [ ] Update `ALLOWED_HOSTS` with your domain
- [ ] Create `.env` file with environment variables
- [ ] Set up a production database (PostgreSQL recommended)
- [ ] Configure static files collection
- [ ] Setup HTTPS/SSL certificate
- [ ] Create superuser account
- [ ] Test the application locally

---

## 🔧 Required Environment Variables

Create a `.env` file in your project root:

```
SECRET_KEY=your-super-secret-key-change-this
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
DATABASE_URL=postgresql://user:password@localhost/recruitdb
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

---

## Option 1: Heroku (Easiest for Beginners)

### Prerequisites
- Heroku account (free tier available)
- Heroku CLI installed
- GitHub repository (already done!)

### Steps

1. **Install Heroku CLI:**
   ```bash
   brew tap heroku/brew && brew install heroku
   ```

2. **Login to Heroku:**
   ```bash
   heroku login
   ```

3. **Create Heroku App:**
   ```bash
   heroku create your-app-name
   ```

4. **Add PostgreSQL:**
   ```bash
   heroku addons:create heroku-postgresql:hobby-dev
   ```

5. **Create Procfile** (in project root):
   ```
   web: gunicorn auth_project.wsgi
   ```

6. **Create runtime.txt** (in project root):
   ```
   python-3.11.9
   ```

7. **Update requirements.txt** - Add these:
   ```bash
   pip install gunicorn psycopg2-binary python-decouple
   pip freeze > requirements.txt
   ```

8. **Set Environment Variables:**
   ```bash
   heroku config:set SECRET_KEY='your-new-secret-key'
   heroku config:set DEBUG=False
   heroku config:set ALLOWED_HOSTS='your-app.herokuapp.com'
   ```

9. **Deploy:**
   ```bash
   git push heroku main
   ```

10. **Run Migrations:**
    ```bash
    heroku run python manage.py migrate
    ```

11. **Create Superuser:**
    ```bash
    heroku run python manage.py createsuperuser
    ```

12. **Visit Your App:**
    ```bash
    heroku open
    ```

**Cost:** Free tier available (with limitations)  
**Pros:** Easy setup, automatic HTTPS, minimal configuration  
**Cons:** Limited free tier resources, can be expensive at scale

---

## Option 2: PythonAnywhere (Django-Friendly)

### Steps

1. **Create Account:** https://www.pythonanywhere.com

2. **Upload Your Code:**
   - Use Git to clone from GitHub
   - Or upload files manually

3. **Set Up Virtual Environment:**
   ```bash
   mkvirtualenv --python=/usr/bin/python3.11 recruitapp
   pip install -r requirements.txt
   pip install django psycopg2-binary
   ```

4. **Configure Web App:**
   - Go to Web tab
   - Add new web app
   - Select Django framework
   - Point to your project

5. **Update WSGI File:**
   - Edit the WSGI configuration file
   - Point to `auth_project/wsgi.py`

6. **Set Environment Variables:**
   - In Web app settings, add environment variables

7. **Reload Web App:**
   - Click "Reload" button

8. **Run Migrations:**
   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   ```

**Cost:** Starting at $5/month  
**Pros:** Django-focused, easy setup, good documentation  
**Cons:** Less flexibility than full VPS

---

## Option 3: DigitalOcean App Platform (Recommended)

### Steps

1. **Create DigitalOcean Account:** https://www.digitalocean.com

2. **Connect GitHub:**
   - Go to Apps > Create App
   - Connect your GitHub account
   - Select RecruitHub repository

3. **Configure App:**
   - Resource type: Web Service
   - Runtime: Python
   - Build command: `pip install -r requirements.txt`
   - Run command: `gunicorn auth_project.wsgi`

4. **Add Database:**
   - Create PostgreSQL database
   - Note the connection string

5. **Set Environment Variables:**
   ```
   DATABASE_URL=postgres://...
   SECRET_KEY=your-secret-key
   DEBUG=False
   ALLOWED_HOSTS=your-app.ondigitalocean.app
   ```

6. **Deploy:**
   - Click "Deploy"
   - DigitalOcean will build and deploy automatically

7. **Run Migrations:**
   ```bash
   doctl apps create-deployment <app-id> --wait
   ```

**Cost:** $5-12/month  
**Pros:** Good performance, reasonable cost, easy GitHub integration  
**Cons:** Requires more setup than Heroku

---

## Option 4: AWS (Most Scalable)

### Using Elastic Beanstalk (Easier)

1. **Install AWS CLI:**
   ```bash
   pip install awsebcli
   ```

2. **Initialize EB App:**
   ```bash
   eb init -p python-3.11 recruitapp
   ```

3. **Create `.ebextensions/django.config`:**
   ```yaml
   option_settings:
     aws:elasticbeanstalk:container:python:
       WSGIPath: auth_project:wsgi.application
     aws:elasticbeanstalk:application:environment:
       PYTHONPATH: /var/app/current:$PYTHONPATH
       SECRET_KEY: your-secret-key
       DEBUG: false
   commands:
     01_migrate:
       command: "source /var/app/venv/*/bin/activate && python manage.py migrate"
       leader_only: true
   ```

4. **Create Environment:**
   ```bash
   eb create recruitapp-env
   ```

5. **Deploy:**
   ```bash
   eb deploy
   ```

**Cost:** Variable (free tier available)  
**Pros:** Highly scalable, auto-scaling, many services integrated  
**Cons:** Complex setup, steeper learning curve

---

## Option 5: Docker + Docker Hub (Advanced)

### Create Dockerfile

```dockerfile
FROM python:3.11

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN python manage.py collectstatic --noinput

EXPOSE 8000

CMD ["gunicorn", "auth_project.wsgi:application", "--bind", "0.0.0.0:8000"]
```

### Create docker-compose.yml

```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "8000:8000"
    environment:
      DEBUG: "False"
      SECRET_KEY: your-secret-key
      DATABASE_URL: postgresql://user:password@db:5432/recruitdb
    depends_on:
      - db
    command: gunicorn auth_project.wsgi:application --bind 0.0.0.0:8000

  db:
    image: postgres:13
    environment:
      POSTGRES_DB: recruitdb
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

### Deploy with Docker

```bash
docker-compose up -d
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
```

**Cost:** Depends on hosting  
**Pros:** Reproducible, portable, modern approach  
**Cons:** Requires Docker knowledge

---

## Production Settings Update

Update `auth_project/settings.py`:

```python
import os
from decouple import config

# Security
SECRET_KEY = config('SECRET_KEY')
DEBUG = config('DEBUG', default=False, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost').split(',')

# Database
if 'DATABASE_URL' in os.environ:
    import dj_database_url
    DATABASES = {
        'default': dj_database_url.config()
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# HTTPS
SECURE_SSL_REDIRECT = not DEBUG
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_SECURITY_POLICY = {
    "default-src": ("'self'",),
}

# Static files
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
```

---

## Recommendation: Deploy on DigitalOcean

**Best balance of ease and cost:**

1. ✅ Simple GitHub integration
2. ✅ Affordable ($5-12/month)
3. ✅ Good performance
4. ✅ Easy to scale
5. ✅ Free SSL certificate
6. ✅ PostgreSQL included

### Quick DigitalOcean Deploy

```bash
# 1. Push to GitHub (already done!)
git push origin main

# 2. On DigitalOcean:
# - Create new app
# - Connect GitHub repository
# - Set environment variables
# - Deploy

# 3. That's it! Your app is live!
```

---

## Post-Deployment Steps

1. **Create Superuser:**
   ```bash
   python manage.py createsuperuser
   ```

2. **Create HR Admin Account:**
   ```bash
   python manage.py shell
   ```
   ```python
   from django.contrib.auth.models import User
   from core.models import HRProfile
   
   user = User.objects.create_user(username='hr_admin', password='hr123456')
   HRProfile.objects.create(user=user, company_name='Your Company')
   ```

3. **Collect Static Files:**
   ```bash
   python manage.py collectstatic
   ```

4. **Setup Email (Optional):**
   - Configure EMAIL settings in settings.py
   - Update SMTP credentials

5. **Setup Backups:**
   - Configure automated database backups
   - Store media files in cloud storage (S3, DigitalOcean Spaces)

---

## Monitoring & Maintenance

### Logs
```bash
# Heroku
heroku logs --tail

# DigitalOcean
doctl apps logs list <app-id>
```

### Database Backups
```bash
# Local backup
python manage.py dumpdata > backup.json

# Restore
python manage.py loaddata backup.json
```

### Update Dependencies
```bash
pip list --outdated
pip install --upgrade [package-name]
pip freeze > requirements.txt
git push
```

---

## Common Issues & Solutions

### Issue: Static Files Not Loading
**Solution:** Run `python manage.py collectstatic`

### Issue: Database Connection Error
**Solution:** Check DATABASE_URL environment variable

### Issue: Email Not Sending
**Solution:** Verify SMTP credentials and email configuration

### Issue: 502 Bad Gateway
**Solution:** Check application logs, restart server

---

## SSL Certificate

Most platforms provide free SSL:
- Heroku: Automatic
- DigitalOcean: Automatic
- PythonAnywhere: Included
- AWS: Use AWS Certificate Manager (free)

---

## Scaling Tips

1. Use CDN for static files
2. Enable caching (Redis)
3. Use PostgreSQL (not SQLite in production)
4. Setup load balancing
5. Monitor performance

---

## Next Steps

1. **Choose deployment platform** (Recommended: DigitalOcean)
2. **Create account** on chosen platform
3. **Follow platform-specific steps** above
4. **Set environment variables**
5. **Deploy and test**
6. **Share live URL** with team

---

**Your RecruitHub is ready to go live! 🚀**
