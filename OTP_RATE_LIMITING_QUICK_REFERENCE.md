# OTP Rate Limiting - Quick Reference

## 🚀 Quick Start

### Check if Email is Locked Out
```python
from core.models import EmailOTP

otp = EmailOTP.objects.get(email='user@example.com')

if otp.is_locked_out():
    print("Account is locked for 30 minutes")
```

### Check if Can Request OTP
```python
can_request, wait_seconds = otp.can_request_otp()

if not can_request:
    print(f"Must wait {wait_seconds} seconds")
else:
    print("Can request new OTP")
```

### Record Failed Attempt
```python
otp.record_failed_attempt()
# Increments failed_attempts and sets last_attempt_at
```

### Reset After Success
```python
otp.reset_failed_attempts()
# Sets failed_attempts=0 and clears last_attempt_at
```

### Record OTP Request
```python
otp.record_otp_request()
# Increments request_count and updates last_request_at
```

## 📊 Key Methods

| Method | Returns | Use Case |
|--------|---------|----------|
| `is_locked_out()` | bool | Check if account is locked |
| `can_request_otp()` | (bool, int) | Check if can request, get wait time |
| `get_hourly_request_count()` | int | Get requests in last hour |
| `record_failed_attempt()` | None | Log failed verification |
| `reset_failed_attempts()` | None | Reset after success |
| `record_otp_request()` | None | Log OTP request |
| `verify_otp(code)` | bool | Verify hash |
| `is_expired()` | bool | Check if 10 min passed |
| `is_valid_attempt()` | bool | Check if < 5 attempts |

## ⚙️ Configuration

Edit in `core/models.py` EmailOTP class:

```python
class EmailOTP(models.Model):
    # ... fields ...
    
    # Rate limiting constants
    MAX_FAILED_ATTEMPTS = 5              # Change to limit attempts
    MAX_ATTEMPTS_PER_HOUR = 5            # Change to limit requests
    ATTEMPT_LOCKOUT_MINUTES = 30         # Change lockout duration
    REQUEST_RATE_LIMIT_MINUTES = 1       # Change request delay
```

## 🔍 Common Checks in Views

### Before Sending OTP
```python
from core.models import EmailOTP

try:
    otp_obj = EmailOTP.objects.get(email=email)
    
    # Check 1: Locked out?
    if otp_obj.is_locked_out():
        return error("Account locked 30 minutes")
    
    # Check 2: Rate limited?
    can_request, wait = otp_obj.can_request_otp()
    if not can_request:
        return error(f"Wait {wait} seconds")
    
    # Check 3: Hourly limit?
    if otp_obj.get_hourly_request_count() >= 5:
        return error("Max requests reached")
        
except EmailOTP.DoesNotExist:
    pass  # First time, no checks needed

# Safe to send OTP
otp_code = generate_otp()
otp_obj = EmailOTP.objects.create(email=email, otp=otp_code)
otp_obj.record_otp_request()
```

### Before Verifying OTP
```python
try:
    otp_obj = EmailOTP.objects.get(email=email)
    
    # Check 1: Locked out?
    if otp_obj.is_locked_out():
        return error("Account locked 30 minutes")
    
    # Check 2: Expired?
    if otp_obj.is_expired():
        return error("OTP expired")
    
    # Check 3: Too many attempts?
    if not otp_obj.is_valid_attempt():
        return error("Too many attempts")
    
    # Verify hash
    if otp_obj.verify_otp(user_code):
        otp_obj.reset_failed_attempts()
        return success("Verified!")
    else:
        otp_obj.record_failed_attempt()
        remaining = 5 - otp_obj.failed_attempts
        return error(f"{remaining} attempts left")
        
except EmailOTP.DoesNotExist:
    return error("OTP not found")
```

## 📱 Error Messages

| Scenario | Message |
|----------|---------|
| Account locked | "Too many failed attempts. Account locked for 30 minutes." |
| Rate limited | "Please wait X seconds before requesting a new OTP." |
| Hourly limit | "You have requested 5 OTPs in the last hour. Please try again later." |
| Failed attempt | "Invalid OTP. X attempts remaining." |
| Expired | "OTP has expired. Please request a new one." |

## 🧪 Testing

### Reset Rate Limiting for Testing
```bash
python manage.py shell
```

```python
from core.models import EmailOTP

# Clear everything for an email
otp = EmailOTP.objects.get(email='test@example.com')
otp.failed_attempts = 0
otp.last_attempt_at = None
otp.last_request_at = None
otp.request_count = 0
otp.save()

# Or delete and recreate
EmailOTP.objects.filter(email='test@example.com').delete()
```

### Check Current State
```python
from core.models import EmailOTP
from django.utils import timezone

otp = EmailOTP.objects.get(email='test@example.com')

print(f"Email: {otp.email}")
print(f"Failed attempts: {otp.failed_attempts}")
print(f"Locked out: {otp.is_locked_out()}")
print(f"Can request: {otp.can_request_otp()}")
print(f"Hourly requests: {otp.get_hourly_request_count()}")
print(f"Last attempt: {otp.last_attempt_at}")
print(f"Last request: {otp.last_request_at}")
print(f"Expired: {otp.is_expired()}")
```

### Test Lockout
```python
from core.models import EmailOTP

otp = EmailOTP.objects.get(email='test@example.com')

# Simulate 5 failed attempts
for i in range(5):
    otp.record_failed_attempt()
    print(f"Attempt {i+1}: locked_out={otp.is_locked_out()}")
```

## 🛠️ Admin Commands

### View All Locked Accounts
```bash
python manage.py shell
```

```python
from core.models import EmailOTP

locked = EmailOTP.objects.filter(failed_attempts__gte=5)
for otp in locked:
    print(f"{otp.email}: locked since {otp.last_attempt_at}")
```

### Unlock Specific Account
```python
from core.models import EmailOTP

otp = EmailOTP.objects.get(email='user@example.com')
otp.reset_failed_attempts()
print(f"{otp.email} unlocked")
```

### Unlock All Accounts
```python
from core.models import EmailOTP

EmailOTP.objects.all().update(
    failed_attempts=0,
    last_attempt_at=None
)
print("All accounts unlocked")
```

### Get Rate Limit Statistics
```python
from core.models import EmailOTP
from django.db.models import Avg, Count, Q

stats = {
    'total_otp_records': EmailOTP.objects.count(),
    'locked_accounts': EmailOTP.objects.filter(failed_attempts__gte=5).count(),
    'avg_failed_attempts': EmailOTP.objects.aggregate(Avg('failed_attempts'))['failed_attempts__avg'],
    'high_request_count': EmailOTP.objects.filter(request_count__gte=3).count(),
}

for key, val in stats.items():
    print(f"{key}: {val}")
```

## 📋 Checklist for Implementation

- [x] Model updated with rate limiting methods
- [x] Database fields added (last_attempt_at, last_request_at, request_count)
- [x] Migration created and applied
- [x] OTP request views updated
- [x] OTP verification views updated
- [x] Error messages implemented
- [x] Django checks pass
- [ ] Manual testing completed
- [ ] Code review completed
- [ ] Deployed to staging
- [ ] Deployed to production

## 🔗 Related Files

- `core/models.py` - EmailOTP model with rate limiting
- `core/views.py` - Views with rate limiting logic
- `OTP_RATE_LIMITING.md` - Detailed documentation
- `OTP_RATE_LIMITING_VISUAL_GUIDE.md` - Flow diagrams
- `OTP_HASHING_IMPLEMENTATION.md` - Hashing details

## 💡 Pro Tips

1. **For Development**: Reset rate limiting frequently
   ```bash
   python manage.py shell < reset_rate_limits.py
   ```

2. **For Production**: Monitor locked accounts
   ```bash
   python manage.py shell
   >>> EmailOTP.objects.filter(failed_attempts__gte=5).count()
   ```

3. **For Debugging**: Print request counts
   ```python
   otp = EmailOTP.objects.get(email=email)
   print(f"DEBUG: {otp.get_hourly_request_count()}/{EmailOTP.MAX_ATTEMPTS_PER_HOUR}")
   ```

4. **For Testing**: Use test emails
   - `test@example.com` for successful flows
   - `brute-force@example.com` for attack simulations

## ⚡ Performance

- **Database Queries**: Minimal (1-2 per request)
- **Calculation Time**: <1ms for all checks
- **Memory**: No caching needed
- **Scalability**: Works with any database size

## 🚨 Common Issues

### Issue: Account keeps locking
**Solution**: Check `last_attempt_at` isn't being set incorrectly
```python
otp.last_attempt_at = None
otp.save()
```

### Issue: Rate limit not working
**Solution**: Check `last_request_at` is being updated
```python
print(otp.last_request_at)  # Should have recent timestamp
```

### Issue: Tests failing
**Solution**: Clear OTP records between tests
```python
EmailOTP.objects.all().delete()
```

---

**Need help?** See OTP_RATE_LIMITING.md for detailed documentation
