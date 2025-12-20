# 📊 HR Portal - Visual Guide & Features

## 🎯 Main Pages Overview

### 1. HR Dashboard (`/hr/dashboard/`)
```
┌─────────────────────────────────────────────────────────┐
│                   HR Dashboard                          │
│                                                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐
│  │ Total    │  │ Avg      │  │ Zero     │  │ Total    │
│  │ Students │  │ CGPA     │  │ Backlogs │  │ Branches │
│  │    42    │  │  7.85    │  │   23     │  │    4     │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘
│
│  ┌─────────────────────────────────────────────────────┐
│  │ Filters & Sorting                                   │
│  │ Branch: [CSE ▼] CGPA Min: [___] CGPA Max: [___]    │
│  │ Backlogs: [___] Sort By: [CGPA (H-L) ▼]            │
│  │ [Filter] [Clear]                                    │
│  └─────────────────────────────────────────────────────┘
│
│  ┌─────────────────────────────────────────────────────┐
│  │ Name    │ Roll │ Branch│CGPA │Backlog│Links        │
│  ├─────────┼──────┼───────┼─────┼────────┼─────────────┤
│  │John Doe │ CS01 │ CSE   │ 8.5 │  🟢 0  │ [GH] [LI]  │
│  │Jane Sm..│ CS02 │ CSE   │ 7.9 │  🟢 0  │ [GH] [LI]  │
│  │...      │ ...  │ ...   │ ... │  ...   │ ...         │
│  └─────────────────────────────────────────────────────┘
│                                                          │
│  [View] [View] [View]...                               │
│
│  💼 HR User │ [Dashboard] [Logout]                     │
└─────────────────────────────────────────────────────────┘
```

### 2. Student Detail Page (`/hr/student/<id>/`)
```
┌──────────────────────────────────────────────────────────┐
│ [← Back to Dashboard]                                    │
│
│ ┌──────────────┐  ┌────────────────────────────────┐   │
│ │              │  │ Name: John Doe                 │   │
│ │  [Photo]     │  │ Username: cs01                 │   │
│ │              │  │ Email: john@example.com        │   │
│ │              │  │ Phone: +91 9999999999         │   │
│ │              │  │ City: Bangalore, State: KA    │   │
│ └──────────────┘  └────────────────────────────────┘   │
│
│ ┌────────────────────────────────────────────────────┐  │
│ │ Academic Information                               │  │
│ │ College: XYZ Institute         Branch: CSE         │  │
│ │ Degree: B.Tech                CGPA: 8.5 🟢         │  │
│ │ Admission: 2021               Backlogs: 0 🟢       │  │
│ │ Year of Study: Final Year      Total Backlogs: 1   │  │
│ └────────────────────────────────────────────────────┘  │
│
│ ┌────────────────────────────────────────────────────┐  │
│ │ Professional Information                           │  │
│ │ Skills: [Python] [Web Dev] [React] [Django]        │  │
│ │ Experience: Intern at ABC Corp (6 months)          │  │
│ │ Bio: Passionate about full-stack development       │  │
│ └────────────────────────────────────────────────────┘  │
│
│ ┌────────────────────────────────────────────────────┐  │
│ │ Social & Platform Links                            │  │
│ │ GitHub:      [🔗 john-doe]        → github.com     │  │
│ │ LinkedIn:    [🔗 john-doe]        → linkedin.com   │  │
│ │ HackerRank:  [🔗 johndoe]         → hackerrank.com │  │
│ │ Other:       LeetCode: johndoe                      │  │
│ └────────────────────────────────────────────────────┘  │
│
│ ┌────────────────────────────────────────────────────┐  │
│ │ Documents                                          │  │
│ │ Resume: [📥 Download]                              │  │
│ └────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────┘
```

### 3. HR Login Page (`/hr/login/`)
```
┌────────────────────────────────────┐
│       💼 HR Login                  │
│                                    │
│  Username: [________________]     │
│  Password: [________________]     │
│                                    │
│         [Login]                    │
│                                    │
│  Don't have account?              │
│  [Register as HR]                 │
│                                    │
│  Student Login?                   │
│  [Student Login]                  │
│                                    │
└────────────────────────────────────┘
```

---

## 🎨 Color Coding System

### CGPA Display
```
CGPA ≥ 8.0  → 🟢 GREEN   (Excellent)
CGPA ≥ 7.0  → 🔵 BLUE    (Good)
CGPA < 7.0  → 🟡 YELLOW  (Average)
```

### Backlogs Display
```
Backlogs = 0   → 🟢 GREEN   (Clear)
Backlogs 1-2   → 🟡 YELLOW  (Few)
Backlogs > 2   → 🔴 RED     (Many)
```

### Badges
```
CSE   → [CSE]      (blue badge)
ECE   → [ECE]      (blue badge)
MECH  → [MECH]     (blue badge)
etc...
```

---

## 🔍 Filtering Examples

### Scenario 1: Top CSE Students (CGPA ≥ 8.5, No Backlogs)
```
Branch:  CSE
CGPA Min: 8.5
CGPA Max: 10.0
Backlogs: 0
Sort By: CGPA (High to Low)

Result: Shows CSE students with CGPA 8.5+ and 0 backlogs,
        sorted by highest CGPA first
```

### Scenario 2: All ECE Students Ready to Hire
```
Branch: ECE
Backlogs: 0
Sort By: CGPA (High to Low)

Result: Shows all ECE students with zero backlogs,
        sorted by CGPA
```

### Scenario 3: Students in CGPA Range 7-8
```
CGPA Min: 7.0
CGPA Max: 8.0
Sort By: Name (A-Z)

Result: Shows all students with CGPA between 7-8,
        sorted alphabetically
```

---

## 📊 Dashboard Statistics

### Automatic Calculations
```
┌─────────────────────────────────────────┐
│ Total Students: 42                      │
│ (All registered student profiles)       │
│                                         │
│ Avg CGPA: 7.85                          │
│ (Sum of all CGPAs ÷ Number of students) │
│                                         │
│ Zero Backlogs: 23                       │
│ (Students with current_backlogs = 0)    │
│                                         │
│ Branches: 4                             │
│ (Unique branch values: CSE, ECE, ME, CE)│
└─────────────────────────────────────────┘
```

---

## 🔗 Social Media Integration

### Direct Links Format
```
GitHub:     https://www.github.com/[username]
LinkedIn:   https://www.linkedin.com/in/[username]
HackerRank: https://www.hackerrank.com/[username]
Other:      Platform: Username (custom format)
```

### Quick Access Buttons
```
Dashboard:
┌──────┬──────┬──────┐
│ [GH] │ [LI] │ [HR] │  ← Click to visit profile
└──────┴──────┴──────┘

Detail Page:
┌───────────────────────────────┐
│ GitHub:   [🔗 john-doe]       │ ← Clickable link
│ LinkedIn: [🔗 john-doe]       │
│ HackerRank: [🔗 johndoe]      │
└───────────────────────────────┘
```

---

## 🎯 Sorting Options

### Visual Guide
```
CGPA (High to Low):    8.9 → 8.8 → 7.5 → 7.2 → 6.8
CGPA (Low to High):    6.8 → 7.2 → 7.5 → 8.8 → 8.9
Backlogs (High to Low): 5 → 4 → 3 → 2 → 1 → 0
Backlogs (Low to High): 0 → 1 → 2 → 3 → 4 → 5
Name (A-Z):           Alice → Bob → Charlie → Dan
Name (Z-A):           Dan → Charlie → Bob → Alice
Branch:               CE → CSE → ECE → ME
```

---

## 📱 Responsive Design Breakpoints

```
Desktop (≥992px):
┌──────────────────────────────────────────────────┐
│ [Logo] [HR Dashboard] [Profile] [Logout]        │
├──────────────────────────────────────────────────┤
│ [Stats Cards in 4 columns]                       │
│ [Filter Form in 6 columns]                       │
│ [Full Table with all columns]                    │
└──────────────────────────────────────────────────┘

Tablet (768px - 991px):
┌─────────────────────────────────┐
│ [Logo] [☰ Menu]                 │
├─────────────────────────────────┤
│ [Stats Cards in 2 columns]      │
│ [Filter Form stacked]           │
│ [Table with scroll]             │
└─────────────────────────────────┘

Mobile (< 768px):
┌────────────────┐
│ [Logo] [☰]     │
├────────────────┤
│ [Stats Cards]  │
│ [Filter Form]  │
│ [Table scroll] │
└────────────────┘
```

---

## 🎬 User Flow

### HR User Journey
```
1. Visit /hr/login/
         ↓
2. Enter credentials (hr_admin / hr123456)
         ↓
3. Redirected to /hr/dashboard/
         ↓
4. See all students with statistics
         ↓
5. Apply filters and sort
         ↓
6. See filtered results
         ↓
7. Click "View" on student
         ↓
8. See detailed profile with:
   - All academic info
   - Social media links
   - Resume download
   ↓
9. Click social link → Opens in new tab
   ↓
10. Back to dashboard or logout
```

### Student Journey
```
1. Visit /register/
         ↓
2. Create account
         ↓
3. Go to /profile/
         ↓
4. Fill in details:
   - Branch (IMPORTANT)
   - CGPA
   - Backlogs
   - GitHub username
   - LinkedIn username
   - etc.
         ↓
5. Upload resume
         ↓
6. Save profile
         ↓
7. Now visible to HR dashboard
         ↓
8. HR can view your profile
         ↓
9. HR can access your social links
         ↓
10. HR can download your resume
```

---

## 💡 Tips for HR Users

### Finding Best Candidates
1. **Top Performers:** CGPA ≥ 8.5, Zero Backlogs
2. **Good All-Rounders:** CGPA 7.5-8.5, Zero Backlogs
3. **By Department:** Filter by branch, sort by CGPA
4. **Quick Contact:** Use social media links

### Efficient Filtering
- Use branch filter first (narrows down significantly)
- Then apply CGPA range
- Finally sort by CGPA for rankings

### Resume Review
- Download resumes from student detail page
- Check experience and projects
- Cross-reference with social profiles

---

## 📈 Sample Statistics

### Typical Dashboard Numbers
```
College with 4 Branches (CSE, ECE, ME, CE)

Total Students: 150-200
Average CGPA: 7.2-7.8
Students with Zero Backlogs: 60-70% (90-140)
Branch Distribution:
  - CSE: 50 students
  - ECE: 40 students
  - ME: 35 students
  - CE: 25 students
```

### Filtering Results
```
All CSE Students: 50
CSE with CGPA ≥ 7.5: 35
CSE with CGPA ≥ 8.0 and Zero Backlogs: 15
```

---

## 🔐 Security Visual

```
Login Page:
┌────────────────────────────┐
│ HTTPS Connection (Secure) │
│ CSRF Token (Validated)    │
│ Password Hashing          │
│ Session Management        │
└────────────────────────────┘
         ↓
   Authenticated User
         ↓
┌────────────────────────────┐
│ Dashboard Access           │
│ (HR Profile Required)      │
│ View Student Data          │
│ Download Resumes           │
│ (User Validation)          │
└────────────────────────────┘
         ↓
   Logout → Session Ended
```

---

## 📊 Data Flow Diagram

```
Student Registration
     ↓
Student Completes Profile (Branch, CGPA, Links)
     ↓
Profile Saved to Database
     ↓
Student Visible in HR Dashboard
     ↓
HR Filters/Sorts Students
     ↓
HR Views Student Details
     ↓
HR Clicks Social Link → Profile Opens
     ↓
HR Downloads Resume
     ↓
Recruitment Process
```

---

## ✨ Feature Summary Table

| Feature | Where | How |
|---------|-------|-----|
| View Students | Dashboard | Auto-loads all |
| Filter Branch | Dashboard | Dropdown select |
| Filter CGPA | Dashboard | Min/Max inputs |
| Filter Backlogs | Dashboard | Number input |
| Sort Results | Dashboard | Dropdown select |
| Statistics | Dashboard | Auto-calculated |
| View Profile | Detail Page | Click "View" button |
| Access GitHub | Dashboard/Detail | Click GitHub button |
| Download Resume | Detail Page | Click Download |

---

This visual guide covers all major features and workflows in the HR Portal system.

Generated: December 21, 2025
