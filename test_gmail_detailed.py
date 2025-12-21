#!/usr/bin/env python
"""
Gmail Email Test - Detailed Debugging
Tests SMTP connection and email sending with verbose output
"""

import os
import sys
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def test_gmail_smtp(email_user, email_password):
    """Test Gmail SMTP connection and send email"""
    
    print("=" * 70)
    print("GMAIL SMTP CONNECTION TEST")
    print("=" * 70)
    
    # SMTP settings
    SMTP_HOST = 'smtp.gmail.com'
    SMTP_PORT = 587
    
    print(f"\n📧 Email Address: {email_user}")
    print(f"🔐 Password Length: {len(email_password)} characters")
    print(f"🌐 SMTP Host: {SMTP_HOST}")
    print(f"🔌 SMTP Port: {SMTP_PORT}")
    print(f"🔒 TLS Enabled: Yes")
    
    try:
        # Step 1: Connect to Gmail SMTP
        print("\n[1/4] Connecting to Gmail SMTP server...")
        server = smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=10)
        print("     ✅ Connected!")
        
        # Step 2: Start TLS
        print("\n[2/4] Starting TLS encryption...")
        server.starttls()
        print("     ✅ TLS started!")
        
        # Step 3: Login
        print("\n[3/4] Authenticating with Gmail...")
        server.login(email_user, email_password)
        print("     ✅ Authentication successful!")
        
        # Step 4: Send email
        print("\n[4/4] Sending test email...")
        
        sender = email_user
        recipient = 'omtapdiya75@gmail.com'
        
        # Create email
        msg = MIMEMultipart('alternative')
        msg['Subject'] = 'RecruitHub Email Test - Success!'
        msg['From'] = sender
        msg['To'] = recipient
        
        text = "This is a test email from RecruitHub.\n\nIf you received this, your email configuration is working!"
        html = """\
        <html>
          <body>
            <h2>RecruitHub Email Test</h2>
            <p>✅ Email configuration is working!</p>
            <p>Your users can now:</p>
            <ul>
              <li>Reset forgotten passwords</li>
              <li>Verify email on registration</li>
              <li>Receive password reset links</li>
            </ul>
            <p>- RecruitHub Team</p>
          </body>
        </html>
        """
        
        part1 = MIMEText(text, 'plain')
        part2 = MIMEText(html, 'html')
        msg.attach(part1)
        msg.attach(part2)
        
        # Send
        server.sendmail(sender, [recipient], msg.as_string())
        print("     ✅ Email sent successfully!")
        
        server.quit()
        
        print("\n" + "=" * 70)
        print("✅ SUCCESS! Email configuration is working!")
        print("=" * 70)
        print("\n📧 Check your inbox at: omtapdiya75@gmail.com")
        print("\n🎉 Your RecruitHub email system is ready for:")
        print("   • Password reset")
        print("   • Email verification (OTP)")
        print("   • User notifications")
        
        return True
        
    except smtplib.SMTPAuthenticationError as e:
        print(f"\n❌ AUTHENTICATION FAILED!")
        print(f"\nError: {e}")
        print("\n🔧 Troubleshooting:")
        print("   1. Verify you're using Gmail App Password (not regular password)")
        print("   2. Check 2-Step Verification is enabled: https://myaccount.google.com/security")
        print("   3. Generate new App Password:")
        print("      - Go to https://myaccount.google.com/apppasswords")
        print("      - Select Mail → Windows Computer")
        print("      - Copy the new 16-character password")
        print("   4. Re-run this test with the new password")
        return False
        
    except smtplib.SMTPException as e:
        print(f"\n❌ SMTP ERROR!")
        print(f"\nError: {e}")
        print("\n🔧 Possible causes:")
        print("   • Internet connection issue")
        print("   • Gmail server temporarily unavailable")
        print("   • Firewall blocking SMTP connection")
        print("   • Wrong SMTP host or port")
        return False
        
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR!")
        print(f"\nError: {type(e).__name__}: {e}")
        return False

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: python test_gmail_detailed.py <email> <app_password>")
        print("Example: python test_gmail_detailed.py omtapdiya75@gmail.com spiglivhpenaiqwx")
        sys.exit(1)
    
    email = sys.argv[1]
    password = sys.argv[2]
    
    test_gmail_smtp(email, password)
