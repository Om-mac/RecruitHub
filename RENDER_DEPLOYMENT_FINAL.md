# Render Deployment: Email Configuration

Your RecruitHub authentication system is ready for production! Follow these steps to deploy:

## Step 1: Add Environment Variables to Render

1. Go to [Render Dashboard](https://dashboard.render.com)
2. Select your RecruitHub service
3. Go to **Settings** → **Environment**
4. Add these 7 environment variables:

```
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp-relay.brevo.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=<your-brevo-email>
EMAIL_HOST_PASSWORD=<your-brevo-api-key>
DEFAULT_FROM_EMAIL=noreply@recruithub.com
```

**Note**: Use the Brevo SMTP credentials provided to you. The API key and email are secret - do not commit them to GitHub.

Brevo account details:
- **Email**: 9e8291001@smtp-brevo.com
- **API Key**: Available in your Brevo dashboard → SMTP Settings


## Step 2: Deploy

- Click **Deploy** in Render dashboard (auto-deploys from GitHub main)
- Wait for build to complete (typically 3-5 minutes)

## Step 3: Test in Production

Once deployed, test these features on your production site:

### Test 1: Password Reset
```
1. Visit: https://recruithub-k435.onrender.com/forgot_password/
2. Enter your email
3. Check email for reset link
4. Click link and set new password
5. Login with new password ✅
```

### Test 2: OTP Registration
```
1. Visit: https://recruithub-k435.onrender.com/register_step1/
2. Enter a new email address
3. Check email for 6-digit OTP code
4. Enter OTP and complete registration ✅
```

### Test 3: Change Password
```
1. Login to your account
2. Click "Change Password" in navbar
3. Enter current and new password
4. Password changed successfully ✅
```

## What's Working

✅ **Email Delivery**: Brevo SMTP tested and confirmed
✅ **Password Reset**: Token-based, 24-hour expiry
✅ **OTP Registration**: 6-digit codes, 10-minute expiry, rate limiting
✅ **Change Password**: Navbar integration, authentication verified
✅ **Error Handling**: Comprehensive error pages (400, 403, 404, 500, 502, 503)

## If Tests Pass

Your RecruitHub authentication system is **production-ready**! 🚀

## Troubleshooting

If emails aren't sending in production:

1. **Check Render logs**: `Logs` tab in Render dashboard
2. **Verify environment variables are set**: Refresh Render after adding them
3. **Check EMAIL_HOST_USER and EMAIL_HOST_PASSWORD are exact**: Copy-paste from this file
4. **Restart the service**: Click "Manual Deploy" in Render dashboard

The .env file in your local directory is for development only. Production uses environment variables set in Render dashboard.
