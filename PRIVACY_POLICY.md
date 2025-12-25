# Privacy Policy

**Last Updated:** December 25, 2025  
**Version:** 1.0  
**Effective Date:** December 25, 2025

## 📋 Table of Contents
1. [Introduction](#introduction)
2. [Information We Collect](#information-we-collect)
3. [How We Use Your Information](#how-we-use-your-information)
4. [Data Security](#data-security)
5. [Your Rights & Choices](#your-rights--choices)
6. [Third-Party Services](#third-party-services)
7. [Data Retention](#data-retention)
8. [Contact Us](#contact-us)

---

## Introduction

RecruitHub ("**we**", "**us**", "**our**", or "**the Platform**") is committed to protecting your privacy. This Privacy Policy explains how we collect, use, disclose, and safeguard your information when you visit our website and use our services.

**Scope:** This policy applies to all users of RecruitHub, including:
- Students registering for placement opportunities
- HR professionals managing recruitment
- Administrators managing the platform

**Note:** We do not knowingly collect information from children under 18 years old. If we become aware of such collection, we will take steps to delete such information.

---

## Information We Collect

### 1. **Information You Provide Directly**

#### Student Registration & Profile
- **Email Address** (used for OTP verification and communication)
- **Full Name** (for identification and communication)
- **Password** (securely hashed with PBKDF2-SHA256)
- **Phone Number** (optional, for contact)
- **Date of Birth** (for profile completeness)
- **Address** (optional, for communication)

#### Academic Information
- **Branch/Specialization** (field of study)
- **CGPA** (cumulative grade point average)
- **Backlogs Count** (incomplete courses)
- **Admission Year** (year of admission)
- **Degree** (undergraduate/postgraduate)

#### Professional Information
- **Skills** (programming languages, tools, frameworks)
- **Experience** (work experience, internships, projects)
- **Bio/About** (professional summary)
- **Resume/CV** (PDF file)
- **Certifications** (professional certifications)

#### Social & Media
- **GitHub Username** (optional, professional profile)
- **LinkedIn Profile** (optional, professional network)
- **HackerRank Username** (optional, coding profile)
- **Portfolio URL** (optional, personal portfolio)
- **Profile Photo** (optional, profile picture)

#### HR Registration & Company Info
- **Company Name** (organization details)
- **Designation** (job title/role)
- **Department** (department name)
- **Work Email** (company email address)
- **Password** (securely hashed)

### 2. **Information Collected Automatically**

#### Server Logs & Analytics
- **IP Address** (for rate limiting and security)
- **Browser Type & Version** (device information)
- **Operating System** (system information)
- **Referrer Page** (how you accessed the site)
- **Pages Visited** (navigation behavior)
- **Time & Date of Access** (activity timestamps)
- **Session Duration** (how long you used the platform)

#### Cookies & Session Data
- **Session Cookies** (for authentication and session management)
- **Rate Limiting Data** (IP-based access tracking)
- **Preferences** (language, theme, display settings)

#### Email & Communication
- **OTP Codes** (time-limited, automatically deleted after verification)
- **Email Verification Status** (whether email is verified)
- **Login Timestamps** (for security audit)

### 3. **File Uploads**
- **Resume/CV Files** (stored on AWS S3)
- **Profile Photos** (stored on AWS S3)
- **Document Metadata** (filename, upload date, file size)

---

## How We Use Your Information

### 1. **Account Management**
- Creating and maintaining your account
- Processing registration and login requests
- Sending account notifications and updates
- Password reset and account recovery
- Verifying email ownership via OTP

### 2. **Service Delivery**
- **For Students:**
  - Displaying your profile to HR professionals
  - Filtering students by criteria (CGPA, branch, etc.)
  - Enabling job and internship opportunities
  - Communication about placements

- **For HR:**
  - Viewing and searching student profiles
  - Filtering and sorting student lists
  - Making hiring decisions
  - Downloading resumes and documents

### 3. **Communication**
- Sending transactional emails (OTP, password reset, account updates)
- Notifying about important platform changes
- Sending placement opportunities (HR notifications to students)
- Responding to support inquiries

### 4. **Security & Safety**
- Detecting and preventing fraudulent activities
- Enforcing rate limiting (preventing brute-force attacks)
- Protecting against unauthorized access
- Maintaining system integrity and security
- Investigating security incidents

### 5. **Analytics & Improvement**
- Analyzing platform usage patterns
- Identifying popular features
- Understanding user behavior
- Improving user experience
- Optimizing platform performance
- A/B testing and feature development

### 6. **Compliance & Legal**
- Complying with legal obligations
- Responding to lawful requests from authorities
- Protecting our rights and property
- Resolving disputes

---

## Data Security

### Encryption & Hashing
- **Passwords:** PBKDF2-SHA256 hashing (industry standard)
- **HTTPS:** All data transmitted over encrypted SSL/TLS connections
- **At Rest:** Sensitive data encrypted at rest on servers
- **OTP Storage:** Hashed and time-limited (10-minute validity)

### Access Controls
- **Authentication:** Session-based authentication with secure tokens
- **Authorization:** Role-based access control (Student/HR/Admin)
- **Admin Panel:** Requires superuser credentials
- **Data Isolation:** Students cannot access other student data
- **HR Filtering:** HR users filtered to see only approved accounts

### Network Security
- **Firewalls:** Configured on hosting infrastructure
- **DDoS Protection:** Render.com provides infrastructure protection
- **Rate Limiting:** IP-based rate limiting to prevent brute-force attacks
- **Security Headers:** 
  - X-Frame-Options: DENY (prevent clickjacking)
  - X-Content-Type-Options: nosniff (prevent MIME type sniffing)
  - Content-Security-Policy: Configured to prevent XSS attacks
  - HSTS: 1-year max-age for HTTPS enforcement

### Database Security
- **PostgreSQL:** Hosted on Render Cloud with encrypted connections
- **Backups:** Automatic daily backups
- **Access:** Limited to application only
- **Credentials:** Stored in secure environment variables

### File Storage Security
- **AWS S3:** Bucket policies restrict public access
- **Encryption:** Files encrypted at rest on S3
- **Access Control:** Only authenticated users can upload/download
- **Virus Scanning:** Recommended (optional) for resume files

---

## Your Rights & Choices

### 1. **Access Your Data**
You have the right to access your personal information. You can view and download your profile data through your account dashboard.

**Request Process:**
- Log into your account
- Navigate to Settings/Profile
- Download your data or request export

### 2. **Correct Your Information**
You can update or correct your profile information at any time through your account settings.

**What You Can Update:**
- Phone number
- Address
- Skills and experience
- Social media links
- Profile photo
- Resume

### 3. **Delete Your Account**
You can request account deletion. Upon deletion:
- Your account and profile will be permanently removed
- Associated documents may remain (contact support)
- Data retained for legal/compliance reasons as noted below

**Process:**
- Contact support@yourdomain.com
- Confirm your identity
- Account deletion within 30 days

### 4. **Data Portability**
You can request a copy of your data in a portable format (JSON/CSV).

### 5. **Opt-Out of Communications**
You can control email preferences:
- Transactional emails (cannot opt-out - required for account)
- Marketing emails (can opt-out via unsubscribe)
- Platform notifications (configurable in settings)

### 6. **Restrict Processing**
You can request to limit how we use your data, though this may impact service functionality.

### 7. **Lodge a Complaint**
If you believe we've mishandled your data, you can:
- Contact us directly (see Contact Us section)
- File a complaint with your local data protection authority

---

## Third-Party Services

### 1. **Resend Email Service**
- **Purpose:** Sending OTP codes, password reset, and transactional emails
- **Data Shared:** Email address, verification codes
- **Privacy Policy:** [Resend Privacy Policy](https://resend.com/privacy)
- **Data Location:** Resend servers (may be US-based)

### 2. **AWS S3 Storage**
- **Purpose:** Storing resume files and profile photos
- **Data Shared:** File uploads, metadata
- **Privacy Policy:** [AWS Privacy Policy](https://aws.amazon.com/privacy/)
- **Data Location:** AWS region configured in environment
- **Encryption:** Files encrypted at rest

### 3. **Render Cloud Hosting**
- **Purpose:** Application hosting and database services
- **Data Shared:** All application data
- **Privacy Policy:** [Render Privacy Policy](https://render.com/privacy)
- **Data Location:** Render infrastructure (US-based)

### 4. **PostgreSQL Database**
- **Purpose:** Data storage and management
- **Data Shared:** All user data, profiles, documents metadata
- **Security:** Encrypted connections, automatic backups

### 5. **Django & Open Source Libraries**
- **Purpose:** Application framework and functionality
- **Note:** No data is sent to third parties by these libraries

---

## Data Retention

### 1. **Active Accounts**
- **Duration:** Data retained as long as account is active
- **Access:** You can delete your account anytime

### 2. **Inactive Accounts**
- **Deletion Policy:** Accounts inactive for 2 years may be deleted
- **Notice:** Warning email sent before deletion
- **Retrieval:** Contact support to reactivate

### 3. **Deleted Accounts**
- **Timeline:** Permanently deleted within 30 days of request
- **Exceptions:** 
  - Data required by law is retained
  - Backup copies may persist for 90 days
  - Transaction records retained for compliance

### 4. **OTP & Temporary Data**
- **OTP Codes:** Deleted after 10 minutes (expiration)
- **Session Data:** Deleted after 30 days of inactivity
- **Logs:** Retained for 90 days for security audit

### 5. **Legal Holds**
If we receive a legal request, we may retain your data beyond normal retention periods to comply with the law.

---

## Contact Us

### Privacy Inquiries
For privacy-related questions or concerns, contact:

**Email:** privacy@yourdomain.com  
**Address:** [Your Institution/Company Address]  
**Response Time:** 30 days for privacy requests

### Data Protection Officer
For GDPR/data protection matters:

**Email:** dpo@yourdomain.com  
**Phone:** [Your Contact Number]

### Support
For general support and account issues:

**Email:** support@yourdomain.com  
**Website:** [Your Support Portal]

### Legal Notices
For legal issues or regulatory matters:

**Email:** legal@yourdomain.com

---

## Changes to This Privacy Policy

We may update this Privacy Policy periodically to reflect changes in our practices, technology, legal requirements, or other factors.

**Notification:**
- Material changes will be announced via email or prominent notice on the platform
- Your continued use of the platform constitutes acceptance of the updated policy
- You should review this policy periodically for updates

**Version History:**
- **v1.0** - December 25, 2025 - Initial privacy policy

---

## Compliance & Standards

### Regulatory Compliance
This Privacy Policy is designed to comply with:
- **GDPR** (General Data Protection Regulation) - EU data protection
- **CCPA** (California Consumer Privacy Act) - California residents
- **PIPEDA** (Personal Information Protection Act) - Canada
- **Local Data Protection Laws** - As applicable to your jurisdiction

### Security Standards
We implement security practices aligned with:
- **OWASP Top 10** - Web application security
- **PCI DSS** - Payment data security (if applicable)
- **ISO 27001** - Information security management

---

## Special Considerations

### For Students
Your profile information is shared with approved HR professionals to facilitate job opportunities. Only data you provide is visible to recruiters. You can:
- Make your profile private (contact support)
- Remove specific information
- Opt-out of recruitment entirely (limited service)

### For HR Professionals
Your company information and approval status are managed by platform administrators. We:
- Verify email ownership via OTP
- Require admin approval before dashboard access
- Monitor account activity for security

### For International Users
If you access this platform from outside your country:
- Your data may be transferred internationally
- Different privacy laws may apply
- We maintain data protection standards across regions

---

## Acknowledgment

By using RecruitHub, you acknowledge that you have read and understood this Privacy Policy and agree to the collection and use of your information as described.

**Questions?** Contact us at privacy@yourdomain.com

---

## Additional Resources

- [Terms of Service](./TERMS_OF_SERVICE.md) - How to use the platform
- [Security Policy](./SECURITY.md) - Security practices and reporting
- [Cookie Policy](./COOKIE_POLICY.md) - Cookie usage and management
- [GitHub Repository](https://github.com/Om-mac/RecruitHub) - Transparency and code review

---

**© 2025 RecruitHub. All rights reserved.**

*This Privacy Policy is provided as-is. Customize it according to your organization's specific practices and jurisdiction.*
