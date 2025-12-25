# Rate Limiting Configuration Guide

## Overview
Rate limiting is **disabled by default**. Enable it via environment variables for production security.

## Master Switch
```bash
ENABLE_RATE_LIMITING=True
```
Set this to `True` to enable all rate limiting features. All other rate limit settings require this to be `True`.

## Configuration Options

### 1. Login Rate Limiting
Prevents brute force attacks on login forms.

```bash
ENABLE_RATE_LIMITING=True
RATE_LIMIT_LOGIN_ENABLED=True
RATE_LIMIT_LOGIN_ATTEMPTS=5        # Max attempts
RATE_LIMIT_LOGIN_WINDOW=900         # Time window in seconds (15 minutes)
```

**Protected endpoints:**
- `/accounts/login/` (Student login)
- `/hr/login/` (HR login)

**Default limits:**
- 5 attempts per 15 minutes per IP

**Response on limit:** HTTP 429 - "Too many login attempts. Please try again in 15 minutes."

---

### 2. Registration Rate Limiting
Prevents spam registrations and account creation attacks.

```bash
ENABLE_RATE_LIMITING=True
RATE_LIMIT_REGISTRATION_ENABLED=True
RATE_LIMIT_REGISTRATION_ATTEMPTS=3 # Max registrations
RATE_LIMIT_REGISTRATION_WINDOW=3600 # Time window in seconds (1 hour)
```

**Protected endpoints:**
- `/register/` (Student registration)
- `/hr/register/` (HR registration)

**Default limits:**
- 3 attempts per 1 hour per IP

**Response on limit:** HTTP 429 - "Too many registration attempts. Please try again in 1 hour."

---

### 3. OTP Rate Limiting
Prevents brute force attacks on OTP verification.

```bash
ENABLE_RATE_LIMITING=True
RATE_LIMIT_OTP_ENABLED=True
RATE_LIMIT_OTP_ATTEMPTS=5   # Max OTP attempts
RATE_LIMIT_OTP_WINDOW=600    # Time window in seconds (10 minutes)
```

**Protected endpoints:**
- `/verify-otp/` (OTP verification)
- `/request-otp/` (Request new OTP)

**Default limits:**
- 5 attempts per 10 minutes per IP

**Response on limit:** HTTP 429 - "Too many OTP attempts. Please try again in 10 minutes."

---

### 4. Password Reset Rate Limiting
Prevents abuse of password reset functionality.

```bash
ENABLE_RATE_LIMITING=True
RATE_LIMIT_PASSWORD_RESET_ENABLED=True
RATE_LIMIT_PASSWORD_RESET_ATTEMPTS=3  # Max reset attempts
RATE_LIMIT_PASSWORD_RESET_WINDOW=3600  # Time window in seconds (1 hour)
```

**Protected endpoints:**
- `/password-reset/` (Password reset)
- `/forgot-password/` (Forgot password)

**Default limits:**
- 3 attempts per 1 hour per IP

**Response on limit:** HTTP 429 - "Too many password reset attempts. Please try again in 1 hour."

---

## Production Configuration Examples

### Example 1: Strict Security (Recommended)
```bash
# Master switch
ENABLE_RATE_LIMITING=True

# Login: 3 attempts per 10 minutes
RATE_LIMIT_LOGIN_ENABLED=True
RATE_LIMIT_LOGIN_ATTEMPTS=3
RATE_LIMIT_LOGIN_WINDOW=600

# Registration: 2 per hour
RATE_LIMIT_REGISTRATION_ENABLED=True
RATE_LIMIT_REGISTRATION_ATTEMPTS=2
RATE_LIMIT_REGISTRATION_WINDOW=3600

# OTP: 3 attempts per 5 minutes
RATE_LIMIT_OTP_ENABLED=True
RATE_LIMIT_OTP_ATTEMPTS=3
RATE_LIMIT_OTP_WINDOW=300

# Password Reset: 2 per hour
RATE_LIMIT_PASSWORD_RESET_ENABLED=True
RATE_LIMIT_PASSWORD_RESET_ATTEMPTS=2
RATE_LIMIT_PASSWORD_RESET_WINDOW=3600
```

### Example 2: Moderate Security
```bash
ENABLE_RATE_LIMITING=True

RATE_LIMIT_LOGIN_ENABLED=True
RATE_LIMIT_LOGIN_ATTEMPTS=5
RATE_LIMIT_LOGIN_WINDOW=900

RATE_LIMIT_REGISTRATION_ENABLED=True
RATE_LIMIT_REGISTRATION_ATTEMPTS=3
RATE_LIMIT_REGISTRATION_WINDOW=3600

RATE_LIMIT_OTP_ENABLED=True
RATE_LIMIT_OTP_ATTEMPTS=5
RATE_LIMIT_OTP_WINDOW=600

RATE_LIMIT_PASSWORD_RESET_ENABLED=True
RATE_LIMIT_PASSWORD_RESET_ATTEMPTS=3
RATE_LIMIT_PASSWORD_RESET_WINDOW=3600
```

### Example 3: Development (Permissive)
```bash
ENABLE_RATE_LIMITING=False  # Completely disabled for testing
```

---

## Render.com Setup

1. Go to your Render dashboard
2. Navigate to Environment Variables
3. Add these variables:
   ```
   ENABLE_RATE_LIMITING=True
   RATE_LIMIT_LOGIN_ENABLED=True
   RATE_LIMIT_LOGIN_ATTEMPTS=5
   RATE_LIMIT_LOGIN_WINDOW=900
   RATE_LIMIT_REGISTRATION_ENABLED=True
   RATE_LIMIT_REGISTRATION_ATTEMPTS=3
   RATE_LIMIT_REGISTRATION_WINDOW=3600
   RATE_LIMIT_OTP_ENABLED=True
   RATE_LIMIT_OTP_ATTEMPTS=5
   RATE_LIMIT_OTP_WINDOW=600
   RATE_LIMIT_PASSWORD_RESET_ENABLED=True
   RATE_LIMIT_PASSWORD_RESET_ATTEMPTS=3
   RATE_LIMIT_PASSWORD_RESET_WINDOW=3600
   ```
4. Redeploy

---

## How It Works

### Rate Limiting Logic
1. Extract client IP from request
2. Check if IP exists in cache for that endpoint
3. If attempts < max_attempts: Allow request, increment counter
4. If attempts >= max_attempts: Return HTTP 429 (Too Many Requests)
5. Counter resets after `WINDOW` seconds

### Example Timeline
```
Time    | Attempt | Status | Cache Value
--------|---------|--------|----------
00:00   | 1       | ✅ OK  | attempts=1
00:05   | 2       | ✅ OK  | attempts=2
00:10   | 3       | ✅ OK  | attempts=3
00:15   | 4       | ✅ OK  | attempts=4
00:20   | 5       | ✅ OK  | attempts=5 (if limit=5)
00:25   | 6       | ❌ 429 | attempts=5 (window not expired)
14:50   | Reset   | ✅ OK  | attempts=0 (window expired)
```

---

## Monitoring Rate Limits

Check Django logs for rate limit hits:
```
WARNING Rate limiting exceeded for endpoint from IP: 192.168.1.1
```

Logged endpoints:
- Login rate limit exceeded: `rate_limit_login_{ip}`
- Registration rate limit exceeded: `rate_limit_registration_{ip}`
- OTP rate limit exceeded: `rate_limit_otp_{ip}`
- Password reset rate limit exceeded: `rate_limit_password_reset_{ip}`

---

## Important Notes

1. **IP-Based**: Rate limiting is per IP address, not per user
2. **Cache-Based**: Uses Django's cache (defaults to in-memory)
3. **Production Only**: Master switch is `False` by default
4. **POST Only**: Currently only limits POST requests
5. **Non-Blocking**: Rate limit errors don't log to error handlers, just warnings

---

## Troubleshooting

### Rate limit not working
1. Check `ENABLE_RATE_LIMITING=True`
2. Check specific endpoint flag is `True`
3. Verify you're making POST requests (GET requests are not limited)
4. Check IP is being detected correctly in logs

### Getting 429 too quickly
1. Lower the `*_ATTEMPTS` value
2. Lower the `*_WINDOW` value
3. Or disable that specific endpoint's rate limiting

### IP showing as 127.0.0.1 instead of real IP
- Check `X-Forwarded-For` header is being sent by reverse proxy
- Render automatically adds this, but ensure your config doesn't block it

