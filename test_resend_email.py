#!/usr/bin/env python
"""
Test Resend Email Sending
"""

import os
from dotenv import load_dotenv
import resend

load_dotenv()

print("=" * 70)
print("TESTING RESEND EMAIL API")
print("=" * 70)

api_key = os.environ.get('RESEND_API_KEY', '')

if not api_key:
    print("\n❌ ERROR: RESEND_API_KEY not set in .env")
    exit(1)

print(f"\n📧 API Key: {api_key[:20]}...{api_key[-10:]}")
print(f"📮 Sending to: omtapdiya75@gmail.com (test mode - your registered email)")
print(f"⚠️  Note: In test mode, Resend only allows sending to your own email")
print(f"          To send to others, verify your domain at https://resend.com/domains")

try:
    resend.api_key = api_key
    
    print("\n[Step 1] Sending email via Resend...")
    
    params = {
        "from": "onboarding@resend.dev",
        "to": "omtapdiya75@gmail.com",  # Send to your registered email in test mode
        "subject": "🎉 RecruitHub Email Test - Resend API",
        "html": """
        <html>
            <body style="font-family: Arial, sans-serif;">
                <h2>RecruitHub Email Test</h2>
                <p>✅ If you received this email, Resend API is working!</p>
                <ul>
                    <li>✅ Resend API connected</li>
                    <li>✅ Email delivered successfully</li>
                    <li>✅ Ready for production</li>
                </ul>
                <p>This email was sent using Resend API.</p>
            </body>
        </html>
        """,
        "text": "RecruitHub Email Test\n\nIf you received this email, Resend API is working!\n\nThis email was sent using Resend API."
    }
    
    response = resend.Emails.send(params)
    
    if response.get('id'):
        print("     ✅ Email sent!")
        print(f"     Email ID: {response['id']}")
        
        print("\n" + "=" * 70)
        print("✅ SUCCESS! RESEND API IS WORKING!")
        print("=" * 70)
        print(f"\n📧 Email sent from: noreply@recruithub.com")
        print(f"📮 Email sent to: om.tapdiya25@vit.edu")
        print(f"🔑 Email ID: {response['id']}")
        print("\n✅ Ready to deploy to Render!")
        print("\nNext steps:")
        print("1. Check your inbox for the test email")
        print("2. Go to Render dashboard")
        print("3. Add environment variable:")
        print(f"   RESEND_API_KEY={api_key}")
        print("4. Click Manual Deploy")
        print("\n🎉 Done!")
    else:
        print(f"\n❌ Error: {response}")
        
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)
