# 🎓 RecruitHub - Campus Recruitment Portal

A comprehensive Django-based HR recruitment management system designed for colleges and placement cells to streamline student hiring processes.

**Status:** ✅ Fully Functional | **Version:** 1.0.0 | **Python:** 3.14.0 | **Django:** 6.0 | **Storage:** AWS S3

## Features

### Student Features
- **User Authentication:** Secure login, logout, and password management with OTP verification
- **Profile Management:** Complete student profiles with education and professional details
  - Personal information (DOB, gender, contact)
  - Academic details (branch, CGPA, backlogs, admission year)
  - Professional info (skills, experience, bio)
  - Social media links (GitHub, LinkedIn, HackerRank, etc.)
  - **Profile Photo Upload** (stored in AWS S3)
- **Document Management:** Upload and manage resumes (AWS S3 storage)
- **Notes System:** Create and organize personal notes
- **Dashboard:** View profile completeness and uploaded documents

### HR Features
- **HR Authentication:** Dedicated HR login portal with OTP verification
- **Student Directory:** View all registered students with complete profiles
- **Advanced Filtering:**
  - Filter by branch/specialization
  - Filter by CGPA range (min/max)
  - Filter by backlogs (current)
- **Sorting Options:**
  - Sort by CGPA (high to low, low to high)
  - Sort by backlogs
  - Sort by name (A-Z, Z-A)
  - Sort by branch
- **Student Details View:** 
  - Detailed profile information with profile photos
  - Social media links and platform usernames
  - Direct access to GitHub, LinkedIn, HackerRank profiles
  - Download resumes
  - Skills, certifications, and experience details
- **Dashboard Statistics:** 
  - Total students count
  - Average CGPA
  - Zero backlog count
  - Branch distribution

### Admin Features
- **Test User Creation:** One-click admin action to create 10 test users (22IF001-22IF010) with complete profiles
- **Advanced Admin Panel:** Custom styling with dark mode support
- **User Management:** Create, edit, delete users and their profiles
- **HR Approval Workflow:** Secure admin approval system for new HR account registrations
  - Email notifications sent to admin (omtapdiya75@gmail.com) on HR registration
  - One-click approval and rejection links
  - Pending/approved status tracking
  - Rejection reason tracking
  - HR users cannot login until approved

## Setup

### Prerequisites
- Python 3.8+
- Django 6.0
- PostgreSQL (production) or SQLite (development)
- AWS S3 Bucket (optional, for cloud file storage)

### Installation

1. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run Migrations:**
   ```bash
   python manage.py migrate
   ```

3. **Create Superuser:**
   ```bash
   python manage.py createsuperuser
   ```

4. **Create Test HR Account:**
   ```bash
   python manage.py create_hr_user
   ```

5. **Run Server:**
   ```bash
   python manage.py runserver
   ```

### AWS S3 Configuration (Optional)

To enable cloud storage for resumes, profile photos, and documents:

1. **Create AWS S3 Bucket:**
   - Go to AWS Console → S3
   - Create a new bucket (e.g., `recruithub-amzn-bucket`)
   - Disable "Block all public access"
   - Add bucket policy for public read access

2. **Set Environment Variables on Render/Production:**
   ```
   USE_S3=true
   AWS_ACCESS_KEY_ID=your_access_key
   AWS_SECRET_ACCESS_KEY=your_secret_key
   AWS_STORAGE_BUCKET_NAME=your_bucket_name
   AWS_S3_REGION_NAME=eu-north-1  (your region)
   ```

3. **Local Development (Optional):**
   ```bash
   # Create .env file
   USE_S3=false  # Use local /media/ folder
   ```

Files will be stored in:
- **Without S3:** `/media/` folder on server
- **With S3:** `s3://your-bucket/media/` in AWS cloud

## Usage

### Student Portal
1. **Register:** Visit `http://127.0.0.1:8000/register/`
2. **Login:** Visit `http://127.0.0.1:8000/login/`
3. **Update Profile:** Go to Profile section and fill in your details
   - Add your branch, CGPA, backlogs
   - Add GitHub, LinkedIn, and other social media usernames
   - Upload your resume
4. **Dashboard:** View your profile and uploaded documents

### HR Portal
1. **Login:** Visit `http://127.0.0.1:8000/hr/login/`
   - **Test Credentials:**
     - Username: `hr_admin`
     - Password: `hr123456`

2. **Dashboard Features:**
   - View all students in the system
   - Apply filters (branch, CGPA range, backlogs)
   - Sort results by various criteria
   - See statistics (total students, avg CGPA, etc.)

3. **Student Details:**
   - Click "View" on any student to see full profile
   - Access direct links to GitHub, LinkedIn, HackerRank
   - Download resumes
   - View skills, certifications, and experience

### Test Student Accounts
Pre-created dummy students in format: `22IF[###]`
- **Username:** `22IF001` → `22IF010`
- **Password:** `22IF001` + `22IF001` = `22IF00122IF001` (username repeated)
- **Email:** `22IF001@college.edu` → `22IF010@college.edu`
- **Total Test Users:** 10 (created via admin action or management command)

#### Creating Test Users via Admin Panel:
1. Go to `https://yourdomain.com/admintapdiyaom/core/userprofile/`
2. At bottom, select Action: **"⚡ Create 10 Test Users"**
3. Click **"Go"** - Users created instantly with complete profiles

#### Creating Test Users via Command Line:
```bash
python manage.py create_50_users  # Creates 10 users (can be modified in code)
```

Each test user has:
- ✅ Complete profile with realistic fake data
- ✅ CGPA between 6.5 - 9.2
- ✅ Random branch assignment
- ✅ Skills and experience details
- ✅ Resume placeholder data

### HR Approval Workflow

RecruitHub includes a secure admin approval workflow for new HR account registrations to prevent unauthorized access.

#### Complete Workflow Process:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         HR REGISTRATION WORKFLOW                            │
└─────────────────────────────────────────────────────────────────────────────┘

STEP 1: HR Registration
├─ HR visits /hr/register/
├─ Fills company name, designation, department
├─ Provides email address
└─ Receives OTP verification email

STEP 2: Email Verification
├─ HR enters OTP from email
├─ Email is verified ✓
└─ Proceeds to Step 3

STEP 3: Create Account
├─ HR sets username & password
├─ Account created with is_approved = FALSE
├─ Approval token generated (unique token for email links)
├─ Success message: "Awaiting admin approval"
├─ Redirects to HR Login page
└─ ✉️ APPROVAL EMAIL SENT TO: omtapdiya75@gmail.com
    ├─ HR details (username, name, company, designation)
    ├─ APPROVE LINK: /admin/approve-hr/{token}/
    └─ REJECT LINK: /admin/reject-hr/{token}/

STEP 4A: Admin Approves (Via Email Link or Admin Panel)
├─ Admin clicks APPROVE link in email
│  └─ Account is_approved = TRUE
│     approved_by = Admin user
│     approved_at = Current timestamp
│
├─ OR: Admin goes to Admin Panel → HR Profiles
│      Clicks "✓ Approve" button
│      Account is approved with same fields
│
└─ ✉️ EMAIL SENT TO HR: "Your HR account has been approved!"
    └─ HR can now login with username & password

STEP 4B: Admin Rejects (Via Admin Panel)
├─ Admin clicks "✗ Reject" button in Admin Panel
├─ Admin provides rejection reason
├─ HR account & user are deleted
└─ ✉️ EMAIL SENT TO HR: "Your application was rejected"
    └─ Rejection reason included in email

STEP 5: HR Login Attempt (BEFORE Approval)
├─ HR visits /hr/login/
├─ Enters username & password
├─ Credentials are valid BUT is_approved = FALSE
├─ ❌ Login denied
└─ Message shown: "Your HR account is pending admin approval. Please wait for verification."
    └─ HR must wait for admin approval

STEP 5: HR Login Attempt (AFTER Approval)
├─ HR visits /hr/login/
├─ Enters username & password
├─ Credentials valid AND is_approved = TRUE
├─ ✓ Login successful
└─ Redirects to HR Dashboard
    └─ HR can now view students, filter, sort, etc.
```

#### How It Works in Code:

**Registration Summary:**
1. User visits `/hr/register_step1/` → Enters email
2. User visits `/hr/register_step2/` → Verifies OTP
3. User visits `/hr/register_step3/` → Creates account
   - HRProfile created with `is_approved=False`
   - `approval_token` generated
   - `send_hr_approval_email()` called
   - Message: "Awaiting admin approval"
   - Redirects to `/hr/login/`

**Approval Process:**
- Admin receives email with approval/rejection links
- Admin clicks link or uses Admin Panel
- `approve_hr_account(token)` or `reject_hr_account(token)` view processes
- Confirmation email sent to HR

**Login Check:**
```python
# In hr_login view:
if user.hr_profile.is_approved == False:
    show_error("Your HR account is pending admin approval")
    return redirect('hr_login')
else:
    login(request, user)
    return redirect('hr_dashboard')
```

#### Configuration:

**Environment Variables:**
```
HR_APPROVAL_EMAIL=omtapdiya75@gmail.com  # Admin approval email
SITE_URL=https://yourdomain.com          # For approval links in emails
```

**Local Testing:**
```bash
# Development uses Django's email backend (console output)
# Emails are printed to terminal instead of sent
python manage.py runserver

# Check terminal for email content and approval token
```

#### API Endpoints:

```
GET  /admin/approve-hr/<token>/   # Approve HR account via token
POST /admin/reject-hr/<token>/    # Reject and delete HR account
```

#### Step-by-Step Testing Guide:

**Scenario: New HR User Registers**

1. **Start Django Server:**
   ```bash
   python manage.py runserver
   ```
   - Terminal will display emails in console (no actual sending in development)

2. **HR Registration - Step 1 (Email):**
   - Visit: `http://localhost:8000/hr/register/`
   - Click "Register" → Step 1
   - Enter email: `john@company.com`
   - Click "Send OTP"
   - **✓ Check Terminal:** Email with OTP is displayed
     ```
     Subject: Your HR Account Verification OTP - RecruitHub
     OTP: [6-digit code]
     ```

3. **HR Registration - Step 2 (OTP Verification):**
   - Copy OTP from terminal
   - Enter OTP in form
   - Click "Verify"
   - **✓ Success:** Message "OTP verified successfully"

4. **HR Registration - Step 3 (Account Creation):**
   - Fill details:
     - Username: `john_hr`
     - Password: `SecurePass123`
     - Company: `Tech Solutions Inc`
     - Designation: `HR Manager`
     - Department: `Human Resources`
   - Click "Register"
   - **✓ Success Message:** "HR Registration successful! Awaiting admin approval"
   - **✓ Check Terminal:** Admin approval email displayed
     ```
     Subject: New HR Registration - john_hr from Tech Solutions Inc
     To: omtapdiya75@gmail.com
     
     New HR Account Approval Request
     Username: john_hr
     Name: John Doe
     Email: john@company.com
     Company: Tech Solutions Inc
     Designation: HR Manager
     Department: Human Resources
     
     APPROVE: http://localhost:8000/admin/approve-hr/[unique-token]/
     REJECT: http://localhost:8000/admin/reject-hr/[unique-token]/
     ```

5. **HR Tries to Login (NOT Approved Yet):**
   - Visit: `http://localhost:8000/hr/login/`
   - Enter:
     - Username: `john_hr`
     - Password: `SecurePass123`
   - Click "Login"
   - **✗ Error Message:** "Your HR account is pending admin approval. Please wait for verification."
   - **✓ Status:** HR cannot access dashboard until approved

6. **Admin Approves (Option A: Via Email Link):**
   - Copy the APPROVE URL from terminal
   - Visit the URL in browser
   - **✓ Success Message:** "HR account john_hr has been approved successfully"
   - **✓ Check Terminal:** Confirmation email sent to HR
     ```
     Subject: Your HR Account Has Been Approved - RecruitHub
     To: john@company.com
     
     Hello John,
     Great news! Your HR account has been approved and is now active.
     You can now log in...
     ```

7. **Admin Approves (Option B: Via Admin Panel):**
   - Visit: `http://localhost:8000/admin/`
   - Login as superuser
   - Go to: **Core → HR Profiles**
   - Find pending account (marked with "⏳ Pending" badge)
   - Click "✓ Approve" button next to account
   - **✓ Success:** Account is approved

8. **Admin Rejects (Via Admin Panel):**
   - Go to: **Core → HR Profiles**
   - Find pending account
   - Click "✗ Reject" button
   - Fill rejection reason: "Company not registered with us"
   - Click "Reject & Delete"
   - **✓ User deleted permanently**
   - **✓ Check Terminal:** Rejection email sent to HR
     ```
     Subject: Your HR Account Registration - RecruitHub
     To: john@company.com
     
     Thank you for applying for an HR account with RecruitHub.
     Unfortunately, your HR account registration has been rejected.
     
     Reason: Company not registered with us
     ```

9. **HR Tries to Login (AFTER Approval):**
   - Visit: `http://localhost:8000/hr/login/`
   - Enter:
     - Username: `john_hr`
     - Password: `SecurePass123`
   - Click "Login"
   - **✓ Success:** Login successful!
   - **✓ Redirects:** HR Dashboard
   - **✓ Message:** "Welcome HR John!"

**Summary of States:**

| Status | Can Login? | Message |
|--------|-----------|---------|
| ⏳ Pending Approval | ❌ No | "Your HR account is pending admin approval" |
| ✓ Approved | ✅ Yes | Login successful, see dashboard |
| ✗ Rejected | ❌ No | User deleted, no account exists |

## Database Models

### UserProfile
- Personal details (name, phone, DOB, gender)
- Address information
- Profile photo and resume
- Education details (**branch**, degree, CGPA, backlogs)
- Professional info (skills, experience, bio)
- Social media usernames

### HRProfile
- Company name
- Designation
- Department
- **Approval Fields:**
  - `is_approved` - Approval status (True/False)
  - `approval_requested_at` - Timestamp of registration
  - `approved_by` - Admin who approved (FK to User)
  - `approved_at` - Approval timestamp
  - `approval_token` - Unique token for email links
  - `rejection_reason` - Reason if rejected
- Created/Updated timestamps

## Admin Panel
- Access at `http://127.0.0.1:8000/admin/`
- Create, edit, and manage users
- Manage student profiles
- View HR accounts
- Manage documents and notes

## Project Structure
```
Authentication/
├── auth_project/        # Django project settings
├── core/               # Main app
│   ├── models.py       # Database models
│   ├── views.py        # View logic
│   ├── urls.py         # URL routing
│   ├── forms.py        # Form definitions
│   ├── admin.py        # Admin configuration
│   └── templates/      # HTML templates
│       └── core/
│           ├── base.html
│           ├── hr_login.html
│           ├── hr_register.html
│           ├── hr_dashboard.html
│           ├── student_detail.html
│           └── ... (other templates)
├── media/              # Uploaded files
├── db.sqlite3          # Database
├── manage.py           # Django management
└── create_test_hr.sh   # Test HR account creation

```

## API Endpoints

### Authentication
- `POST /register/` - Student registration
- `GET /login/` - Student login page
- `POST /login/` - Student login
- `GET /hr/login/` - HR login page
- `POST /hr/login/` - HR login
- `GET /hr/register/` - HR registration
- `POST /hr/register/` - HR registration

### Student Routes
- `GET /dashboard/` - Student dashboard
- `GET /profile/` - Student profile page
- `POST /profile/` - Update student profile
- `GET /upload/` - Document upload page
- `POST /upload/` - Upload document
- `GET /add_note/` - Add note page
- `POST /add_note/` - Create note

### HR Routes
- `GET /hr/dashboard/` - HR dashboard with filtering/sorting
- `GET /hr/student/<user_id>/` - View student details
- `GET /hr/logout/` - HR logout

## Features Explained

### HR Dashboard Filtering
1. **Branch Filter:** Filter students by branch (CSE, ECE, Mechanical, etc.)
2. **CGPA Range:** Filter students with CGPA between min and max values
3. **Backlogs:** Show only students with specified maximum backlogs
4. **Sorting:** Sort results by CGPA, backlogs, name, or branch

### Student Profile Links
HR can access:
- GitHub profile: `https://www.github.com/[username]`
- LinkedIn profile: `https://www.linkedin.com/in/[username]`
- HackerRank profile: `https://www.hackerrank.com/[username]`
- Other platforms: Custom platform names and usernames

### Statistics
- **Total Students:** Count of all registered students
- **Average CGPA:** Calculated from all student CGPAs
- **Zero Backlogs:** Count of students with 0 current backlogs
- **Branches:** Total number of unique branches represented

## Security
- Password hashing with Django's built-in system
- CSRF protection on all forms
- Login required decorators on protected views
- User model validation
- File upload restrictions (images and documents only)

## Future Enhancements
- Email verification for account creation
- Batch student import from CSV
- Interview scheduling system
- Email notifications
- Advanced analytics and reports
- Multi-company HR management
- Student visibility controls
- Recruiter feedback system

---

## 🚀 Quick Start

### 1. Clone & Setup
```bash
git clone https://github.com/yourusername/RecruitHub.git
cd RecruitHub
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Initialize Database
```bash
python manage.py migrate
python manage.py createsuperuser
```

### 3. Create Test HR Account
```bash
python manage.py shell < create_test_hr.sh
```

### 4. Run Server
```bash
python manage.py runserver
```

Access the application at `http://127.0.0.1:8000`

---

## 📋 Test Credentials

### HR Account (for recruitment team)
```
URL: http://127.0.0.1:8000/hr/login/
Username: hr_admin
Password: hr123456
```

### Sample Student Accounts (for testing)
| Branch | Username | Password |
|--------|----------|----------|
| CSE | 22CS001 | 22CS00122CS001 |
| CSE | 22CS010 | 22CS01022CS010 |
| IT | 22IT005 | 22IT00522IT005 |
| ECE | 22EE015 | 22EE01522EE015 |
| Mechanical | 22ME025 | 22ME02522ME025 |

*Format: `22[BRANCH][###]` where BRANCH is 2-char code and ### is 001-200*

---

## 🎯 Features at a Glance

| Feature | Student | HR |
|---------|---------|-----|
| Profile Management | ✅ | ❌ |
| Document Upload | ✅ | ❌ |
| Notes System | ✅ | ❌ |
| View Dashboard | ✅ | ✅ |
| View All Students | ❌ | ✅ |
| Filter Students | ❌ | ✅ |
| Sort Students | ❌ | ✅ |
| View Student Details | ❌ | ✅ |
| Download Resume | ❌ | ✅ |
| Access Social Profiles | ❌ | ✅ |

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | Django 6.0, Python 3.14 |
| **Database** | PostgreSQL (prod), SQLite3 (dev) |
| **Frontend** | Bootstrap 5.3, Vanilla JS |
| **File Storage** | AWS S3 (cloud) / Local media/ (dev) |
| **Images** | Pillow 10.0+ |
| **OTP Verification** | Django Email Backend (Resend) |
| **Server** | Gunicorn + Render / Django Dev Server |
| **Styling** | Custom CSS + Bootstrap 5.3 |

---

## 📁 Project Structure

```
RecruitHub/
├── 📄 manage.py                    # Django management script
├── 📄 README.md                    # This file
├── 📄 requirements.txt             # Dependencies
│
├── 📁 auth_project/               # Django Project Config
│   ├── settings.py                # Django settings
│   ├── urls.py                    # URL routing
│   ├── wsgi.py                    # WSGI config
│   └── asgi.py                    # ASGI config
│
├── 📁 core/                       # Main Application
│   ├── models.py                  # Database models
│   ├── views.py                   # View functions
│   ├── urls.py                    # App URLs
│   ├── forms.py                   # Forms
│   ├── admin.py                   # Admin config
│   │
│   ├── 📁 templates/core/
│   │   ├── base.html              # Base template
│   │   ├── register.html          # Student registration
│   │   ├── login.html             # Student login
│   │   ├── dashboard.html         # Student dashboard
│   │   ├── profile.html           # Profile page
│   │   ├── hr_login.html          # HR login
│   │   ├── hr_register.html       # HR registration
│   │   ├── hr_dashboard.html      # HR recruitment dashboard
│   │   ├── student_detail.html    # Student profile (HR view)
│   │   ├── add_note.html          # Add note
│   │   ├── view_note.html         # View note
│   │   ├── edit_note.html         # Edit note
│   │   ├── delete_note.html       # Delete note
│   │   ├── upload_document.html   # Upload resume
│   │   └── ... (other templates)
│   │
│   └── 📁 migrations/
│       └── (Database migration files)
│
├── 📁 media/                      # Uploaded files
│   └── documents/                 # Student resumes
│
└── 📁 db.sqlite3                  # SQLite database
```

---

## 🔐 Security Considerations

- ✅ Password hashing with Django's default PBKDF2
- ✅ CSRF tokens on all forms
- ✅ SQL injection protection via ORM
- ✅ Login required decorators
- ✅ File upload validation
- ⚠️ **For Production:** Use environment variables, HTTPS, stronger SECRET_KEY

---

## 📊 Database Schema

### UserProfile
- User details (name, email, phone)
- Address information
- Academic info (branch, CGPA, backlogs)
- Professional info (skills, experience)
- Social media links
- Resume and profile photo

### HRProfile
- Company information
- Designation
- Department
- Created/Updated timestamps

### Document
- File title
- File path
- Upload timestamp
- Associated with user

### Note
- Title and content
- Created/Updated timestamps
- Associated with user

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---
📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

⸻

👨‍💻 Author

Om Tapdiya
B.Tech CSE (Data Science), VIT Pune
Created for college recruitment management and HR automation.

⸻

📞 Support

For issues, questions, or suggestions:
	•	Open an issue on GitHub
	•	Contact: omtapdiya75@gmail.com

⸻

🎓 About RecruitHub

RecruitHub is a modern recruitment management system designed specifically for educational institutions. It bridges the gap between students and recruiters by providing:
	•	📊 Real-time Analytics – Track student profiles and recruitment metrics
	•	🔍 Advanced Filtering – Find perfect candidates based on multiple criteria
	•	💼 Professional Profiles – Complete student information in one place
	•	🔗 Social Integration – Direct links to candidate’s GitHub, LinkedIn, and other profiles
	•	📱 Responsive Design – Works seamlessly on desktop and mobile devices

⸻

🔗 Developer Links
	•	GitHub: https://github.com/Om-mac
    
	•	LinkedIn: https://www.linkedin.com/in/omtapdiya

⸻

Star ⭐ this repository if you found it helpful!