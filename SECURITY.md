# Security Implementation Guide

## Overview
This document outlines all security measures implemented in the RecruitHub authentication system.

---

## 1. 🔐 SQL Injection Protection

### Implementation
- **Django ORM Parameterized Queries**: All database queries use Django's ORM which automatically parameterizes queries
- **No Raw SQL**: Application avoids raw SQL queries
- **Query Validation**: All user inputs are validated before database operations

### Example
```python
# ✅ Safe (Django ORM)
User.objects.filter(username=username)

# ❌ Unsafe (if it were used)
# User.objects.raw(f"SELECT * FROM users WHERE username = '{username}'")
```

---

## 2. 🔐 XSS (Cross-Site Scripting) Protection

### Implementation

#### Input Sanitization
- **Bleach Library**: All user inputs sanitized using the `bleach` library
- **Removed HTML/JS Tags**: All dangerous HTML and JavaScript stripped from input fields
- **Custom Sanitizer**: `sanitize_input()` function in `core/forms.py`

```python
def sanitize_input(value):
    """Sanitize user input to prevent XSS attacks"""
    return clean(str(value).strip(), tags=[], strip=True)
```

#### Template Safety
- **Auto-escaping**: Django templates auto-escape variables by default
- **mark_safe() Limited Use**: Only used where absolutely necessary
- **Content Security Policy**: Strict CSP headers implemented

#### Security Headers
- `X-XSS-Protection: 1; mode=block`
- `Content-Security-Policy`: Restricts script sources
- `X-Content-Type-Options: nosniff`

### Affected Fields
- Username
- First Name
- Last Name
- Email (validated separately)
- All text input fields

---

## 3. 🔐 CSRF (Cross-Site Request Forgery) Protection

### Implementation

#### Django CSRF Middleware
- **CSRF Token in Forms**: All forms include `{% csrf_token %}`
- **CSRF Middleware**: `django.middleware.csrf.CsrfViewMiddleware` enabled
- **CSRF Token Validation**: All POST requests require valid CSRF token

#### Configuration
```python
# settings.py
CSRF_COOKIE_SECURE = not DEBUG  # HTTPS only in production
CSRF_COOKIE_HTTPONLY = True     # Not accessible via JavaScript
CSRF_TRUSTED_ORIGINS = [
    'https://vakverse.com',
    'https://*.vakverse.com'
]
CSRF_COOKIE_AGE = 31449600  # 1 year
```

#### Implementation in Templates
All forms include CSRF protection:
```html
<form method="post">
    {% csrf_token %}
    <!-- form fields -->
</form>
```

---

## 4. 🔐 Rate Limiting (Brute Force Protection)

### Implementation

#### Login Rate Limiting
- **Limit**: 5 login attempts per 15 minutes (900 seconds)
- **Per IP**: Rate limiting is applied per client IP address
- **Affected Endpoints**:
  - `/accounts/login/` (Student login)
  - `/hr/login/` (HR login)

#### Code
```python
class RateLimitMiddleware(MiddlewareMixin):
    # 5 attempts per 15 minutes per IP
    if attempts >= 5:
        return HttpResponse(
            'Too many login attempts. Please try again in 15 minutes.',
            status=429
        )
```

#### Response
- **HTTP 429**: Too Many Requests status code
- **User-friendly message**: Clear error message
- **Automatic Reset**: Counter resets after 15 minutes

---

## 5. 🔐 Session Security & Expiry

### Implementation

#### Session Timeout
- **Session Duration**: 1 hour (3600 seconds)
- **Idle Timeout**: Session expires at browser close
- **Refresh on Request**: Session updated on every request

#### Configuration
```python
# settings.py
SESSION_COOKIE_AGE = 3600  # 1 hour
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_COOKIE_HTTPONLY = True  # Not accessible via JavaScript
SESSION_SAVE_EVERY_REQUEST = True  # Update on every request
SESSION_COOKIE_SECURE = not DEBUG  # HTTPS only in production
```

#### Features
- ✅ Automatic logout after 1 hour of inactivity
- ✅ HttpOnly cookies prevent JavaScript access
- ✅ Secure flag ensures HTTPS transmission in production
- ✅ Session renewed on every request (sliding window)

---

## 6. 🔐 Additional Security Measures

### Input Validation
- **Required Fields**: Username, email, first name, last name all required
- **Duplicate Prevention**: Checks for existing usernames and emails
- **Password Requirements**: Minimum 8 characters
- **Email Validation**: Django's built-in email validator

### Security Headers
| Header | Value | Purpose |
|--------|-------|---------|
| X-Content-Type-Options | nosniff | Prevent MIME type sniffing |
| X-Frame-Options | DENY | Prevent clickjacking |
| X-XSS-Protection | 1; mode=block | XSS protection in older browsers |
| Referrer-Policy | strict-origin-when-cross-origin | Control referrer information |
| Permissions-Policy | geolocation=(), microphone=(), camera=() | Disable dangerous APIs |
| Strict-Transport-Security | max-age=31536000; includeSubDomains | Force HTTPS for 1 year |

### Database Security
- **Django ORM**: Prevents SQL injection
- **Parameterized Queries**: All queries use placeholders
- **Connection SSL**: PostgreSQL connections use SSL in production

### Password Security
- **Hashing**: Django's PBKDF2 password hasher with SHA256
- **Salt**: Automatic salt generation for each password
- **Iterations**: 260,000+ iterations for hash computation

---

## 7. 📋 Testing & Verification

### How to Test Security

#### Test Rate Limiting
```bash
# Try multiple login attempts
for i in {1..6}; do
    curl -X POST http://localhost:8000/accounts/login/ \
         -d "username=test&password=wrong"
done
# After 5 attempts, you should get HTTP 429
```

#### Test CSRF Protection
```bash
# POST without CSRF token should fail
curl -X POST http://localhost:8000/accounts/login/ \
     -d "username=test&password=test123"
# Should return 403 Forbidden
```

#### Test XSS Protection
```bash
# Try registering with XSS payload
# Username: <script>alert('xss')</script>
# Result: Script tags are stripped, username becomes clean
```

#### Test Session Expiry
```bash
# Login, then wait 1 hour
# Session should expire and user redirected to login
```

---

## 8. 🛡️ Security Best Practices

### For Developers
1. ✅ Always use Django ORM for database queries
2. ✅ Never use string formatting for SQL queries
3. ✅ Always include `{% csrf_token %}` in POST forms
4. ✅ Use `sanitize_input()` for user-submitted text
5. ✅ Never mark user input as safe with `|safe`
6. ✅ Use HTTPS in production
7. ✅ Keep Django and dependencies updated

### For Users
1. ✅ Use strong passwords (8+ characters)
2. ✅ Don't share login credentials
3. ✅ Log out when done
4. ✅ Use HTTPS URLs only
5. ✅ Enable 2FA when available

---

## 9. 📦 Dependencies for Security

```
django-ratelimit>=4.1.0  # Rate limiting
bleach>=6.1.0            # Input sanitization
Django==6.0.0            # Core framework with built-in security
```

---

## 10. 🔧 Configuration Checklist

- [x] CSRF protection enabled
- [x] CSRF cookies are HttpOnly
- [x] CSRF cookies are Secure (in production)
- [x] Session cookies are HttpOnly
- [x] Session timeout set to 1 hour
- [x] Rate limiting implemented (5 attempts/15 min)
- [x] Security headers configured
- [x] Input sanitization implemented
- [x] XSS protection headers added
- [x] HSTS enabled (in production)
- [x] SQL injection prevention via ORM
- [x] Password hashing enabled

---

## 11. 📝 Future Improvements

- [ ] Implement 2FA (Two-Factor Authentication)
- [ ] Add account lockout after failed attempts
- [ ] Implement API rate limiting with JWT tokens
- [ ] Add password reset rate limiting
- [ ] Implement device fingerprinting
- [ ] Add security audit logging
- [ ] Implement Web Application Firewall (WAF) rules

---

## Emergency Contacts

For security issues, please email: security@vakverse.com

**Do not** publicly disclose security vulnerabilities. Report them privately.

---

Last Updated: December 21, 2025
Security Level: ⭐⭐⭐⭐ (Production Ready)
