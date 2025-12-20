# 🎓 RecruitHub - Campus Recruitment Portal

A comprehensive Django-based HR recruitment management system designed for colleges and placement cells to streamline student hiring processes.

**Status:** ✅ Fully Functional | **Version:** 1.0.0 | **Python:** 3.14.0 | **Django:** 6.0

## Features

### Student Features
- **User Authentication:** Secure login, logout, and password management
- **Profile Management:** Complete student profiles with education and professional details
  - Personal information (DOB, gender, contact)
  - Academic details (branch, CGPA, backlogs, admission year)
  - Professional info (skills, experience, bio)
  - Social media links (GitHub, LinkedIn, HackerRank, etc.)
- **Document Management:** Upload and manage resumes
- **Notes System:** Create and organize personal notes
- **Dashboard:** View profile completeness and uploaded documents

### HR Features
- **HR Authentication:** Dedicated HR login portal
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
  - Detailed profile information
  - Social media links and platform usernames
  - Direct access to GitHub, LinkedIn, HackerRank profiles
  - Download resumes
  - Skills, certifications, and experience details
- **Dashboard Statistics:** 
  - Total students count
  - Average CGPA
  - Zero backlog count
  - Branch distribution

## Setup

### Prerequisites
- Python 3.8+
- Django 6.0
- SQLite (default)

### Installation

1. **Install Dependencies:**
   ```bash
   pip install django pillow
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
   bash create_test_hr.sh
   ```
   
   Or manually in Django shell:
   ```bash
   python manage.py shell
   ```
   
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
   ```

5. **Run Server:**
   ```bash
   python manage.py runserver
   ```

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
Pre-created dummy students in format: `22[BRANCH][###]`
- **Branch Codes:** CS (Computer Science), IF (IT), EE (Electrical), CE (Civil), ME (Mechanical)
- **Examples:**
  - Username: `22CS001` | Password: `22CS00122CS001`
  - Username: `22IT020` | Password: `22IT02022IT020`
  - Username: `22EE010` | Password: `22EE01022EE010`
- **Total Students Created:** 200+ across all branches

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
| **Database** | SQLite3 |
| **Frontend** | Bootstrap 5.3, Vanilla JS |
| **Images** | Pillow 10.0+ |
| **Server** | Django Development Server |

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