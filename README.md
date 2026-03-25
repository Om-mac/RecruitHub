# 🎓 RecruitHub - Campus Recruitment Portal

A comprehensive Django-based HR recruitment management system designed for colleges and placement cells to streamline student hiring processes with proper account type separation and security.

**Status:** ✅ Production Ready | **Version:** 2.0.0 | **Python:** 3.13 | **Django:** 6.0 | **Database:** AWS DynamoDB | **Hosting:** AWS EC2

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
│ is_superuser=False │ is_staff=False │ Has Profile in DB     │
│    is_staff=False  │                │      ↓                │
│                    ├─→ STUDENT      │  recruithub-user-     │
│                    │   (Regular User)│  profiles (DynamoDB)  │
│                    │                │                       │
│    is_staff=True   │ Has Profile in  │      ↓                │
│                    ├─→ HR ACCOUNT   │  recruithub-hr-       │
│                    │ (Recruiters)    │  profiles (DynamoDB)  │
│                    │                │                       │
│  is_superuser=True ├─→ ADMIN        │  No Profile           │
│   is_staff=True    │ (Management)    │  (Full Access)        │
└─────────────────────────────────────────────────────────────┘
```

### AWS DynamoDB Tables

All data is stored in AWS DynamoDB (On-Demand capacity). Below are the tables used:

| Table Name | Partition Key | Description |
|---|---|---|
| `recruithub-users` | `user_id (S)` | Core user accounts (username, password hash, flags) |
| `recruithub-user-profiles` | `user_id (S)` | Student academic & professional data |
| `recruithub-hr-profiles` | `user_id (S)` | HR recruiter company info & approval status |
| `recruithub-email-otps` | `email (S)` | OTP records for email verification |
| `recruithub-documents` | `user_id (S)` | Uploaded resumes and documents metadata |
| `recruithub-notes` | `user_id (S)` | Admin notes |

All tables use:
- **Capacity Mode:** On-Demand (auto-scaling)
- **Table Class:** Standard
- **Deletion Protection:** Off
- **Replication:** Single region

**`recruithub-users`**
- Core fields: `user_id`, `username`, `email`, `password_hash`, `is_staff`, `is_superuser`, `is_active`, `last_login`, `date_joined`

**`recruithub-user-profiles`** (Students)
- Personal: name, email, DOB, phone, address
- Education: branch, CGPA, backlogs, admission year, degree
- Professional: skills, experience, resume, bio
- Social: GitHub, LinkedIn, HackerRank usernames
- Media: profile_photo (AWS S3), resume (AWS S3)

**`recruithub-hr-profiles`** (Recruiters)
- Company details: name, designation, department
- Admin notes and approval status
- Approval workflow: `requested_at`, `approved_by`, `approved_at`
- Approval token for email verification

**`recruithub-email-otps`**
- Stores OTP for email verification during registration
- Validates email ownership before account creation

---

## Account Types & Separation

### 1. **STUDENT ACCOUNTS** (Regular Users)
- **is_superuser:** False
- **is_staff:** False
- **Has Profile:** `recruithub-user-profiles` (contains academic & professional data)
- **Permissions:** Can view own profile, upload resume, manage documents
- **Login:** `/accounts/login/` (Student Login)

**Blocked from:**
- Accessing HR features
- Viewing other student data
- Admin panel

### 2. **HR ACCOUNTS** (Recruiters)
- **is_superuser:** False
- **is_staff:** True (marked as staff to prevent student profile creation)
- **Has Profile:** `recruithub-hr-profiles` (contains company & approval status)
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
  - Step 3: Account creation (marked as `is_staff=True`)
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
- Create, edit, delete users (stored in `recruithub-users`)
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
- Database (DynamoDB) management
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
   [OTP stored in recruithub-email-otps]
   ↓
4. Create Account (username + password)
   ↓
5. Write to recruithub-users + recruithub-user-profiles (DynamoDB)
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
   [OTP stored in recruithub-email-otps]
   ↓
4. Create Account (username + password)
   ↓
5. Set is_staff=True in recruithub-users
   ↓
6. Delete any user-profile record if auto-created
   ↓
7. Create item in recruithub-hr-profiles (is_approved=False)
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
Checks for Superuser in recruithub-users
↓
If Not Exists → Creates Superuser from Env Vars
↓
Ensures no user-profile record exists for admin
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
        # Write item to recruithub-user-profiles DynamoDB table
        dynamodb.put_item(TableName='recruithub-user-profiles', ...)
    
    # Auto-cleanup: Remove UserProfile if user becomes staff/superuser
    if not created and (instance.is_staff or instance.is_superuser):
        dynamodb.delete_item(TableName='recruithub-user-profiles', ...)
```

#### 2. **Student Login Blocking**
- Custom `StudentLoginView` prevents HR/Admin from student login
- Checks `is_staff` and `is_superuser` flags in `recruithub-users` before login
- Shows error: "HR and Staff accounts must use the HR login page"
- Blocks early (before session creation)

#### 3. **HR Login Verification**
- Checks for item in `recruithub-hr-profiles`
- Verifies `is_approved` attribute
- Shows "Pending Approval" if not approved
- Only approved HR can access dashboard

#### 4. **HR Dashboard Protection**
- Reads from `recruithub-hr-profiles` to check approval
- Excludes staff/superuser accounts from student list scan
- Prevents HR from accessing admin/student data
- Student detail view validates user type

### Data Filtering

#### Admin Interface
- **User Profiles:** Queries exclude items with `is_staff=True` and `is_superuser=True`
- **HR Profiles:** Shows all items from `recruithub-hr-profiles` (pending and approved)
- **Users:** Filters to show only non-staff accounts from `recruithub-users`

#### Views & Templates
- HR dashboard: Scans `recruithub-user-profiles`, filters out staff/superusers
- Student detail: Validates `not is_staff and not is_superuser` from `recruithub-users`
- Prevents unauthorized data access through direct URLs

### Email Verification
- OTP-based verification using `recruithub-email-otps` table
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
HR Login                     5 attempts         15 min
OTP Verification             5 attempts         10 min
OTP Request (Resend)         5 per hour         60 min
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
- List all regular users (students) from `recruithub-users`
- Filters: branch, degree, gender, CGPA
- Search: username, email, name
- Actions: Edit, delete

#### 2. **User Profiles (Students)**
- Displays profiles from `recruithub-user-profiles`
- Filtered to exclude staff/admin
- Readonly: user_id, created_at
- Editable: all profile fields
- Search by username, email, branch, skills

#### 3. **HR Profiles (Recruiters)**
- List all items from `recruithub-hr-profiles`
- Status badges: ✓ Approved / ⏳ Pending
- Bulk actions: Approve / Reject
- Filters: Approval status, department, dates
- Search: username, company, designation

#### 4. **Documents**
- List uploaded resumes/documents from `recruithub-documents`
- Filter by upload date
- View file type and size
- Download functionality

#### 5. **Email OTP**
- Track OTP verifications in `recruithub-email-otps`
- View attempt counts
- Manage OTP records

---

## Deployment

### Infrastructure
- **Compute:** AWS EC2 (application server running Gunicorn + Django)
- **Database:** AWS DynamoDB (6 tables, on-demand capacity)
- **Storage:** AWS S3 (media files: resumes, profile photos)
- **Email:** Resend (transactional email)

### Environment Variables (Required)
```bash
# Django Security
SECRET_KEY=your-secret-key
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Superuser (Auto-creation)
DJANGO_SUPERUSER_USERNAME=your-admin-username
DJANGO_SUPERUSER_EMAIL=your-email@example.com
DJANGO_SUPERUSER_PASSWORD=your-secure-password-min-16-chars

# AWS (DynamoDB + S3)
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_REGION_NAME=your-region          # e.g. ap-south-1
AWS_STORAGE_BUCKET_NAME=your-bucket  # S3 bucket for media

# Email (Resend)
RESEND_API_KEY=your-resend-api-key
EMAIL_BACKEND=core.email_backends.ResendBackend
DEFAULT_FROM_EMAIL=noreply@yourdomain.com
```

### Deployment Steps (EC2)
1. SSH into EC2 instance
2. Pull latest code from GitHub
3. Install/update dependencies: `pip install -r requirements.txt`
4. Run `collectstatic` (static files)
5. Run initialization script (creates superuser in DynamoDB if not exists)
6. Restart Gunicorn service
7. Application ready on EC2 public IP / domain

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
```

**Static Files**
```python
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
```

### DynamoDB Configuration
- **Tables:** 6 tables, all on-demand capacity
- **Region:** Configured via `AWS_REGION_NAME` environment variable
- **Access:** IAM role attached to EC2 instance (or access key pair)
- **Backups:** AWS point-in-time recovery (PITR) recommended
- **Monitoring:** AWS CloudWatch for DynamoDB metrics

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
│   ├── dynamodb.py            # DynamoDB client & helpers
│   ├── templates/             # HTML templates
│   ├── static/                # CSS, JS, images
│   └── migrations/            # Migrations (schema reference only)
│
├── manage.py                   # Django CLI
├── requirements.txt            # Python dependencies
├── Procfile                    # Server start config
├── runtime.txt                 # Python version
└── README.md                   # This file
```

---

## Key Technologies

- **Backend:** Django 6.0 (Python 3.13)
- **Database:** AWS DynamoDB (NoSQL, on-demand)
- **Frontend:** Bootstrap 5, HTML5, CSS3
- **Authentication:** Django built-in + OTP
- **Email:** Resend (transactional email)
- **Storage:** AWS S3 (media files)
- **Hosting:** AWS EC2
- **Version Control:** Git & GitHub

---

## Testing Accounts

### Admin Account
- **URL:** `/<ADMIN_URL_PATH>/` (set `ADMIN_URL_PATH` environment variable)
- **Username:** Set via `DJANGO_SUPERUSER_USERNAME`
- **Email:** Set via `DJANGO_SUPERUSER_EMAIL`
- **Password:** Set via `DJANGO_SUPERUSER_PASSWORD`
- **Auto-created:** On first deployment if not exists in `recruithub-users`

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
**Solution:** Signal auto-removes item from `recruithub-user-profiles` when user becomes staff

### Issue: Admin shows as student in HR dashboard
**Solution:** HR dashboard scan filters exclude `is_staff=True` and `is_superuser=True`

### Issue: HR can login as student
**Solution:** StudentLoginView checks `recruithub-users` flags and blocks login with error

### Issue: HR registration doesn't create HR profile
**Solution:** Fixed to set `is_staff=True` in `recruithub-users` first, then write to `recruithub-hr-profiles`

---

## Getting Started (Local Development)

### Prerequisites
- Python 3.13+
- AWS account with DynamoDB access (or DynamoDB Local for offline dev)
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

# Edit .env with your AWS credentials, email config, etc.
```

5. **Create DynamoDB Tables**
```bash
# Tables must exist in AWS DynamoDB before running the app
# Use the AWS Console or run the setup script:
python manage.py create_dynamo_tables
```

6. **Initialize Admin**
```bash
python manage.py init_superuser  # Creates admin in recruithub-users
```

7. **Collect Static Files**
```bash
python manage.py collectstatic --noinput
```

8. **Run Development Server**
```bash
python manage.py runserver
```

Access at: `http://localhost:8000`
Admin at: `http://localhost:8000/<ADMIN_URL_PATH>/`

> **Tip for local dev:** Use [DynamoDB Local](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/DynamoDBLocal.html) to avoid AWS charges during development. Set `AWS_ENDPOINT_URL=http://localhost:8001` in your `.env`.

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

#### ✅ Database Migration to DynamoDB
- Migrated from PostgreSQL (Render) to AWS DynamoDB
- Created 6 tables with on-demand capacity
- Updated all queries to use `boto3` DynamoDB client
- Removed Django ORM database dependencies for core data

#### ✅ Admin Interface Fixes
- Fixed queryset to use DynamoDB scan with filter expressions
- Added `select_related` equivalent using batch DynamoDB gets
- Fixed sorting to avoid NULL sort issues (use `created_at` fallback)
- Fixed HTML rendering in admin list display

#### ✅ Account Type Separation
- Fixed superuser profile creation: signal excludes staff/superuser
- Auto-cleanup: Signal deletes item from `recruithub-user-profiles` if user becomes staff/superuser
- HR registration: Write `is_staff=True` to `recruithub-users` before creating `recruithub-hr-profiles` item

#### ✅ Login Security
- **Created StudentLoginView:** Custom view blocks HR/Admin from student login
- **Form validation:** Checks DynamoDB `recruithub-users` flags before session creation
- **Error messaging:** Clear direction to use HR/Admin login pages

#### ✅ HR Account Features
- Fixed scan to show all items from `recruithub-hr-profiles`
- Bulk approve/reject actions update `is_approved` attribute in DynamoDB
- Approval workflow: Writes `approved_by` and `approved_at` timestamps

---

## Performance & Optimization

### DynamoDB Optimization
- **On-Demand Capacity:** Auto-scales with traffic, no provisioning needed
- **Partition Key Design:** `user_id` as partition key for O(1) lookups
- **Batch Operations:** Use `batch_get_item` for multi-user fetches
- **Scan Filtering:** Apply filter expressions server-side to reduce data transfer
- **Index Strategy:** Add GSIs (Global Secondary Indexes) as query patterns grow

### Frontend Optimization
- **Static Files:** WhiteNoise compression and caching
- **CSS/JS:** Bootstrap CDN for faster loading
- **Images:** Lazy loading for profile photos (served from S3)
- **Responsive Design:** Mobile-friendly UI

### EC2 Server Performance
- **Gunicorn Workers:** Configurable worker count
- **Nginx (recommended):** Use as reverse proxy in front of Gunicorn
- **Connection:** boto3 DynamoDB client reused across requests
- **Logging:** CloudWatch integration for application logs

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

## Troubleshooting & FAQ

**Q: I can't login as HR**
- A: Make sure your HR account is approved by admin. Check the `recruithub-hr-profiles` table in DynamoDB for `is_approved` status.

**Q: OTP expires too quickly**
- A: OTP is valid for 10 minutes. Check EC2 instance time synchronization (`timedatectl` on Linux).

**Q: Rate limited from too many login attempts**
- A: Wait 15 minutes for the rate limit to reset.

**Q: Email not receiving OTP**
- A: Check spam/junk folder. Verify `RESEND_API_KEY` environment variable on EC2.

**Q: Profile photo not uploading**
- A: Ensure `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, and `AWS_STORAGE_BUCKET_NAME` are set. Check S3 bucket permissions and CORS policy.

**Q: DynamoDB access denied errors**
- A: Verify IAM permissions for the EC2 instance role (or access key). Ensure `dynamodb:PutItem`, `dynamodb:GetItem`, `dynamodb:Scan`, `dynamodb:DeleteItem`, `dynamodb:UpdateItem` permissions are granted for all `recruithub-*` tables.

**Q: Admin account not created on deployment**
- A: Verify `DJANGO_SUPERUSER_*` environment variables are set correctly on EC2.

**Q: Static files returning 404**
- A: Run `python manage.py collectstatic --noinput` and verify `STATIC_ROOT` path. Ensure Nginx (if used) is configured to serve `/static/`.

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
- [ ] Advanced search with DynamoDB GSIs or OpenSearch
- [ ] Student feedback and evaluation system
- [ ] Company profile pages for students
- [ ] Email campaign system for HR
- [ ] Automated email workflows
- [ ] Document storage and versioning
- [ ] Activity logging and audit trail (DynamoDB Streams)
- [ ] DynamoDB Global Secondary Indexes for optimized filtering

---

## Deployment Checklist

- [ ] EC2 instance running and SSH accessible
- [ ] All environment variables configured
- [ ] DynamoDB tables created (all 6)
- [ ] IAM permissions set for DynamoDB + S3
- [ ] Static files collected
- [ ] Email service (Resend) configured
- [ ] AWS S3 bucket created and credentials set
- [ ] SSL certificate active (recommended: AWS ACM + Load Balancer or Let's Encrypt)
- [ ] Debug mode disabled
- [ ] Allowed hosts configured
- [ ] Secret key secure
- [ ] Gunicorn service running (systemd or supervisor)
- [ ] Nginx configured as reverse proxy (recommended)

---

## License

This project is proprietary software. Unauthorized copying or distribution is prohibited.

---

## Legal Documents

- **[Privacy Policy](./PRIVACY_POLICY.md)** - How we collect, use, and protect your data
- **[Security Policy](./SECURITY.md)** - Security practices and vulnerability reporting
- **[Terms of Service](./TERMS_OF_SERVICE.md)** - Platform usage terms and conditions

---

**Made with ❤️ for Campus Recruitment**
