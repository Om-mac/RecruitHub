# Password Reset & Change Password - Setup Guide for Users

## Quick Start (For Every User)

### For Local Development (Testing)
1. **No setup needed!** The system automatically uses console email backend
2. Password reset emails appear in terminal
3. Perfect for testing the UI and flow

### For Production (Real Emails)

#### Step 1: Prepare Email Credentials

**Option A: Gmail (Recommended)**
1. Go to https://myaccount.google.com/security
2. Enable 2-Step Verification
3. Click "App passwords"
4. Select Mail → Windows Computer
5. Copy the 16-character password

**Option B: SendGrid**
1. Sign up at https://sendgrid.com
2. Create API key
3. Use API key as password

**Option C: Other SMTP Providers**
- Mailgun, AWS SES, Microsoft 365, etc.
- Get SMTP host, port, username, password from provider

#### Step 2: Configure Environment Variables

**On Your Server / Hosting Platform:**

For **Render.com** (recommended):
1. Go to your service Dashboard
2. Settings → Environment
3. Add these variables:
   ```
   EMAIL_HOST_USER=your-email@gmail.com
   EMAIL_HOST_PASSWORD=your-app-password
   DEFAULT_FROM_EMAIL=noreply@yourdomain.com
   EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
   ```

For **Heroku**:
```bash
heroku config:set EMAIL_HOST_USER=your-email@gmail.com
heroku config:set EMAIL_HOST_PASSWORD=your-app-password
heroku config:set DEFAULT_FROM_EMAIL=noreply@yourdomain.com
heroku config:set EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
```

For **Local .env file**:
```bash
# Create file: .env in project root
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=noreply@yourdomain.com
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
```

#### Step 3: Test Email Configuration

Run the test script:
```bash
cd /path/to/Authentication
source .venv/bin/activate
python send_test_email.py
```

Or send to specific email:
```bash
python send_test_email.py your-email@example.com
```

✅ If successful: Email will be sent to your inbox

#### Step 4: Deploy & Test

1. Push code to GitHub
2. Set environment variables on hosting platform
3. Deploy your application
4. Test password reset feature:
   - Go to login page
   - Click "Forgot Password?"
   - Enter registered email
   - Check email for reset link
   - Click link and set new password

---

## What Your Users Can Do

### Student/User Features

**🔐 Forgot Password:**
1. Go to login page
2. Click "Forgot Password?"
3. Enter email address
4. Check email for reset link
5. Click link and create new password
6. Login with new password

**🔑 Change Password:**
1. Login to your account
2. Click "Change Password" in navbar
3. Enter current password
4. Enter new password (min 8 characters)
5. Confirm new password
6. Click "Change Password"

---

## Email Configuration Details

### Console Backend (Development Only)
- **How it works**: Prints emails to terminal/console
- **When to use**: Local development, testing
- **Setup time**: 0 minutes (automatic)
- **Real emails sent**: No

### SMTP Backend (Production)
- **How it works**: Sends real emails via SMTP server
- **When to use**: Production, live website
- **Setup time**: 5-10 minutes
- **Real emails sent**: Yes

### Default Values in Code

```python
# Development (Console Backend)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
DEFAULT_FROM_EMAIL = 'noreply@recruithub.com'

# Production (SMTP Backend - override with environment variables)
EMAIL_BACKEND = os.environ.get('EMAIL_BACKEND', 'django.core.mail.backends.console.EmailBackend')
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'noreply@recruithub.com')
```

---

## Troubleshooting

### Emails not sending?

**1. Check environment variables are set:**
```bash
# On your hosting platform, verify these are configured:
echo $EMAIL_HOST_USER
echo $EMAIL_HOST_PASSWORD
echo $EMAIL_BACKEND
```

**2. Check Gmail app password:**
- Is 2-Step Verification enabled? ✓
- Did you use App Password (not regular password)? ✓
- Is the password 16 characters? ✓

**3. Test locally:**
```bash
python send_test_email.py your-email@example.com
```

**4. Check server logs:**
- Render: View logs in dashboard
- Heroku: `heroku logs --tail`
- Your server: Check application logs

### Common Errors

| Error | Solution |
|-------|----------|
| `SMTPAuthenticationError` | Wrong email/password - verify credentials |
| `SMTPServerDisconnected` | Internet connection issue |
| `Connection refused` | Wrong SMTP host/port |
| `SMTPException` | Email backend not configured |

---

## Security Best Practices

✅ **DO:**
- Use Gmail App Password, not regular password
- Enable 2-Step Verification on Gmail
- Store credentials in environment variables
- Never commit .env file to GitHub
- Use HTTPS for your website
- Set strong passwords (min 8 characters)

❌ **DON'T:**
- Don't hardcode credentials in code
- Don't use regular Gmail password
- Don't share app passwords
- Don't store credentials in .env on GitHub
- Don't use HTTP for password reset

---

## Implementation Notes

### How Password Reset Works

1. User requests password reset
2. System generates unique token (valid 24 hours)
3. Email sent with reset link containing token
4. User clicks link and verifies token
5. User sets new password
6. Password updated, user can login

### Security Features

✅ Tokens expire after 24 hours
✅ One-time use tokens
✅ CSRF protection on all forms
✅ Password strength validation
✅ Confirmation password matching
✅ Old password verification

---

## Environment Variable Reference

### Required for Production
```bash
EMAIL_HOST_USER          # Your email address (sender)
EMAIL_HOST_PASSWORD      # App password or SMTP password
DEFAULT_FROM_EMAIL       # Display name in emails
EMAIL_BACKEND            # django.core.mail.backends.smtp.EmailBackend
```

### Optional
```bash
EMAIL_HOST               # Default: smtp.gmail.com
EMAIL_PORT               # Default: 587
EMAIL_USE_TLS            # Default: True
```

### Optional (Other Providers)
```bash
# For SendGrid
EMAIL_HOST=smtp.sendgrid.net
EMAIL_HOST_USER=apikey
EMAIL_HOST_PASSWORD=SG.xxxxxxxxxxxxx

# For Mailgun
EMAIL_HOST=smtp.mailgun.org
EMAIL_HOST_USER=postmaster@yourdomain.com
EMAIL_HOST_PASSWORD=your-api-key
```

---

## File Structure

```
Authentication/
├── .env.example              # Template for environment variables
├── .env                      # Your actual credentials (NOT in git)
├── send_test_email.py        # Email testing script
├── requirements.txt          # Python dependencies (includes python-dotenv)
├── auth_project/
│   ├── settings.py           # Auto-loads .env file
│   └── urls.py
├── core/
│   ├── forms.py              # Password reset forms
│   ├── views.py              # Password reset views
│   ├── urls.py               # Password reset routes
│   └── templates/core/
│       ├── password_reset.html
│       ├── password_reset_done.html
│       ├── password_reset_confirm.html
│       ├── change_password.html
│       └── password_change_done.html
```

---

## Testing Checklist

- [ ] Run locally - console emails work
- [ ] Test forgot password flow
- [ ] Test change password flow
- [ ] Test with invalid email
- [ ] Test with short password (< 8 chars)
- [ ] Test password mismatch
- [ ] Deploy to production
- [ ] Set email environment variables
- [ ] Test real email sends
- [ ] Verify email content is correct
- [ ] Test password reset via email link
- [ ] Test login with new password

---

## Support

**Documentation Files:**
- `PASSWORD_RESET_IMPLEMENTATION.md` - Technical details
- `PASSWORD_RESET_USER_GUIDE.md` - User instructions
- `DEPLOYMENT_READY_PASSWORD_RESET.md` - Deployment checklist

**Quick Links:**
- Email Test Script: `send_test_email.py`
- Environment Template: `.env.example`
- Django Settings: `auth_project/settings.py`

---

## ✅ Ready to Deploy!

Your password reset system is complete and production-ready. Just:
1. Copy `.env.example` to `.env`
2. Add your email credentials
3. Run `python send_test_email.py` to verify
4. Deploy with environment variables configured
5. Users can immediately reset/change passwords!
