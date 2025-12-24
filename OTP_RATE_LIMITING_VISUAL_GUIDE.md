# OTP Rate Limiting - Visual Guide

## Rate Limiting Flow Diagram

### OTP Request Flow
```
┌─────────────────────────────────────────────────────────────────┐
│                   User Requests OTP                             │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
                    ┌─────────────────────┐
                    │ Check if locked out │
                    │ (5 failed attempts) │
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
                    │  Locked? (30 min)   │
                    └──────┬─────────┬────┘
                   Yes     │         │ No
                    │      │         │
                    │      └─────────▼─────────────────────┐
                    │                                       │
                    │       ┌─────────────────────────┐    │
                    │       │ Check request rate      │    │
                    │       │ (1 min between)         │    │
                    │       └──────────┬──────────────┘    │
                    │                  │                   │
                    │       ┌──────────▼──────────┐        │
                    │       │ Too soon? (< 1min)  │        │
                    │       └──────┬─────────┬────┘        │
                    │      Yes     │         │ No          │
                    │       │      │         │             │
                    │       │      └─────────▼─────────────┤
                    │       │                              │
                    │       │      ┌──────────────────┐   │
                    │       │      │ Check hourly     │   │
                    │       │      │ limit (max 5)    │   │
                    │       │      └────────┬─────────┘   │
                    │       │               │             │
                    │       │      ┌────────▼────────┐    │
                    │       │      │ Exceeded limit? │    │
                    │       │      └────┬────────┬───┘    │
                    │       │     Yes   │        │ No     │
                    │       │      │    │        │        │
                    │       │      │    │        └────────▼────┐
                    │       │      │    │                       │
                    │       │      │    │    ┌────────────────┐│
                    │       │      │    │    │ Generate OTP   ││
                    │       │      │    │    │ & Send Email   ││
                    │       │      │    │    │ Record request ││
                    │       │      │    │    └────────┬───────┘│
                    │       │      │    │             │        │
                    │       │      │    │    ┌────────▼────┐   │
                    │       │      │    │    │ Success!    │   │
                    │       │      │    │    │ Redirect to │   │
                    │       │      │    │    │ verify page │   │
                    │       │      │    │    └─────────────┘   │
                    │       │      │    │                      │
        ┌───────────┴───────┴──────┴────┴──────────────────────┘
        │
        │
        ▼
    ┌──────────────────────┐
    │ Show Error Message   │
    │ & Redirect to start  │
    └──────────────────────┘
```

### OTP Verification Flow
```
┌─────────────────────────────────────────────────────────────────┐
│                   User Submits OTP Code                         │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
                    ┌─────────────────────┐
                    │ Check if locked out │
                    │ (5 failed attempts) │
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
                    │  Locked? (30 min)   │
                    └──────┬─────────┬────┘
                   Yes     │         │ No
                    │      │         │
                    │      └─────────▼─────────────────────┐
                    │                                       │
                    │       ┌─────────────────────────┐    │
                    │       │ Check if OTP expired    │    │
                    │       │ (10 minutes)            │    │
                    │       └──────────┬──────────────┘    │
                    │                  │                   │
                    │       ┌──────────▼──────────┐        │
                    │       │ OTP Expired?        │        │
                    │       └──────┬─────────┬────┘        │
                    │      Yes     │         │ No          │
                    │       │      │         │             │
                    │       │      └─────────▼─────────────┤
                    │       │                              │
                    │       │      ┌──────────────────┐   │
                    │       │      │ Hash-Compare OTP │   │
                    │       │      │ (PBKDF2-SHA256)  │   │
                    │       │      └────────┬─────────┘   │
                    │       │               │             │
                    │       │      ┌────────▼────────┐    │
                    │       │      │ OTP Valid?      │    │
                    │       │      └────┬────────┬───┘    │
                    │       │     Yes   │        │ No     │
                    │       │      │    │        │        │
                    │       │      │    │        └────────▼────┐
                    │       │      │    │                       │
                    │       │      │    │  ┌──────────────────┐│
                    │       │      │    │  │ Record failed    ││
                    │       │      │    │  │ attempt          ││
                    │       │      │    │  │ Increment counter││
                    │       │      │    │  └────────┬─────────┘│
                    │       │      │    │           │          │
                    │       │      │    │  ┌────────▼───────┐  │
                    │       │      │    │  │ Attempts left? │  │
                    │       │      │    │  └────┬──────┬────┘  │
                    │       │      │    │   Yes │      │ No    │
                    │       │      │    │    │  │      │       │
                    │       │      │    │    │  └──────┴─────┐ │
                    │       │      │    │    │               │ │
                    │       │      │    │    │  ┌────────────▼─┤
                    │       │      │    │    │  │ Lock account ││
                    │       │      │    │    │  │ for 30 min   ││
                    │       │      │    │    │  └──────────────┘│
                    │       │      │    │    │                  │
                    │       │      │    │    └──────────────────┘
                    │       │      │    │
                    │       │      │    └──────┐
                    │       │      │           │
        ┌───────────┘       │      │           │
        │ ┌─────────────────┘      │           │
        │ │      ┌──────────────────┴──┐       │
        │ │      │                      │       │
        │ │ ┌────▼─────────────────┐  │       │
        │ │ │ Reset attempts       │  │       │
        │ │ │ Mark verified        │  │       │
        │ │ │ Redirect to next step│  │       │
        │ │ └──────────────────────┘  │       │
        │ │                           │       │
        │ │      ┌────────────────────┴──────┐
        │ │      │                           │
        │ │      ▼                           ▼
        │ │   ┌──────────────┐         ┌──────────────┐
        │ │   │ Success!     │         │ Show error & │
        │ │   │ Verified     │         │ Decrement    │
        │ └──►│ Continue     │         │ remaining    │
        │     └──────────────┘         └──────────────┘
        │
        └──────────┐
                   │
        ┌──────────▼──────────────┐
        │ Show Lock Message       │
        │ & Redirect to Start     │
        └────────────────────────┘
```

## Timeline Examples

### Example 1: Successful Flow
```
Timeline: User with valid email
──────────────────────────────────────────

10:00:00 - Request OTP
           ✓ No previous lockout
           ✓ No rate limiting
           ✓ Under hourly limit
           → OTP Sent
           
10:01:45 - Submit OTP Code
           ✓ Not expired (< 10 min)
           ✓ Not locked out
           → Verify hash
           → Match!
           → Reset failed_attempts = 0
           → Mark verified
           → Redirect to next step
```

### Example 2: Brute Force Attack
```
Timeline: Attacker trying multiple codes
─────────────────────────────────────────

10:00:00 - Request OTP → Sent
10:00:02 - Try code: 123456 → Attempt 1/5 failed
10:00:04 - Try code: 234567 → Attempt 2/5 failed
10:00:06 - Try code: 345678 → Attempt 3/5 failed
10:00:08 - Try code: 456789 → Attempt 4/5 failed
10:00:10 - Try code: 567890 → Attempt 5/5 failed
           → Account LOCKED
           → last_attempt_at = 10:00:10
           → lockout_until = 10:30:10
           
10:00:15 - Try code: 111111 → ACCOUNT LOCKED for 30 min
           → Error: "Too many failed attempts"
           
10:30:15 - Try code: 111111 → Lockout expired!
           → Can try again
           → Attempt 1/5 failed (counter resets)
```

### Example 3: Spam Attack
```
Timeline: Attacker requesting many OTPs
─────────────────────────────────────────

Window: 1 hour (10:00 - 11:00)

10:00 - Request 1 → ✓ Sent (request_count=1, last_request_at=10:00)
10:01 - Request 2 → ✓ Sent (request_count=2, last_request_at=10:01)
10:02 - Request 3 → ✓ Sent (request_count=3, last_request_at=10:02)
10:03 - Request 4 → ✓ Sent (request_count=4, last_request_at=10:03)
10:04 - Request 5 → ✓ Sent (request_count=5, last_request_at=10:04)
10:05 - Request 6 → ✗ REJECTED
        Error: "You requested 5 OTPs in the last hour"
10:10 - Request 7 → ✗ REJECTED (still within hour window)
11:05 - Request 6 → ✓ Sent (Request 1 aged out, window resets)
```

### Example 4: Rate Limited Requests
```
Timeline: User requesting OTP too quickly
──────────────────────────────────────────

10:00:00 - Request OTP → ✓ Sent
10:00:30 - Request OTP → ✗ REJECTED
           Error: "Please wait 30 seconds before requesting new OTP"
           (minimum 1 minute = 60 seconds between requests)
10:00:45 - Request OTP → ✗ REJECTED
           Error: "Please wait 15 seconds before requesting new OTP"
10:01:00 - Request OTP → ✓ Sent
           (1 minute has passed)
```

## Rate Limiting Constants Reference

```
┌───────────────────────────────────────────────────────┐
│              RATE LIMITING CONSTANTS                  │
├─────────────────────────────┬─────────┬──────────────┤
│ Constant                    │ Value   │ Purpose      │
├─────────────────────────────┼─────────┼──────────────┤
│ MAX_FAILED_ATTEMPTS         │ 5       │ Brute force  │
│                             │         │ protection   │
├─────────────────────────────┼─────────┼──────────────┤
│ ATTEMPT_LOCKOUT_MINUTES     │ 30      │ Lockout      │
│                             │         │ duration     │
├─────────────────────────────┼─────────┼──────────────┤
│ REQUEST_RATE_LIMIT_MINUTES  │ 1       │ Min time     │
│                             │         │ between req  │
├─────────────────────────────┼─────────┼──────────────┤
│ MAX_ATTEMPTS_PER_HOUR       │ 5       │ Hourly spam  │
│                             │         │ limit        │
├─────────────────────────────┼─────────┼──────────────┤
│ OTP_EXPIRATION_MINUTES      │ 10      │ OTP validity │
└─────────────────────────────┴─────────┴──────────────┘
```

## Database Field State Tracking

### Fresh OTP Request
```
EmailOTP(
    email='user@example.com',
    otp='pbkdf2_sha256$720000$...',      # Hashed with salt
    created_at='2024-12-24 10:00:00',
    is_verified=False,
    failed_attempts=0,                   # No attempts yet
    last_attempt_at=None,                # No failures yet
    last_request_at='2024-12-24 10:00:00',
    request_count=1                      # First request
)
```

### After 2 Failed Attempts
```
EmailOTP(
    email='user@example.com',
    otp='pbkdf2_sha256$720000$...',
    created_at='2024-12-24 10:00:00',
    is_verified=False,
    failed_attempts=2,                   # 2 wrong codes
    last_attempt_at='2024-12-24 10:00:15', # Last fail time
    last_request_at='2024-12-24 10:00:00',
    request_count=1
)
```

### After Successful Verification
```
EmailOTP(
    email='user@example.com',
    otp='pbkdf2_sha256$720000$...',
    created_at='2024-12-24 10:00:00',
    is_verified=True,                    # ✓ Verified
    failed_attempts=0,                   # Reset to 0
    last_attempt_at=None,                # Cleared
    last_request_at='2024-12-24 10:00:00',
    request_count=1
)
```

## Security Levels

### Green Zone (Safe)
```
✓ 0-2 failed attempts
✓ Under hourly request limit
✓ Not locked out
✓ OTP not expired
→ Normal user experience
```

### Yellow Zone (Warning)
```
⚠ 3-4 failed attempts remaining
⚠ Close to hourly limit
⚠ Rate limited on requests
→ Show remaining attempts
→ Warn about lockout
```

### Red Zone (Blocked)
```
✗ 5 failed attempts → LOCKED
✗ Exceeded hourly limit → BLOCKED
✗ Account locked for 30 min
✗ OTP expired (>10 min)
→ Show error message
→ Force restart of flow
```

---

This visual guide helps understand the multi-layered rate limiting protection!
