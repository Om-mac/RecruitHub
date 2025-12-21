# ❌ Email Authentication Failed

## Issue
The Gmail app password you provided is not being accepted by Gmail's SMTP server.

Error: `5.7.8 Username and Password not accepted`

## Why This Happens

1. **App Password Expired** - Old app passwords stop working
2. **Wrong Password** - Maybe different from what was copied
3. **2-Step Verification Off** - Need this enabled for app passwords
4. **Account Locked** - Too many failed attempts

## Solution: Generate a Fresh App Password

### Step-by-Step:

1. **Go to Gmail Security**: https://myaccount.google.com/security
   - Sign in if prompted

2. **Check 2-Step Verification**:
   - Look for "2-Step Verification" section
   - If it says "OFF" or "Not set up" → Enable it first
   - Complete the phone verification

3. **Generate New App Password**:
   - Once 2-Step is enabled, go to: https://myaccount.google.com/apppasswords
   - You'll see a dropdown menu
   - Select: **Mail** and **Windows Computer**
   - Google generates a new 16-character password
   - **Copy it exactly** (Gmail shows it with spaces but that's just formatting)

4. **Use the New Password** (without spaces):
   ```bash
   python test_gmail_detailed.py omtapdiya75@gmail.com NEWPASSWORDHERE
   ```

---

## What the Password Should Look Like

When Gmail shows you the password, it looks like:
```
spig livh pena iqwx
```

But you use it **without spaces**:
```
spiglivhpenaiqwx
```

---

## If That Still Doesn't Work

### Option 1: Use SendGrid (Easiest Alternative)
```bash
# Sign up free at https://sendgrid.com
# Get API key
# Use in your app:
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.sendgrid.net
EMAIL_PORT=587
EMAIL_HOST_USER=apikey
EMAIL_HOST_PASSWORD=SG.xxxxxxxxxxxxx
```

### Option 2: Try Less Secure Apps
If you want to use regular Gmail password (not recommended):
1. Go to: https://myaccount.google.com/lesssecureapps
2. Enable "Less secure app access"
3. Use your regular Gmail password

⚠️ **Warning**: This is less secure. App passwords are better.

---

## Summary

**Action Needed**: Generate a new app password from https://myaccount.google.com/apppasswords

**Then**: Test with the new password using the test script

**If still failing**: Use SendGrid as backup

Let me know the new password once you generate it! 🚀
