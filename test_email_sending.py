#!/usr/bin/env python
"""
Test Email Sending with Gmail SMTP
This script tests if emails can be sent using Gmail credentials
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

print("=" * 70)
print("TESTING EMAIL SENDING WITH GMAIL")
print("=" * 70)

# Get credentials from environment
email_user = os.environ.get('EMAIL_HOST_USER', '')
email_password = os.environ.get('EMAIL_HOST_PASSWORD', '')
email_from = os.environ.get('DEFAULT_FROM_EMAIL', '')

if not email_user or not email_password:
    print("\n❌ ERROR: Missing EMAIL_HOST_USER or EMAIL_HOST_PASSWORD in .env")
    print("\nPlease add these to .env file:")
    print("EMAIL_HOST_USER=omtapdiya.25@vit.edu")
    print("EMAIL_HOST_PASSWORD=your_16_char_app_password")
    exit(1)

print(f"\n📧 Email User: {email_user}")
print(f"🔐 Password: {'*' * 20} (hidden)")
print(f"📬 From: {email_from}")

# Test recipient - change this to your email
recipient = "omtapdiya.25@vit.edu"
print(f"📮 Sending to: {recipient}")

try:
    print("\n[Step 1] Connecting to Gmail SMTP...")
    server = smtplib.SMTP('smtp.gmail.com', 587, timeout=10)
    print("     ✅ Connected!")
    
    print("\n[Step 2] Starting TLS encryption...")
    server.starttls()
    print("     ✅ TLS started!")
    
    print("\n[Step 3] Authenticating with Gmail...")
    server.login(email_user, email_password)
    print("     ✅ Authenticated!")
    
    print("\n[Step 4] Creating email message...")
    msg = MIMEMultipart('alternative')
    msg['Subject'] = "🔴 RecruitHub Test Email - Success!"
    msg['From'] = email_from
    msg['To'] = recipient
    
    text = """
RecruitHub Email Test

If you received this email, it means:
✅ Gmail SMTP is working
✅ Credentials are correct
✅ Ready for production!

This is a test email from your local machine.
    """
    
    html = """<html><body>
    <h2>RecruitHub Email Test</h2>
    <p><strong>✅ If you received this email:</strong></p>
    <ul>
        <li>Gmail SMTP is working</li>
        <li>Credentials are correct</li>
        <li>Ready for production!</li>
    </ul>
    <p>This is a test email from your local machine.</p>
    </body></html>"""
    
    msg.attach(MIMEText(text, 'plain'))
    msg.attach(MIMEText(html, 'html'))
    
    print("     ✅ Email message created!")
    
    print("\n[Step 5] Sending email...")
    server.sendmail(email_from, recipient, msg.as_string())
    print("     ✅ Email sent!")
    
    server.quit()
    
    print("\n" + "=" * 70)
    print("✅ SUCCESS! EMAIL SENDING WORKS!")
    print("=" * 70)
    print(f"\n📧 Email sent from: {email_from}")
    print(f"📮 Email sent to: {recipient}")
    print("\n✅ Your Gmail credentials are working correctly!")
    print("✅ Ready to add to Render production!")
    print("\nNext steps:")
    print("1. Check your inbox for the test email")
    print("2. Go to Render dashboard")
    print("3. Add these environment variables:")
    print(f"   EMAIL_HOST_USER={email_user}")
    print(f"   EMAIL_HOST_PASSWORD=pcmf tajh mijy mupf")
    print(f"   DEFAULT_FROM_EMAIL={email_from}")
    print("4. Click Manual Deploy")
    print("\n🎉 Done!")
    
except smtplib.SMTPAuthenticationError as e:
    print(f"\n❌ AUTHENTICATION ERROR!")
    print(f"   {e}")
    print("\n🔍 Troubleshooting:")
    print("   1. Check if app password is correct (16 characters)")
    print("   2. Make sure you have 2-factor auth enabled on Gmail")
    print("   3. Go to https://myaccount.google.com/apppasswords")
    print("   4. Generate a new app password")
    print("   5. Update .env file with new password")
    
except smtplib.SMTPException as e:
    print(f"\n❌ SMTP ERROR: {e}")
    print("\nTroubleshooting:")
    print("   1. Check internet connection")
    print("   2. Make sure Gmail SMTP is accessible")
    print("   3. Try again in a few seconds")
    
except Exception as e:
    print(f"\n❌ ERROR: {type(e).__name__}: {e}")
    print("\nTroubleshooting:")
    print("   1. Check .env file exists")
    print("   2. Check EMAIL_HOST_USER and EMAIL_HOST_PASSWORD are set")
    print("   3. Make sure credentials are correct")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)
