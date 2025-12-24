# OTP Hashing Implementation (PBKDF2-SHA256)

## Overview
The OTP (One-Time Password) storage has been updated to use PBKDF2-SHA256 hashing for enhanced security. OTPs are no longer stored in plain text.

## Changes Made

### 1. Model Updates (core/models.py)

#### Imports Added
```python
from django.contrib.auth.hashers import make_password, check_password
```

#### EmailOTP Model Changes

**Field Changes:**
- `otp` field: Changed from `CharField(max_length=6)` to `CharField(max_length=255)`
  - The increased size is necessary to store hashed values (PBKDF2-SHA256 hashes are longer)
- Added `failed_attempts` field: `IntegerField(default=0)`
  - Explicitly tracks failed verification attempts

**New Methods:**

1. **`save()` override**
   ```python
   def save(self, *args, **kwargs):
       """Hash OTP before saving using PBKDF2-SHA256"""
       if not self.otp.startswith('pbkdf2_sha256$'):
           # Only hash if not already hashed
           self.otp = make_password(self.otp)
       super().save(*args, **kwargs)
   ```
   - Automatically hashes the OTP before storing in database
   - Uses Django's default hasher: PBKDF2-SHA256
   - Includes check to prevent double-hashing

2. **`verify_otp()` method**
   ```python
   def verify_otp(self, plain_otp):
       """Verify plain OTP against stored hash"""
       return check_password(plain_otp, self.otp)
   ```
   - Securely compares plain OTP with stored hash
   - Returns True if OTP matches, False otherwise

**Updated `is_valid_attempt()` method:**
```python
def is_valid_attempt(self):
    """Check if user has too many failed attempts"""
    return self.failed_attempts < 5
```
- Now uses `failed_attempts` field instead of `attempts`

### 2. View Updates (core/views.py)

#### Updated Functions:
1. **hr_register_step2_verify_otp()**
2. **password_reset_verify_otp()** (and similar password reset functions)

**Key Changes:**
- Removed direct OTP comparison: `EmailOTP.objects.get(email=email, otp=otp_code)`
- Added secure OTP verification:
  ```python
  otp_obj = EmailOTP.objects.get(email=email)
  
  # Verify hashed OTP
  if otp_obj.verify_otp(otp_code):
      # OTP is valid
      request.session['hr_otp_verified'] = True
  else:
      # Invalid OTP - increment failed attempts
      otp_obj.failed_attempts += 1
      otp_obj.save()
  ```

### 3. Database Migration

**Migration File:** `core/migrations/0010_emailotp_failed_attempts_alter_emailotp_otp.py`

Changes applied:
- Increased `otp` field max_length from 6 to 255
- Added `failed_attempts` field with default value of 0

## Security Benefits

1. **No Plain Text Storage**: OTPs are hashed using PBKDF2-SHA256 with salting
2. **One-Way Hash**: It's computationally infeasible to derive the original OTP from the hash
3. **Salted Hashes**: Django automatically adds salt, making rainbow table attacks ineffective
4. **Multiple Iterations**: PBKDF2 uses multiple iterations (default: 720,000) to slow down brute force attacks

## PBKDF2-SHA256 Details

- **Algorithm**: PBKDF2 (Password-Based Key Derivation Function 2)
- **Hash Function**: SHA-256
- **Salt**: Automatically generated and stored with hash
- **Hash Format**: `pbkdf2_sha256$iterations$salt$hash`
- **Default Iterations**: 720,000 (as per Django settings)

Example hash format in database:
```
pbkdf2_sha256$720000$abc123def456$xyz789...
```

## OWASP Compliance

This implementation aligns with OWASP guidelines for password storage:
- Uses strong cryptographic hash function (SHA-256)
- Implements key stretching (PBKDF2 with 720,000 iterations)
- Automatic salt generation
- No reversible encryption

## Backward Compatibility

**Important**: Existing OTP entries in the database before this change will have plain text values. These will NOT work after the update.

**Action Required**:
- Clear old OTP entries before deploying:
  ```bash
  python manage.py shell
  >>> from core.models import EmailOTP
  >>> EmailOTP.objects.all().delete()
  ```

## Testing

To verify the implementation:

```python
from core.models import EmailOTP
from django.contrib.auth.hashers import check_password

# Create a test OTP
otp = EmailOTP(email='test@example.com', otp='123456')
otp.save()

# Verify it's hashed
print(otp.otp)  # Will print hashed value like: pbkdf2_sha256$720000$...

# Test verification
print(otp.verify_otp('123456'))  # True
print(otp.verify_otp('999999'))  # False
```

## Deployment Notes

1. Run migrations: `python manage.py migrate core`
2. Clear existing OTP entries or they will become invalid
3. No additional configuration needed - uses Django's default hasher
4. Users will need to request new OTPs after deployment

## Future Improvements

- Consider using Argon2 for even stronger hashing (requires `django[argon2]`)
- Implement OTP rate limiting per email
- Add optional 2FA with TOTP after email verification
