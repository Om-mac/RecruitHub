# OTP Rate Limiting Implementation

## Overview
Rate limiting has been implemented to protect against brute force attacks and abuse of the OTP system. Multiple layers of protection are in place.

## Rate Limiting Tiers

### 1. Attempt-Based Lockout
**Purpose**: Prevent brute force attacks on OTP verification

- **Max Failed Attempts**: 5
- **Lockout Duration**: 30 minutes
- **Applies To**: OTP verification attempts

**Behavior**:
```
Attempt 1: Invalid OTP → 4 attempts remaining
Attempt 2: Invalid OTP → 3 attempts remaining
Attempt 3: Invalid OTP → 2 attempts remaining
Attempt 4: Invalid OTP → 1 attempt remaining
Attempt 5: Invalid OTP → Account locked for 30 minutes
```

### 2. Request Rate Limiting (Per Request)
**Purpose**: Prevent rapid OTP request spam

- **Min Time Between Requests**: 1 minute
- **Applied To**: OTP generation/sending

**Behavior**:
- User requests OTP at 10:00 AM
- User tries to request again at 10:00:30 AM → Rejected
- Message: "Please wait X seconds before requesting a new OTP"
- User can request again at 10:01 AM

### 3. Hourly Request Limit
**Purpose**: Prevent excessive OTP requests in a time window

- **Max Requests Per Hour**: 5
- **Time Window**: Sliding 1-hour window
- **Applied To**: OTP generation/sending

**Behavior**:
```
10:00 AM: Request 1 → OTP sent
10:05 AM: Request 2 → OTP sent
10:10 AM: Request 3 → OTP sent
10:15 AM: Request 4 → OTP sent
10:20 AM: Request 5 → OTP sent
10:25 AM: Request 6 → Rejected
         Message: "You have requested 5 OTPs in the last hour. Please try again later."
11:00 AM: Request 6 → OTP sent (first request moved out of window)
```

## Model Methods

### EmailOTP Methods

#### `is_locked_out()`
```python
def is_locked_out(self):
    """Check if email is locked out due to too many failed attempts"""
    # Returns True if:
    # - Failed attempts >= 5 AND
    # - Less than 30 minutes have passed since last attempt
    # Returns False if lockout period has expired
```

**Returns**: `True` (locked out) / `False` (can retry)

#### `can_request_otp()`
```python
def can_request_otp(self):
    """Check if email can request a new OTP (rate limiting)"""
    # Checks if at least 1 minute has passed since last request
    # Returns: (can_request: bool, wait_time_in_seconds: int)
```

**Returns**: 
- `(True, 0)` - Can request immediately
- `(False, 45)` - Must wait 45 seconds

#### `get_hourly_request_count()`
```python
def get_hourly_request_count(self):
    """Get number of OTP requests in the last hour"""
    # Counts requests made within the last 60 minutes
    # Resets counter if last request was older than 1 hour
```

**Returns**: Integer (0-5 typically, can be higher if tracking needed)

#### `record_failed_attempt()`
```python
def record_failed_attempt(self):
    """Record a failed verification attempt and update lockout time"""
    # Increments failed_attempts counter
    # Updates last_attempt_at timestamp
    # Saves to database
```

#### `reset_failed_attempts()`
```python
def reset_failed_attempts(self):
    """Reset failed attempts after successful verification"""
    # Sets failed_attempts to 0
    # Clears last_attempt_at timestamp
    # Saves to database
```

#### `record_otp_request()`
```python
def record_otp_request(self):
    """Record an OTP request for rate limiting"""
    # Increments request_count
    # Updates last_request_at timestamp
    # Resets counter if outside 1-hour window
    # Saves to database
```

## Database Fields

### New Fields in EmailOTP Model

| Field | Type | Purpose |
|-------|------|---------|
| `last_attempt_at` | DateTimeField | Tracks when last failed OTP verification attempt occurred |
| `last_request_at` | DateTimeField | Tracks when last OTP was requested |
| `request_count` | IntegerField | Counts OTP requests in current hourly window |
| `failed_attempts` | IntegerField | Counts failed OTP verification attempts |

### Constants in EmailOTP Model

```python
MAX_FAILED_ATTEMPTS = 5
MAX_ATTEMPTS_PER_HOUR = 5
ATTEMPT_LOCKOUT_MINUTES = 30
REQUEST_RATE_LIMIT_MINUTES = 1
```

## Implementation in Views

### OTP Request Flow
```
1. User submits email for OTP
   ↓
2. Check if user is locked out (from previous failed attempts)
   - If locked out → Reject with message showing remaining time
   ↓
3. Check rate limit (1 minute between requests)
   - If too soon → Reject with message showing wait time
   ↓
4. Check hourly limit (max 5 requests per hour)
   - If exceeded → Reject with message
   ↓
5. Generate and send OTP
   ↓
6. Record OTP request with timestamp
```

### OTP Verification Flow
```
1. User submits OTP code
   ↓
2. Check if locked out
   - If locked → Reject verification
   ↓
3. Check if OTP expired (10 minutes)
   - If expired → Reject verification
   ↓
4. Verify OTP hash
   - If valid → Mark verified, reset failed attempts, allow continuation
   - If invalid → Record failed attempt, show remaining attempts
            → If 5 attempts reached → Lock account for 30 minutes
```

## Updated Views

### Functions with Rate Limiting

1. **hr_register_step1_email()**
   - Checks lockout status
   - Checks request rate limit
   - Checks hourly request limit
   - Records OTP request

2. **hr_register_step2_verify_otp()**
   - Checks lockout status before verification
   - Records failed attempts with timestamp
   - Resets attempts on successful verification

3. **password_reset_request()**
   - Same rate limiting as HR registration email step
   - Protects password reset flow

4. **password_reset_verify_otp()**
   - Same verification rate limiting as HR registration OTP step

## Security Benefits

1. **Brute Force Protection**: 5 attempts max, then 30-minute lockout
2. **Spam Prevention**: Max 5 OTP requests per hour
3. **Request Throttling**: 1-minute minimum between requests
4. **Escalating Penalties**: Lockout duration prevents rapid retry attacks
5. **Time-Based Reset**: Automatic unlocking after timeout

## Error Messages Shown to Users

### During OTP Request
- "Too many failed attempts. Please try again in X minutes."
- "Please wait X seconds before requesting a new OTP."
- "You have requested 5 OTPs in the last hour. Please try again later."

### During OTP Verification
- "Invalid OTP. X attempts remaining."
- "Too many failed attempts. Account locked for 30 minutes."
- "OTP has expired. Please request a new one."

## Admin Management

### View Rate Limit Status
```python
from core.models import EmailOTP

otp = EmailOTP.objects.get(email='user@example.com')
print(f"Failed attempts: {otp.failed_attempts}")
print(f"Locked out: {otp.is_locked_out()}")
print(f"Hourly requests: {otp.get_hourly_request_count()}")
print(f"Can request: {otp.can_request_otp()}")
```

### Reset Rate Limiting for a User
```python
from core.models import EmailOTP

otp = EmailOTP.objects.get(email='user@example.com')
otp.reset_failed_attempts()
otp.last_request_at = None
otp.request_count = 0
otp.save()
```

### Clear All Rate Limiting
```python
from core.models import EmailOTP

EmailOTP.objects.all().update(
    failed_attempts=0,
    last_attempt_at=None,
    last_request_at=None,
    request_count=0
)
```

## Monitoring and Logging

Consider adding these for production:

```python
# In views.py - Log suspicious activity
import logging

logger = logging.getLogger('otp_security')

# After lockout
logger.warning(f'OTP brute force attempt detected for {email}')

# After hourly limit exceeded
logger.warning(f'OTP rate limit exceeded for {email}')
```

## Testing Rate Limiting

### Test Lockout
```bash
1. Request OTP for test@example.com
2. Verify OTP with 5 invalid attempts
3. Verify locked out with message showing 30-minute lockout
4. Wait 30 minutes (or modify database for testing)
5. Verify can request new OTP
```

### Test Request Rate Limit
```bash
1. Request OTP at 10:00:00
2. Try to request again at 10:00:30 → Should be rejected
3. Try again at 10:01:00 → Should be accepted
```

### Test Hourly Limit
```bash
1. Request 5 OTPs with 1-minute intervals
2. Try 6th request within the hour → Should be rejected
3. Wait for oldest request to exit the hour window
4. Try again → Should be accepted
```

## Future Enhancements

1. **IP-Based Rate Limiting**: Limit requests per IP address
2. **Progressive Delays**: Increase wait time with each violation
3. **CAPTCHA Integration**: Require CAPTCHA after 3 failed attempts
4. **Email Notifications**: Alert user when suspicious activity detected
5. **Admin Dashboard**: Display rate limiting statistics
6. **Configurable Limits**: Allow admin to adjust limits via settings
7. **Permanent Blocking**: Option to permanently block problematic IPs/emails

## Deployment Notes

1. Migration applied: `core/migrations/0011_*`
2. All existing OTP records will have rate limiting fields initialized to 0/null
3. No existing data loss
4. Rate limiting is transparent to users until they exceed limits
5. System logs should monitor for repeated rate limit violations

## Compatibility

- Django 4.2+
- All databases (SQLite, PostgreSQL, MySQL)
- No external dependencies required
- Uses Django built-in datetime utilities
