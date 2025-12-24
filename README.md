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
- **Login:** `/admintapdiyaom/` (Django Admin)
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

#### Notes System
- Create personal notes
- Edit and delete notes
- Organize thoughts and reminders

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
Environment Variables:
- DJANGO_SUPERUSER_USERNAME=tapdiyaom
- DJANGO_SUPERUSER_EMAIL=tapdiya75@gmail.com
- DJANGO_SUPERUSER_PASSWORD=***

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

### Password Security
- Django's `set_password()` (PBKDF2-SHA256 hashing)
- Secure password reset flow with OTP
- Change password requires old password verification
- Session-based authentication

---

## Admin Interface

### Custom Admin Site
- **URL:** `/admintapdiyaom/` (security through obscurity)
- **Styling:** Custom CSS with brand colors
- **Header:** "🎓 RecruitHub Admin Dashboard"
- **Features:** Dark mode support, responsive design

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

---

## Recent Fixes & Improvements

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

# Email (Brevo SMTP)
BREVO_API_KEY=your-brevo-api-key
BREVO_SMTP_KEY=your-brevo-smtp-key
EMAIL_BACKEND=path.to.email.backend
EMAIL_HOST=smtp-relay.brevo.com
EMAIL_PORT=587

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

### Database Management
- **PostgreSQL:** Hosted on Render
- **Migrations:** Automatic on deployment
- **Backups:** Render automatic daily backups
- **Monitoring:** Render dashboard with metrics

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
- **Email:** Brevo SMTP (free tier)
- **Storage:** AWS S3 (media files)
- **Hosting:** Render.com
- **Version Control:** Git & GitHub

---

## Testing Accounts

### Admin Account
- **URL:** `/admintapdiyaom/`
- **Username:** tapdiyaom
- **Email:** tapdiya75@gmail.com
- **Password:** Check environment variables

### Test Student Accounts
- Can create via admin or manually register
- Format: username/password defined during registration
- Complete profiles with test data

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

## Future Enhancements

- [ ] Email notifications to HR on student registration
- [ ] Interview scheduling system
- [ ] Job posting and application management
- [ ] Offer letter generation
- [ ] Analytics dashboard with charts
- [ ] Two-factor authentication (2FA)
- [ ] Role-based permissions system
- [ ] API for mobile app
- [ ] Bulk student upload (CSV)
- [ ] Advanced search and filters

---

## Support & Contact

**Developer:** Om Tapdiya
**Email:** tapdiya75@gmail.com
**GitHub:** [RecruitHub Repository](https://github.com/Om-mac/RecruitHub)

**Last Updated:** December 24, 2025
**Version:** 2.0.0 (Production Ready)

---

## License

This project is proprietary software. Unauthorized copying or distribution is prohibited.

---

**Made with ❤️ for Campus Recruitment**
