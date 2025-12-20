# 🚀 Deployment Guide for RecruitHub

## Quick Deploy Instructions

### Prerequisites
- Python 3.8+ installed
- Git installed
- pip package manager

### Step 1: Clone Repository
```bash
git clone https://github.com/yourusername/RecruitHub.git
cd RecruitHub
```

### Step 2: Create Virtual Environment
```bash
# On macOS/Linux
python3 -m venv .venv
source .venv/bin/activate

# On Windows
python -m venv .venv
.venv\Scripts\activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Apply Database Migrations
```bash
python manage.py migrate
```

### Step 5: Create Superuser (Optional - for Django Admin)
```bash
python manage.py createsuperuser
```

Follow prompts to set username and password.

### Step 6: Create Test HR Account
```bash
python manage.py shell
```

Then paste this code:
```python
from django.contrib.auth.models import User
from core.models import HRProfile

user = User.objects.create_user(
    username='hr_admin',
    email='hr@example.com',
    password='hr123456',
    first_name='HR',
    last_name='Admin'
)

HRProfile.objects.create(
    user=user,
    company_name='Your Company',
    designation='HR Manager',
    department='Human Resources'
)

print("✅ HR Account Created Successfully!")
```

Exit with: `exit()`

### Step 7: Run Development Server
```bash
python manage.py runserver
```

Server runs at: `http://127.0.0.1:8000`

---

## 🔑 Test Credentials

### HR Admin Login
- **URL:** `http://127.0.0.1:8000/hr/login/`
- **Username:** `hr_admin`
- **Password:** `hr123456`

### Sample Student Logins
Create your own or use these pre-created accounts:
- **Username:** `22CS001` | **Password:** `22CS00122CS001`
- **Username:** `22IT010` | **Password:** `22IT01022IT010`
- **Username:** `22EE020` | **Password:** `22EE02022EE020`

---

## 📊 Create Dummy Students (200+)

Run this command to populate database with test students:

```bash
python manage.py shell
```

Paste this code:
```python
import random
from django.contrib.auth.models import User
from core.models import UserProfile

branches = {'CS': 'Computer Science', 'IF': 'Information Technology', 'EE': 'Electrical Engineering', 'CE': 'Civil Engineering', 'ME': 'Mechanical Engineering'}
first_names = ['Aarav', 'Vivaan', 'Arjun', 'Rohan', 'Ashish', 'Priya', 'Ananya', 'Shreya', 'Neha', 'Divya']
last_names = ['Sharma', 'Patel', 'Singh', 'Kumar', 'Gupta', 'Verma', 'Reddy', 'Iyer', 'Nair', 'Desai']
skills = ['Python', 'Java', 'React', 'Django', 'AWS', 'Docker', 'SQL', 'JavaScript', 'C++', 'Node.js']

created = 0
for branch_code in branches:
    for seq in range(1, 41):
        username = f'22{branch_code}{seq:03d}'
        if User.objects.filter(username=username).exists():
            continue
        
        password = f'{username}{username}'
        user = User.objects.create_user(
            username=username,
            email=f'{username}@college.edu',
            password=password,
            first_name=random.choice(first_names),
            last_name=random.choice(last_names)
        )
        
        profile = UserProfile.objects.get(user=user)
        profile.branch = branch_code
        profile.cgpa = round(random.uniform(6.2, 9.8), 2)
        profile.backlogs = random.randint(0, 2)
        profile.current_backlogs = random.randint(0, profile.backlogs) if profile.backlogs > 0 else 0
        profile.skills = ', '.join(random.sample(skills, 3))
        profile.github_username = f'user{seq}'
        profile.linkedin_username = f'user{seq}'
        profile.save()
        created += 1

print(f'✅ Created {created} dummy students')
```

Exit with: `exit()`

---

## 🌐 Production Deployment

### Before Going Live
1. **Update SECRET_KEY** in `auth_project/settings.py`
2. **Set DEBUG = False**
3. **Update ALLOWED_HOSTS** with your domain
4. **Use environment variables** for sensitive data
5. **Set up HTTPS** (SSL certificate)
6. **Configure database** (PostgreSQL recommended over SQLite)

### Heroku Deployment Example
```bash
# Install Heroku CLI first
heroku login
heroku create your-app-name
git push heroku main
heroku run python manage.py migrate
```

### AWS/Azure/DigitalOcean
Refer to platform-specific Django deployment guides.

---

## 🐛 Troubleshooting

### Port Already in Use
```bash
# Change port
python manage.py runserver 8080

# Or kill process on port 8000
# macOS/Linux
lsof -ti:8000 | xargs kill -9
```

### Database Errors
```bash
# Reset database (CAREFUL - deletes all data!)
rm db.sqlite3
python manage.py migrate
```

### Migration Issues
```bash
python manage.py makemigrations
python manage.py migrate --fake-initial
python manage.py migrate
```

---

## 📞 Support
- Check README.md for detailed documentation
- Review Django documentation: https://docs.djangoproject.com/
- Open GitHub Issues for bugs

---

**Happy deploying! 🎉**
