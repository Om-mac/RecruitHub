# HR Approval Workflow - Complete Implementation Guide

## Overview
RecruitHub now includes a secure admin approval workflow for new HR account registrations. This prevents unauthorized HR access and ensures only approved HR personnel can use the system.

---

## Complete Workflow Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         HR REGISTRATION & APPROVAL WORKFLOW                 │
└─────────────────────────────────────────────────────────────────────────────┘

STEP 1: HR Registration
├─ HR visits /hr/register/
├─ Fills company name, designation, department
├─ Provides email address
└─ Receives OTP verification email

STEP 2: Email Verification (OTP)
├─ HR enters 6-digit OTP from email
├─ Email is verified ✓
└─ Proceeds to Step 3

STEP 3: Create Account
├─ HR sets username & password
├─ Account is created with is_approved = FALSE
├─ Unique approval token is generated
├─ Success message: "Awaiting admin approval"
├─ Redirects to HR Login page
│
└─ ✉️ APPROVAL EMAIL SENT TO: omtapdiya75@gmail.com
    ├─ HR Details:
    │  ├─ Username
    │  ├─ Name (First + Last)
    │  ├─ Email address
    │  ├─ Company name
    │  ├─ Designation
    │  └─ Department
    │
    └─ Action Links:
       ├─ APPROVE LINK: /admin/approve-hr/{unique-token}/
       └─ REJECT LINK: /admin/reject-hr/{unique-token}/

┌─ APPROVAL PATH ────────────────────────────────────────────────────────────┐
│                                                                             │
│ OPTION A: Admin Approves via Email Link                                   │
├─ Admin clicks APPROVE link in email                                        │
├─ Account: is_approved = TRUE                                              │
├─          approved_by = Admin user                                         │
├─          approved_at = Current timestamp                                  │
│                                                                             │
│ OPTION B: Admin Approves via Admin Panel                                  │
├─ Go to: Admin Panel → Core → HR Profiles                                  │
├─ Find pending HR account (marked "⏳ Pending" in Status column)            │
├─ Click "✓ Approve" button                                                 │
├─ Same approval fields updated                                              │
│                                                                             │
│ Either option → ✉️ EMAIL SENT TO HR: "Account Approved!"                 │
│                 ├─ Subject: Your HR Account Has Been Approved             │
│                 ├─ Message: You can now login with your credentials       │
│                 └─ Login URL: /hr/login/                                  │
└────────────────────────────────────────────────────────────────────────────┘

┌─ REJECTION PATH ──────────────────────────────────────────────────────────┐
│                                                                            │
│ Admin Rejects (Only via Admin Panel)                                     │
├─ Go to: Admin Panel → Core → HR Profiles                                 │
├─ Find pending HR account                                                 │
├─ Click "✗ Reject" button                                                 │
├─ Form appears: Fill rejection reason (e.g., "Company not verified")      │
├─ Click "Reject & Delete"                                                 │
│                                                                            │
├─ Results:                                                                 │
│  ├─ HR account is PERMANENTLY DELETED                                   │
│  ├─ User record is DELETED                                              │
│  ├─ All associated data is removed                                       │
│  │                                                                         │
│  └─ ✉️ EMAIL SENT TO HR: "Application Rejected"                         │
│     ├─ Subject: Your HR Account Registration - RecruitHub                │
│     ├─ Message: Your application was rejected                            │
│     ├─ Reason: [Admin's rejection reason]                                │
│     └─ Note: HR must re-register if they want to reapply                 │
└────────────────────────────────────────────────────────────────────────────┘

┌─ LOGIN SCENARIOS ──────────────────────────────────────────────────────────┐
│                                                                             │
│ SCENARIO 1: Login Before Approval                                         │
├─ HR visits: /hr/login/                                                    │
├─ Enters valid username & password                                         │
├─ System checks: is_approved == False                                      │
│                                                                             │
├─ ❌ LOGIN DENIED                                                           │
├─ Error message shown:                                                      │
│  "Your HR account is pending admin approval. Please wait for verification."│
├─ HR is redirected back to login form                                       │
├─ HR must wait for admin approval                                           │
│                                                                             │
│ SCENARIO 2: Login After Approval                                          │
├─ HR visits: /hr/login/                                                    │
├─ Enters valid username & password                                         │
├─ System checks: is_approved == True                                       │
│                                                                             │
├─ ✅ LOGIN SUCCESSFUL                                                       │
├─ Success message: "Welcome HR [First Name]!"                              │
├─ HR redirects to: HR Dashboard                                            │
├─ HR can now:                                                              │
│  ├─ View all students                                                     │
│  ├─ Filter students (by branch, CGPA, backlogs)                          │
│  ├─ Sort students (by CGPA, backlogs, name, branch)                      │
│  ├─ View detailed student profiles                                        │
│  ├─ Download student resumes                                              │
│  └─ Access student GitHub, LinkedIn, HackerRank profiles                 │
└────────────────────────────────────────────────────────────────────────────┘
```

---

## Email Notifications

### 1. Approval Request Email (Admin)
**Sent to:** omtapdiya75@gmail.com  
**When:** Immediately after HR completes registration  
**Contains:**
- HR applicant full details (username, name, email)
- Company, designation, department information
- Two action links with unique tokens:
  - APPROVE link
  - REJECT link

### 2. Approval Confirmation Email (HR)
**Sent to:** HR's registered email  
**When:** Admin approves the account  
**Contains:**
- Confirmation: "Your HR account has been approved!"
- Login credentials instructions
- Login URL
- Instructions to access HR dashboard

### 3. Rejection Email (HR)
**Sent to:** HR's registered email  
**When:** Admin rejects the account  
**Contains:**
- Notification: "Your application was rejected"
- Reason provided by admin
- Note: HR can reapply if desired

---

## Database Fields (HRProfile Model)

### New Approval Fields Added in Migration 0008:

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `is_approved` | Boolean | False | Account approval status |
| `approval_requested_at` | DateTime | auto_now_add | When registration was submitted |
| `approved_by` | ForeignKey (User) | NULL | Admin who approved |
| `approved_at` | DateTime | NULL | When account was approved |
| `approval_token` | CharField (100) | NULL | Unique token for email links |
| `rejection_reason` | TextField | "" | Reason if rejected |

### Existing Fields:
- `user` - OneToOneField to User
- `company_name` - CharField
- `designation` - CharField
- `department` - CharField
- `created_at` - DateTimeField (auto_now_add)
- `updated_at` - DateTimeField (auto_now)

---

## Admin Interface Enhancements

### HR Profiles List View
- **Approval Status Badge:** Shows "✓ Approved" (green) or "⏳ Pending" (orange)
- **Approval Requested Time:** Shows when HR registered
- **Filter Options:**
  - Filter by `is_approved` status
  - Filter by department
  - Filter by approval_requested_at date
- **Sorting:** Pending approvals shown first

### HR Profile Detail View
- **Approval Status Section (Collapsible):**
  - Current approval status
  - Requested timestamp
  - Approved by (admin name)
  - Approval timestamp
  - Approval token
  - Rejection reason (if applicable)
- **Quick Action Buttons:**
  - "✓ Approve" button for pending accounts
  - "✗ Reject" button for pending accounts

---

## Code Implementation Details

### 1. HRProfile Model (`core/models.py`)
```python
class HRProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='hr_profile')
    company_name = models.CharField(max_length=255, blank=True)
    designation = models.CharField(max_length=100, blank=True)
    department = models.CharField(max_length=100, blank=True)
    
    # Approval workflow fields
    is_approved = models.BooleanField(default=False, help_text="HR account approved by admin")
    approval_requested_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_hr_profiles')
    approved_at = models.DateTimeField(null=True, blank=True)
    approval_token = models.CharField(max_length=100, unique=True, null=True, blank=True)
    rejection_reason = models.TextField(blank=True, help_text="Reason for rejection if applicable")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def generate_approval_token(self):
        """Generate unique approval token"""
        import secrets
        self.approval_token = secrets.token_urlsafe(50)
        self.save()
        return self.approval_token
```

### 2. View Functions (`core/views.py`)

**HR Registration Step 3:**
```python
# Sets is_approved=False
# Generates approval token
# Sends email to admin
# Shows "Awaiting admin approval" message
```

**HR Login:**
```python
# Checks if is_approved == True
# If False, shows "pending approval" message
# If True, allows login
```

**Approval Functions:**
- `approve_hr_account(token)` - Approves via token
- `reject_hr_account(token)` - Rejects via form
- `send_hr_approval_email()` - Sends admin notification
- `send_approval_confirmation_email()` - Sends approval to HR
- `send_rejection_email()` - Sends rejection to HR

### 3. URL Routes (`core/urls.py`)
```python
path('admin/approve-hr/<str:token>/', views.approve_hr_account, name='approve_hr_account'),
path('admin/reject-hr/<str:token>/', views.reject_hr_account, name='reject_hr_account'),
```

### 4. Admin Interface (`core/admin.py`)
- Enhanced HRProfileAdmin class
- Displays approval status badge
- Shows approval information
- Provides quick action buttons
- Orders pending approvals first

---

## Configuration Requirements

### Environment Variables

For **Production (Render/Deployment):**
```
HR_APPROVAL_EMAIL=omtapdiya75@gmail.com  # Admin email for approvals
SITE_URL=https://yourdomain.com          # For approval links in emails
```

For **Development (Local):**
```
HR_APPROVAL_EMAIL=omtapdiya75@gmail.com  # (optional, defaults to this)
SITE_URL=http://localhost:8000           # (optional, defaults to this)
```

### Email Backend Configuration

**Development (Console Output):**
```python
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
# Emails are printed to terminal instead of being sent
```

**Production (Resend API):**
```python
EMAIL_BACKEND = 'core.email_backends.ResendBackend'
RESEND_API_KEY = os.environ.get('RESEND_API_KEY')
```

---

## Migration Information

### Migration 0008 Details
- **File:** `core/migrations/0008_hrprofile_approval_requested_at_and_more.py`
- **Status:** ✅ Applied
- **Changes:**
  - Added 6 new fields to HRProfile model
  - All fields have appropriate defaults for existing records
  - Unique constraint on `approval_token`
  - ForeignKey relationship to User for `approved_by`

**Applied:** Yes (shows [X] in `python manage.py showmigrations`)

---

## Testing the Workflow

### Complete Step-by-Step Test:

1. **Start Server:**
   ```bash
   python manage.py runserver
   ```

2. **HR Register:**
   - Visit: http://localhost:8000/hr/register/
   - Complete 3-step registration (email → OTP → account details)
   - See success message: "Awaiting admin approval"
   - **Check Terminal:** Email with approval/rejection links shown

3. **Try to Login (Before Approval):**
   - Visit: http://localhost:8000/hr/login/
   - Enter credentials
   - See error: "Your HR account is pending admin approval"
   - ❌ Cannot login yet

4. **Admin Approves:**
   - **Option A:** Click approval link from terminal email
   - **Option B:** Admin Panel → HR Profiles → Click "✓ Approve"
   - **Check Terminal:** Confirmation email sent to HR

5. **HR Tries to Login (After Approval):**
   - Visit: http://localhost:8000/hr/login/
   - Enter credentials
   - ✅ Login successful!
   - Access HR Dashboard

---

## Security Features

✅ **Email Verification:** HR must verify email before account creation  
✅ **Admin Approval:** HR account cannot be used without admin approval  
✅ **Unique Tokens:** Approval links use cryptographically secure tokens  
✅ **Rejection Deletion:** Rejected accounts are permanently deleted  
✅ **Status Tracking:** Full audit trail of approval/rejection  
✅ **Email Notifications:** All parties notified via email  

---

## Files Modified

- ✅ `core/models.py` - HRProfile model updated with approval fields
- ✅ `core/views.py` - HR registration, login, approval, rejection views
- ✅ `core/admin.py` - Enhanced HR admin interface
- ✅ `core/urls.py` - Added approval/rejection URL routes
- ✅ `core/migrations/0008_*.py` - Database migration for new fields
- ✅ `core/templates/core/reject_hr_account.html` - Rejection form template
- ✅ `README.md` - Complete workflow documentation

---

## Status: ✅ COMPLETE

All components implemented and tested:
- ✅ Database model with approval fields
- ✅ Migration created and applied
- ✅ Email notifications (approval request, confirmation, rejection)
- ✅ Admin approval interface (email links + admin panel)
- ✅ HR login approval check
- ✅ Admin panel enhancements
- ✅ Complete documentation
- ✅ All Python files compile successfully
- ✅ Django system checks pass

**Ready for deployment to Render!**
