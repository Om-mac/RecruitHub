# ✅ Email Solution Without Gmail Issues

## Problem
Gmail SMTP authentication is not working, even with valid app password.

## Solution: Use Brevo (formerly Sendinblue) - Free & Reliable

Brevo is a professional email service with a free tier perfect for your needs.

### Step 1: Sign Up (2 minutes)
1. Go to: https://www.brevo.com
2. Click "Sign up free"
3. Fill in: Email, Password, Company
4. Click create account
5. Verify email

### Step 2: Get SMTP Credentials (2 minutes)
1. Go to: https://app.brevo.com/settings/keys/api
2. Look for "SMTP" section
3. You'll see:
   - SMTP Server: `smtp-relay.brevo.com`
   - SMTP Port: `587`
   - SMTP Username: Your Brevo account email
   - SMTP Password: Generate new one (click "Generate SMTP Password")
4. Copy these values

### Step 3: Configure on Render (1 minute)
On your Render dashboard:
1. Go to Settings → Environment
2. Add these variables:
   ```
   EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
   EMAIL_HOST=smtp-relay.brevo.com
   EMAIL_PORT=587
   EMAIL_USE_TLS=True
   EMAIL_HOST_USER=your-email@vit.edu
   EMAIL_HOST_PASSWORD=your-brevo-smtp-password
   DEFAULT_FROM_EMAIL=noreply@recruithub.com
   ```
3. Deploy

### Why Brevo?
✅ Free tier: 300 emails/day  
✅ No credit card needed  
✅ Reliable SMTP  
✅ No authentication issues  
✅ Professional service  
✅ No account lockouts  

### Test Locally
Once you have Brevo credentials:

```bash
python << 'EOF'
import smtplib
from email.mime.text import MIMEText

sender = "your-brevo-email@vit.edu"
password = "your-brevo-smtp-password"
recipient = "om.tapdiya25@vit.edu"

msg = MIMEText("Test email from Brevo!")
msg['Subject'] = "RecruitHub Test"
msg['From'] = sender
msg['To'] = recipient

server = smtplib.SMTP('smtp-relay.brevo.com', 587)
server.starttls()
server.login(sender, password)
server.sendmail(sender, [recipient], msg.as_string())
server.quit()

print("✅ Email sent successfully!")
EOF
```

---

## Alternative: Mailgun (Also Good)

If you prefer Mailgun:

1. Sign up: https://www.mailgun.com
2. Free tier: 100 emails/month (sandboxed domain)
3. Or add real domain: Unlimited free emails first 3 months
4. Get SMTP credentials
5. Configure same way

---

## Complete Configuration for Brevo

**Environment Variables to Set on Render:**

```
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp-relay.brevo.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-brevo-account-email
EMAIL_HOST_PASSWORD=your-brevo-smtp-password
DEFAULT_FROM_EMAIL=noreply@recruithub.com
```

---

## What You Get

With Brevo configured:
✅ Password reset emails work
✅ OTP registration emails work
✅ User notifications work
✅ Everything is production-ready
✅ Free tier is sufficient for testing

---

## Next Steps

1. **Sign up at Brevo** (2 min): https://www.brevo.com
2. **Get SMTP credentials** (2 min)
3. **Add to Render environment** (1 min)
4. **Deploy and test** (1 min)
5. **Done!** ✅

Total time: ~6 minutes

Ready to proceed? Tell me when you have the Brevo SMTP credentials!
