# 🔐 OTP Security - Implementation Quick Reference

## ✅ Implementation Status: COMPLETE

All OTP security layers are fully implemented and tested.

---

## 🎯 What Was Implemented

### Phase 1: PBKDF2-SHA256 Hashing ✅
- OTP stored as `pbkdf2_sha256$iterations$salt$hash`
- Verified using Django's `check_password()`
- Auto-hashes on model save
- **Location**: `core/models.py` EmailOTP.save() and verify_otp()

### Phase 2: Email-Based Rate Limiting ✅
- **5 failed attempts** → 30 minutes locked
- **5 OTP requests** per hour maximum  
- **1 minute throttle** between requests
- **Location**: `core/models.py` EmailOTP model and related methods

### Phase 3: IP-Based Rate Limiting ✅
- **3 attempts per minute** per IP
- **15 minutes block** after exceeding limit
- **Proxy-aware** (X-Forwarded-For, X-Real-IP support)
- **Location**: `core/models.py` IPRateLimit model + `core/utils.py`

### Phase 4: One-Time Use Deletion ✅
- OTP **deleted immediately** after successful verification
- Cannot be reused (cascading "OTP not found" error)
- **Location**: Lines 436, 745 in `core/views.py` (both main endpoints)

---

## 🛡️ Security Timeline

```
User attempts OTP verification
    ↓
Check: Is IP blocked? (3/min limit)
    ↓ Pass: Increment IP counter
Check: Is email locked? (5 failed/30 min)
    ↓ Pass: Continue to verification
Check: Is OTP expired? (10 min window)
    ↓ Pass: Verify hash
    ↓ Success: Delete OTP, reset counters
    ↓ Failure: Increment failed attempts
```

---

## 📊 Rate Limiting Config

| Limit | Duration | Action |
|-------|----------|--------|
| **IP Rate** | 3 attempts/min | 15-min auto-block |
| **Email Failed** | 5 attempts | 30-min auto-lock |
| **Email Requests** | 5 per hour | Rejection with wait time |
| **Request Throttle** | 1-min minimum | Rejection with wait time |
| **OTP Validity** | 10 minutes | Auto-expiration |

---

## 🔧 Code Locations

### Models (core/models.py)
```python
# Line 135-250: EmailOTP model
- verify_otp(plain_otp)              # Hash verification
- is_locked_out()                    # Check email lockout
- can_request_otp()                  # Check request throttle
- record_failed_attempt()            # Increment on failure
- reset_failed_attempts()            # Reset on success
- record_otp_request()               # Track request count

# Line 257-346: IPRateLimit model  
- check_rate_limit()                 # Comprehensive IP check
- increment_attempt()                # Count attempt
- is_blocked()                       # Check block status
- reset_for_ip()                     # Clear on success
```

### Views (core/views.py)
```python
# Line 314-380: hr_register_step1_email()
- Requests OTP, applies email rate limiting

# Line 386-454: hr_register_step2_verify_otp() ✅ Protected
- IP rate limiting (line 395-405)
- OTP verification (line 413-441)
- OTP deletion on success (line 436)

# Line 631-705: password_reset_request()
- Requests OTP, applies email rate limiting

# Line 695-767: password_reset_verify_otp() ✅ Protected
- IP rate limiting (line 705-715)
- OTP verification (line 723-751)
- OTP deletion on success (line 745)
```

### Utilities (core/utils.py)
```python
# get_client_ip(request)
- Extracts real IP from request
- Checks: X-Forwarded-For → X-Real-IP → REMOTE_ADDR
- Handles proxy chains correctly
```

---

## 📈 Error Messages

### Locked Out (Email)
```
"Too many failed attempts. Account locked for 30 minutes."
```

### Blocked (IP)
```
"Too many verification attempts from your IP. Please try again in 15 minutes."
```

### Throttled (Request)
```
"Please wait {wait_seconds} seconds before requesting a new OTP."
```

### Not Found (Deleted)
```
"OTP not found. Please request a new one."
```

### Expired
```
"OTP has expired. Please request a new one."
```

### Invalid
```
"Invalid OTP. {remaining} attempts remaining."
```

---

## 🚀 Production Checklist

- ✅ All endpoints protected with rate limiting
- ✅ PBKDF2-SHA256 hashing with 720K iterations
- ✅ One-time use enforcement via deletion
- ✅ Automatic time-based unlocking
- ✅ Proxy-aware IP detection
- ✅ Django system checks passing
- ✅ All migrations applied
- ✅ Database schema updated
- ✅ Error handling complete
- ✅ User messages clear

**Status**: 🎯 **PRODUCTION READY**

---

## 🧪 Quick Testing

### Test One-Time Use
1. Request OTP for test@example.com
2. Enter OTP correctly → Success ✓
3. Enter same OTP again → "OTP not found" ✓

### Test Email Lockout
1. Request OTP for test@example.com
2. Enter wrong OTP 5 times
3. Attempt #5 → Locked message ✓
4. Wait 30 minutes → Can request new OTP ✓

### Test IP Blocking
1. Verify OTP from same IP 3 times in <1 min
2. Attempt #3 → Blocked message ✓
3. Wait 15 minutes → Can verify again ✓

---

## 📚 Documentation Files

1. **OTP_SECURITY_IMPLEMENTATION_COMPLETE.md** ← Main reference
2. **OTP_ONE_TIME_USE_IMPLEMENTATION.md** ← Deletion details
3. **OTP_RATE_LIMITING.md** ← Email rate limiting
4. **IP_RATE_LIMITING.md** ← IP rate limiting
5. **OTP_HASHING_IMPLEMENTATION.md** ← Hashing details

---

## 🔄 Affected Endpoints

| Endpoint | Method | Protection |
|----------|--------|-----------|
| HR Register Step 1 | GET/POST | Email rate limiting |
| **HR Register Step 2** | GET/POST | **IP + Email + Deletion** ✅ |
| Password Reset Step 1 | GET/POST | Email rate limiting |
| **Password Reset Step 2** | GET/POST | **IP + Email + Deletion** ✅ |

---

## ⚙️ Configuration

To modify rate limits, edit `core/models.py`:

```python
# EmailOTP class
MAX_FAILED_ATTEMPTS = 5              # Change from 5
MAX_ATTEMPTS_PER_HOUR = 5            # Change from 5
ATTEMPT_LOCKOUT_MINUTES = 30         # Change from 30
REQUEST_RATE_LIMIT_MINUTES = 1       # Change from 1

# IPRateLimit class
MAX_ATTEMPTS_PER_MINUTE = 3          # Change from 3
BLOCK_DURATION_MINUTES = 15          # Change from 15
```

**Note**: No migration needed for config changes

---

## 💾 Database Impact

- **New Fields Added**: failed_attempts, last_attempt_at, last_request_at, request_count (EmailOTP)
- **New Model**: IPRateLimit (tracks per-IP attempts)
- **Migrations Applied**: 0010, 0011, 0012 (all ✅)
- **Data Deleted**: OTP records on successful verification (by design)

---

## 🎓 Key Concepts

**PBKDF2-SHA256**: 
- Password-Based Key Derivation Function 2
- Combines password + random salt + 720,000 iterations
- Makes rainbow table attacks infeasible

**Rate Limiting (Email)**:
- Focuses on user account (email)
- Prevents repeated brute force attempts
- Automatic time-based unlock

**Rate Limiting (IP)**:
- Focuses on network source (IP address)
- Prevents distributed attacks
- Blocks entire IP range for duration

**One-Time Use**:
- OTP valid for exactly one verification
- Deleted from database after success
- Cannot be reused even if intercepted

---

## 🚨 Troubleshooting

| Issue | Cause | Solution |
|-------|-------|----------|
| "OTP not found" always | User deleted OTP somehow? | Normal - request new OTP |
| Rate limit not resetting | Time window not expired | Wait for auto-reset (1, 15, or 30 min) |
| Wrong IP detected | Behind proxy | Check X-Forwarded-For header |
| Can't request OTP | Rate limited | Check email rate limiting status |

---

## ✨ Summary

Your system now has **4-layer OTP security**:

1. 🔐 **Hashing** - Secure storage
2. 📧 **Email Limits** - Per-account protection  
3. 🌐 **IP Limits** - Distributed attack prevention
4. 🗑️ **Deletion** - One-time use enforcement

**Result**: Enterprise-grade OTP security with zero tolerance for reuse.

---

*Quick Reference Guide*  
*Implementation Date: Post-Phase 4*  
*Status: ✅ COMPLETE & TESTED*
