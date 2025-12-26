# 🎓 RecruitHub - Campus Recruitment Portal

A comprehensive Django-based HR recruitment management system designed for colleges and placement cells to streamline student hiring processes with proper account type separation and security.

**Status:** ✅ Production Ready | **Version:** 2.0.0 | **Python:** 3.13 | **Django:** 6.0 | **Database:** PostgreSQL (Render) | **Hosting:** Render.com

---

## 📋 Table of Contents
1. [System Architecture](#system-architecture)
2. [Account Types & Separation](#account-types--separation)
3. [Features](#features)
4. [Registration Flows](#registration-flows)
5. [Security Implementation](#security-implementation)
6. [Admin Interface](#admin-interface)
7. [Deployment](#deployment)
8. [Recent Fixes & Improvements](#recent-fixes--improvements)

**Legal & Privacy:**
- [Privacy Policy](./PRIVACY_POLICY.md) - Data handling and user rights
- [Security Policy](./SECURITY.md) - Vulnerability reporting and security practices

---

## System Architecture

### Account Type Separation

RecruitHub implements **strict account type separation** to prevent unauthorized access:

```
┌─────────────────────────────────────────────────────────────┐
│                    Django User Account                      │
├─────────────────────────────────────────────────────────────┤
│ is_superuser=False │ is_staff=False │ Has OneToOne Profile  │
│    is_staff=False  │                │      ↓                │
│                    ├─→ STUDENT      │  UserProfile          │
│                    │   (Regular User)│  (Student Data)       │
│                    │                │                       │
│    is_staff=True   │ Has OneToOne    │      ↓                │
│                    ├─→ HR ACCOUNT   │  HRProfile            │
│                    │ (Recruiters)    │  (Company & Status)   │
│                    │                │                       │
│  is_superuser=True ├─→ ADMIN        │  No Profile           │
│   is_staff=True    │ (Management)    │  (Full Access)        │
└─────────────────────────────────────────────────────────────┘
```

### Database Models

**UserProfile** (Students)
- Personal: name, email, DOB, phone, address
- Education: branch, CGPA, backlogs, admission year, degree
- Professional: skills, experience, resume, bio
- Social: GitHub, LinkedIn, HackerRank usernames
- Media: profile_photo (AWS S3), resume (AWS S3)

**HRProfile** (Recruiters)
- Company details: name, designation, department
- Admin notes and approval status
- Approval workflow: requested_at, approved_by, approved_at
- Approval token for email verification

**EmailOTP**
- Stores OTP for email verification during registration
- Validates email ownership before account creation

---

## Account Types & Separation

### 1. **STUDENT ACCOUNTS** (Regular Users)
- **is_superuser:** False
- **is_staff:** False
- **Has Profile:** UserProfile (contains academic & professional data)
- **Permissions:** Can view own profile, upload resume, manage documents
- **Login:** `/accounts/login/` (Student Login)

**Blocked from:**
- Accessing HR features
- Viewing other student data
- Admin panel

### 2. **HR ACCOUNTS** (Recruiters)
- **is_superuser:** False
- **is_staff:** True (marked as staff to prevent student profile creation)
- **Has Profile:** HRProfile (contains company & approval status)
- **Permissions:** Can view filtered student directory, approve student hiring
- **Login:** `/hr/login/` (Dedicated HR Login)
- **Requirements:** Email verification + Admin approval before access

**Key Features:**
- Dashboard with student filtering and sorting
- View detailed student profiles
- Download student resumes

### 3. **ADMIN ACCOUNTS** (Management)
- **is_superuser:** True
- **is_staff:** True
- **Has Profile:** None (no student or HR profile)
- **Permissions:** Full system access, user management, HR approval
- **Login:** `/<ADMIN_URL_PATH>/` (Django Admin - set via environment variable)
- **Auto-created:** From environment variables on first deployment

**Key Features:**
- Approve/reject HR account registrations
- Manage all users and profiles
- View system statistics
- Configure system settings

---

## Features

### 🎓 Student Features

#### Authentication & Registration
- **Secure Registration:** OTP-based email verification (3-step process)
  - Step 1: Enter email → Receive OTP
  - Step 2: Verify OTP → Email confirmed
  - Step 3: Create account → Account active immediately
- **Login:** Blocked for HR/Admin accounts (must use HR or Admin login)
- **Password Management:**
  - Forgot password → OTP verification → Reset password
  - Change password (authenticated users only)

#### Profile Management
- Complete academic profile with CGPA and backlogs tracking
- Professional information (skills, experience, bio)
- Social media links (GitHub, LinkedIn, HackerRank, etc.)
- Profile photo upload (AWS S3)
- Resume upload (AWS S3)
- Dashboard showing profile completeness

#### Document Management
- Upload multiple resumes
- View uploaded documents
- Track upload dates and file sizes

#### Security Features
- **OTP Email Verification:** 10-minute countdown timer for registration
- **Password Reset OTP:** Secure password recovery with time-limited verification
- **Rate Limiting:** IP-based protection against brute force attacks
- **Session Management:** Automatic logout on inactivity
- **CSRF Protection:** Cross-site request forgery prevention
- **Secure Headers:** Content Security Policy, X-Frame-Options, etc.

### 👔 HR Features

#### Authentication & Registration
- **Dedicated HR Login:** Separate login page from students
- **HR Registration:** OTP-based 3-step registration
  - Step 1: Email verification
  - Step 2: OTP confirmation
  - Step 3: Account creation (marked as is_staff=True)
- **Approval Workflow:** 
  - Admin receives email with approval link
  - HR cannot access dashboard until approved
  - Shows "Pending Approval" message until admin action

#### Student Directory
- **View All Students:** Browse complete student profiles
- **Filter By:**
  - Branch/specialization
  - CGPA range (min/max)
  - Backlogs count (≤ specified number)
- **Sort By:**
  - CGPA (high→low, low→high)
  - Backlogs (ascending/descending)
  - Name (A→Z, Z→A)
  - Branch (alphabetical)

#### Student Details
- View complete student profile
- Profile photo and resume
- Skills and certifications
- Experience and bio
- Contact information
- Social media profiles with direct links
- Download resume functionality

### ⚙️ Admin Features

#### Dashboard
- Custom styling with brand colors
- Quick access to all management functions
- Statistics and system overview

#### User Management
- Create, edit, delete users
- Manage student and HR profiles
- View user activity and last login

#### HR Approval Workflow
- Bulk approve/reject HR registrations
- View pending HR account requests
- Automatic email notification on HR registration
- Approval status tracking with timestamps
- Admin notes and rejection reasons

#### System Configuration
- Manage environment variables
- Database management
- Email configuration
- AWS S3 storage settings

---

## Registration Flows

### Student Registration Flow
```
1. Click "Register"
   ↓
2. Enter Email → Receive OTP (email)
   ↓
3. Enter OTP → Verify (OTP valid for 10 minutes)
   ↓
4. Create Account (username + password)
   ↓
5. Auto-create UserProfile (student profile)
   ↓
6. Account Active → Can Login Immediately
```

### HR Registration Flow
```
1. Click "Register as HR"
   ↓
2. Enter Email → Receive OTP (email)
   ↓
3. Enter OTP → Verify Email
   ↓
4. Create Account (username + password)
   ↓
5. Set is_staff=True (prevent student profile creation)
   ↓
6. Delete any UserProfile (if auto-created)
   ↓
7. Create HRProfile (is_approved=False by default)
   ↓
8. Send Admin Approval Email
   ↓
9. Show "Pending Approval" until admin approves
   ↓
10. Admin Approves → HR Gets Dashboard Access
```

### Admin Account Creation
```
Environment Variables (Set in deployment):
- DJANGO_SUPERUSER_USERNAME=your-admin-username
- DJANGO_SUPERUSER_EMAIL=your-admin-email@domain.com
- DJANGO_SUPERUSER_PASSWORD=your-secure-password

On First Deployment:
↓
Django Initialization Script Runs
↓
Checks for Superuser
↓
If Not Exists → Creates Superuser from Env Vars
↓
Removes UserProfile if Created (signal handler)
↓
Admin Account Ready
```

---

## Security Implementation

### Account Type Protection

#### 1. **Signal-Based Profile Creation**
```python
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    # Only create UserProfile for non-staff, non-superuser accounts
    if created and not instance.is_staff and not instance.is_superuser:
        UserProfile.objects.get_or_create(user=instance)
    
    # Auto-cleanup: Remove UserProfile if user becomes staff/superuser
    if not created and (instance.is_staff or instance.is_superuser):
        UserProfile.objects.filter(user=instance).delete()
```

#### 2. **Student Login Blocking**
- Custom `StudentLoginView` prevents HR/Admin from student login
- Checks `is_staff` and `is_superuser` flags before login
- Shows error: "HR and Staff accounts must use the HR login page"
- Blocks early (before session creation)

#### 3. **HR Login Verification**
- Checks for `hr_profile` existence
- Verifies `is_approved` status
- Shows "Pending Approval" if not approved
- Only approved HR can access dashboard

#### 4. **HR Dashboard Protection**
- Checks `hr_profile` existence and approval status
- Excludes staff/superuser accounts from student list
- Prevents HR from accessing admin/student data
- Student detail view validates user type

### Data Filtering

#### Admin Interface
- **UserProfileAdmin:** Excludes `is_staff=True` and `is_superuser=True`
- **HRProfileAdmin:** Shows all HR profiles (pending and approved)
- **UserAdmin:** Filters to show only non-staff accounts

#### Views & Templates
- HR dashboard: `exclude(user__is_staff=True).exclude(user__is_superuser=True)`
- Student detail: Validates `not is_staff and not is_superuser`
- Prevents unauthorized data access through direct URLs

### Email Verification
- OTP-based verification for registration and password reset
- Time-limited tokens (10 minutes)
- Attempt limiting on OTP entries
- Prevents account takeover through email hijacking

### Rate Limiting & Brute Force Protection

#### IP-Based Rate Limiting
- **Middleware-based protection** for sensitive endpoints
- **Configurable limits** via environment variables
- **Automatic blocking** with HTTP 429 response
- **Clear messaging** with countdown timer for retry

#### Rate Limit Tiers
```
Endpoint                     Limit              Window
─────────────────────────────────────────────────────
Student Login                5 attempts         15 min
HR Login                      5 attempts         15 min
OTP Verification             5 attempts         10 min
OTP Request (Resend)         5 per hour        60 min
Registration (Student)       3 attempts         1 hour
Registration (HR)            3 attempts         1 hour
Password Reset Request       3 attempts         1 hour
Password Reset Verification  5 attempts         10 min
```

#### Countdown Timer Features
- **Visual Feedback:** MM:SS format countdown display
- **Color Coding:** Green → Orange → Red based on remaining time
- **Persistent Across Refresh:** Calculates from server timestamp
- **Auto-Expiry Messages:** Notifies when OTP expires
- **Auto-Redirect:** 429 error page auto-redirects when timer expires
- **Resend Cooldown:** 60-second button cooldown with countdown display

---

## Admin Interface

### Custom Admin Site
- **URL:** Custom admin path (configured in settings)
- **Authentication:** Requires superuser credentials
- **Styling:** Custom CSS with brand colors
- **Header:** "🎓 RecruitHub Admin Dashboard"
- **Features:** Dark mode support, responsive design
- **Security:** CSRF protection, session-based authentication

### Admin Sections

#### 1. **User Management**
- List all regular users (students)
- Filters: branch, degree, gender, CGPA
- Search: username, email, name
- Actions: Edit, delete

#### 2. **User Profiles (Students)**
- Displays student profiles
- Filtered to exclude staff/admin
- Readonly: user, created_at
- Editable: all profile fields
- Search by username, email, branch, skills

#### 3. **HR Profiles (Recruiters)**
- List all HR account registrations
- Status badges: ✓ Approved / ⏳ Pending
- Bulk actions: Approve / Reject
- Filters: Approval status, department, dates
- Search: username, company, designation
- Auto-counts total HR profiles in database

#### 4. **Documents**
- List uploaded resumes/documents
- Filter by upload date
- View file type and size
- Download functionality

#### 5. **Email OTP**
- Track OTP verifications
- View attempt counts
- Manage OTP records

### 🛡️ Rate Limiting & Security

#### IP-Based Rate Limiting
- **Login Attempts:** 5 attempts per 15 minutes
- **OTP Verification:** 5 attempts per 10 minutes
- **Registration:** 3 attempts per 1 hour
- **Password Reset:** 3 attempts per 1 hour

#### OTP Countdown Timer UI
- **Visual Countdown:** MM:SS format countdown display
- **Color Indicators:** 
  - Green (>50% time remaining)
  - Orange (20-50% time remaining)
  - Red (<20% time remaining)
- **Auto-Expiry:** Shows "OTP has expired" notification
- **Persistent Timer:** Continues accurately on page refresh (calculates from server timestamp)

#### Rate Limit Error Page
- **HTTP 429 Response:** Too Many Attempts error
- **Countdown Display:** Shows remaining wait time
- **Auto-Redirect:** Redirects after timer expires
- **Security Tips:** Guidance on account protection

#### Resend OTP Cooldown
- **60-Second Cooldown:** Prevents OTP spam
- **Real-Time Display:** Button shows countdown timer
- **Button State:** Disabled during cooldown, enabled after expiry

---

## Recent Fixes & Improvements

### Session: December 25, 2025

#### ✅ Countdown Timer System
- **OTP Timer:** 10-minute countdown with color transitions
- **Persistent Timers:** Calculate remaining time from server timestamps on page refresh
- **Resend Cooldown:** 60-second button cooldown with live display
- **Rate Limit Timer:** 15-minute countdown on 429 error page with auto-redirect
- **Inline JavaScript:** No external file dependency for instant functionality

#### ✅ Timer Implementation
- **Student Registration:** Timer on OTP verification page
- **HR Registration:** Timer on HR OTP verification page
- **Password Reset:** Timer on password reset OTP page
- **Rate Limiting:** Timer on 429 "Too Many Attempts" error page
- **Accurate Calculation:** Uses server-provided timestamps, not client-side duration

### Session: December 24, 2025

#### ✅ Database Cleanup
- Reset PostgreSQL database on Render to clean slate
- Removed stale user data from previous deployments
- Initialized fresh with superuser creation from env vars

#### ✅ Admin Interface Fixes
- **Fixed 500 Error:** Removed `approval_status_info` method from readonly_fields
- **Fixed queryset N+1:** Added `select_related('user')` for efficiency
- **Fixed sorting:** Changed from `-approval_requested_at` to `-created_at` (avoid NULL sorting)
- **Fixed HTML rendering:** Changed `format_html()` to `mark_safe()` for strings without placeholders

#### ✅ Account Type Separation
- **Fixed superuser profile creation:** Modified signal to exclude staff/superuser
- **Auto-cleanup:** Signal now removes UserProfile if user becomes staff/superuser
- **Cleanup script:** Added `cleanup_admin_profiles.py` for manual cleanup of stale profiles
- **HR registration fix:** Mark user as `is_staff=True` before save, delete UserProfile afterward

#### ✅ Login Security
- **Created StudentLoginView:** Custom view blocks HR/Admin from student login
- **Form validation:** Uses `form_valid()` to check user type before session creation
- **Error messaging:** Clear direction to use HR/Admin login pages
- **Early blocking:** Prevents authentication before login redirect

#### ✅ HR Account Features
- **HR Profile Display:** Fixed queryset to show all registered HR accounts
- **Bulk Actions:** Added approve/reject actions for HR profiles
- **Debug Logging:** Added total HR profile count to admin changelist
- **Approval Workflow:** Timestamps and admin tracking

#### ✅ Data Visibility
- **HR Dashboard:** Excludes admin/staff from student list
- **Student Detail:** Validates user type before showing profile
- **Admin Filters:** Properly exclude staff accounts from student listings
- **List Display:** Badge-based status indicators for approval

---

## Deployment

### Environment Variables (Required)
```bash
# Database
DATABASE_URL=postgresql://user:password@host:port/dbname

# Django Security
SECRET_KEY=your-secret-key
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Superuser (Auto-creation)
DJANGO_SUPERUSER_USERNAME=tapdiyaom
DJANGO_SUPERUSER_EMAIL=your-email@gmail.com
DJANGO_SUPERUSER_PASSWORD=secure-password

# Email (Resend)
RESEND_API_KEY=your-resend-api-key
EMAIL_BACKEND=core.email_backends.ResendBackend
DEFAULT_FROM_EMAIL=noreply@yourdomain.com

# AWS S3 (Optional)
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_STORAGE_BUCKET_NAME=your-bucket
```

### Deployment Steps
1. Push code to GitHub
2. Render detects new commit
3. Runs `collectstatic` (static files)
4. Runs migrations (database schema)
5. Initializes superuser (if not exists)
6. Starts Gunicorn server
7. Application ready on deployed URL

### Key Settings

**Security Headers**
```python
SECURE_SSL_REDIRECT = not DEBUG
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG
SECURE_HSTS_SECONDS = 31536000 if not DEBUG else 0
X_FRAME_OPTIONS = 'DENY'
SECURE_CONTENT_SECURITY_POLICY = {...}
```

**Email Configuration**
```python
EMAIL_BACKEND = 'core.email_backends.ResendBackend'
DEFAULT_FROM_EMAIL = 'noreply@yourdomain.com'
RESEND_API_KEY = os.environ.get('RESEND_API_KEY')
```

**Rate Limiting**
```python
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}
ENABLE_RATE_LIMITING = True
RATE_LIMIT_LOGIN_ATTEMPTS = 5
RATE_LIMIT_LOGIN_WINDOW = 900  # seconds
# ... other rate limit settings
```

**Static Files**
```python
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
```

### Database Management
- **PostgreSQL:** Hosted on Render Cloud
- **Migrations:** Automatic on deployment via Procfile
- **Connection Pooling:** Configured in DATABASE_URL
- **Backups:** Render automatic daily backups
- **Monitoring:** Render dashboard with metrics and alerts

---

## Project Structure

```
RecruitHub/
├── auth_project/              # Django project settings
│   ├── settings.py            # Configuration
│   ├── urls.py                # Main URL routing
│   ├── wsgi.py                # Gunicorn entry point
│   └── asgi.py                # ASGI config
│
├── core/                       # Main application
│   ├── models.py              # User, UserProfile, HRProfile, EmailOTP
│   ├── views.py               # All view logic
│   ├── admin.py               # Admin configuration
│   ├── forms.py               # Registration/login forms
│   ├── urls.py                # App URL routing
│   ├── middleware.py          # Custom middleware
│   ├── email_backends.py      # Email configuration
│   ├── templates/             # HTML templates
│   ├── static/                # CSS, JS, images
│   └── migrations/            # Database migrations
│
├── manage.py                   # Django CLI
├── requirements.txt            # Python dependencies
├── Procfile                    # Render deployment config
├── runtime.txt                 # Python version
└── README.md                   # This file
```

---

## Key Technologies

- **Backend:** Django 6.0 (Python 3.13)
- **Database:** PostgreSQL (Render Cloud)
- **Frontend:** Bootstrap 5, HTML5, CSS3
- **Authentication:** Django built-in + OTP
- **Email:** Resend (transactional email)
- **Storage:** AWS S3 (media files)
- **Hosting:** Render.com
- **Version Control:** Git & GitHub

---

## Testing Accounts

### Admin Account
- **URL:** `/<ADMIN_URL_PATH>/` (set `ADMIN_URL_PATH` environment variable)
- **Username:** Set via `DJANGO_SUPERUSER_USERNAME`
- **Email:** Set via `DJANGO_SUPERUSER_EMAIL`
- **Password:** Set via `DJANGO_SUPERUSER_PASSWORD`
- **Auto-created:** On first deployment if not exists

### Test Student Accounts
- Can create via `/register/` page
- Email verification required (OTP)
- Complete profile with academic details
- Upload resume and documents

### Test HR Accounts
- Register via `/hr/register/`
- Requires email verification
- Needs admin approval to access dashboard
- Can view and filter students once approved

---

## Common Issues & Solutions

### Issue: HR account appears in User Profiles
**Solution:** Signal now auto-removes UserProfile when user becomes staff

### Issue: Admin shows as student in HR dashboard
**Solution:** HR dashboard filters exclude `is_staff=True` and `is_superuser=True`

### Issue: HR can login as student
**Solution:** StudentLoginView blocks login with error message

### Issue: 500 error on HR Profiles page
**Solution:** Changed `format_html()` to `mark_safe()` for HTML strings

### Issue: HR registration doesn't create HR profile
**Solution:** Fixed to set `is_staff=True` before save, then delete UserProfile

---

## Getting Started (Local Development)

### Prerequisites
- Python 3.13+
- PostgreSQL (or SQLite for development)
- Git
- pip (Python package manager)

### Installation

1. **Clone Repository**
```bash
git clone https://github.com/Om-mac/RecruitHub.git
cd RecruitHub
```

2. **Create Virtual Environment**
```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. **Install Dependencies**
```bash
pip install -r requirements.txt
```

4. **Environment Setup**
```bash
# Create .env file
cp .env.example .env

# Edit .env with your configuration
# Database, email, API keys, etc.
```

5. **Database Setup**
```bash
python manage.py migrate
python manage.py createsuperuser  # Create admin account
```

6. **Collect Static Files**
```bash
python manage.py collectstatic --noinput
```

7. **Run Development Server**
```bash
python manage.py runserver
```

Access at: `http://localhost:8000`
Admin at: `http://localhost:8000/<ADMIN_URL_PATH>/`

### Default Accounts

**Admin Account:** Created via `createsuperuser` command

**Test Student Account:** Create via registration page

**Test HR Account:** Register and approve via admin panel

---

## Future Enhancements

- [ ] Interview scheduling system with calendar integration
- [ ] Job posting and online application management
- [ ] Offer letter generation and e-signature
- [ ] Email notifications and reminders to HR
- [ ] Analytics dashboard with recruitment metrics
- [ ] Two-factor authentication (2FA) with TOTP
- [ ] Role-based permissions (custom roles)
- [ ] REST API for mobile app integration
- [ ] Bulk student upload (CSV/Excel import)
- [ ] Advanced search with full-text search
- [ ] Student feedback and evaluation system
- [ ] Company profile pages for students
- [ ] Email campaign system for HR
- [ ] Automated email workflows
- [ ] Document storage and versioning
- [ ] Activity logging and audit trail

---

## API Documentation

### Available Endpoints

**Authentication**
- `POST /accounts/login/` - Student login
- `POST /accounts/logout/` - Logout
- `POST /accounts/register/` - Student registration
- `POST /password-reset/` - Password reset request
- `POST /password-reset/verify/` - Verify password reset OTP

**Student Features**
- `GET /dashboard/` - Student dashboard
- `GET /profile/` - View own profile
- `PUT /profile/` - Update profile
- `POST /upload-document/` - Upload resume

**HR Features**
- `GET /hr/login/` - HR login page
- `GET /hr/register/` - HR registration
- `GET /hr/dashboard/` - HR dashboard (approved only)
- `GET /hr/students/` - List students (with filters)
- `GET /hr/student/<id>/` - View student details

**Admin Features**
- Custom admin dashboard (URL configured in settings)
- User management and profile editing
- HR account approval workflow
- System statistics and monitoring

---

---

## Troubleshooting & FAQ

### Common Issues

**Q: I can't login as HR**
- A: Make sure your HR account is approved by admin. Check the HR Profiles section in admin panel for approval status.

**Q: OTP expires too quickly**
- A: OTP is valid for 10 minutes. Check server time synchronization.

**Q: Rate limited from too many login attempts**
- A: Wait 15 minutes for the rate limit to reset. See `/static/429.html` for timer.

**Q: Email not receiving OTP**
- A: Check spam/junk folder. Verify email configuration in environment variables.

**Q: Profile photo not uploading**
- A: Ensure AWS S3 credentials are configured. Check bucket permissions.

**Q: Admin account not created on deployment**
- A: Verify `DJANGO_SUPERUSER_*` environment variables are set correctly.

**Q: Static files returning 404**
- A: Run `python manage.py collectstatic --noinput` and verify `STATIC_ROOT` path.

### Debug Mode

**Enable Debug Logging**
```python
# settings.py
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'DEBUG',
    },
}
```

### Database Reset (Development Only)

```bash
# WARNING: This deletes all data!
python manage.py flush
python manage.py migrate
python manage.py createsuperuser
```

---

## Support & Contact

**Project Repository:** [RecruitHub on GitHub](https://github.com/Om-mac/RecruitHub)

**Developer:** Om Tapdiya

**Email:** tapdiya75@gmail.com (for queries, not credentials)

**Issues & Bugs:** Create an issue on GitHub repository

**Last Updated:** December 25, 2025  
**Version:** 2.1.0 (Production Ready)

---

## Performance & Optimization

### Database Optimization
- **Indexing:** Indexed on frequently queried fields (email, username)
- **Query Optimization:** `select_related()` and `prefetch_related()` used
- **Pagination:** Admin list views paginated (100 per page)
- **Caching:** Session caching for rate limiting

### Frontend Optimization
- **Static Files:** WhiteNoise compression and caching
- **CSS/JS:** Bootstrap CDN for faster loading
- **Images:** Lazy loading for profile photos
- **Responsive Design:** Mobile-friendly UI

### Server Performance
- **Gunicorn Workers:** 1 worker (configurable)
- **Connection Pooling:** Database connection pooling
- **Middleware:** Minimal middleware stack
- **Logging:** Efficient logging without file I/O

---

## Development Best Practices

### Code Style
- Python: PEP 8 compliance
- Django: Follow Django conventions
- HTML/CSS: Bootstrap 5 standards
- JavaScript: ES6+ standards

### Testing
```bash
# Run tests
python manage.py test

# Test with coverage
coverage run --source='.' manage.py test
coverage report
```

### Deployment Checklist
- [ ] All migrations applied
- [ ] Static files collected
- [ ] Environment variables configured
- [ ] Database backed up
- [ ] Email service configured
- [ ] AWS S3 credentials set
- [ ] SSL certificate active
- [ ] Debug mode disabled
- [ ] Allowed hosts configured
- [ ] Secret key secure

---

## License

This project is proprietary software. Unauthorized copying or distribution is prohibited.

---

## Legal Documents

- **[Privacy Policy](./PRIVACY_POLICY.md)** - How we collect, use, and protect your data
- **[Security Policy](./SECURITY.md)** - Security practices and vulnerability reporting
- **[Terms of Service](./TERMS_OF_SERVICE.md)** - Platform usage terms and conditions

---**Made with ❤️ for Campus Recruitment**
