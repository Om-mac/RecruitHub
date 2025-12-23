"""
Custom Django email backend for Resend API
"""

from django.core.mail.backends.base import BaseEmailBackend
import resend
import logging

logger = logging.getLogger('core')


class ResendBackend(BaseEmailBackend):
    """Email backend using Resend API"""
    
    def __init__(self, fail_silently=False, **kwargs):
        super().__init__(fail_silently=fail_silently, **kwargs)
        self.api_key = None
        
    def open(self):
        """Set up Resend API key"""
        import os
        logger.info("[RESEND-OPEN] Opening Resend email backend connection...")
        
        self.api_key = os.environ.get('RESEND_API_KEY')
        logger.info(f"[RESEND-OPEN] API Key from environment: {self.api_key[:10] if self.api_key else 'NOT FOUND'}...")
        
        if not self.api_key:
            logger.error("[RESEND-OPEN] ❌ RESEND_API_KEY not set in environment variables")
            if not self.fail_silently:
                raise ValueError("RESEND_API_KEY not configured")
        
        try:
            resend.api_key = self.api_key
            logger.info("[RESEND-OPEN] ✅ Resend API key configured successfully")
        except Exception as e:
            logger.error(f"[RESEND-OPEN] ❌ Failed to configure Resend API: {str(e)}")
        
    def close(self):
        """Close connection"""
        pass
        
    def send_messages(self, email_messages):
        """Send one or more EmailMessage objects and return the number of email
        messages sent.
        """
        if not email_messages:
            return 0
            
        self.open()
        num_sent = 0
        
        for message in email_messages:
            try:
                # Prepare email data
                params = {
                    "from": "noreply@vakverse.com",  # Use verified vakverse domain
                    "to": message.to[0] if isinstance(message.to, list) else message.to,
                    "subject": message.subject,
                }
                
                # Add HTML or text body
                if message.alternatives:
                    # If there's an HTML alternative, use it
                    for content, mimetype in message.alternatives:
                        if mimetype == "text/html":
                            params["html"] = content
                            break
                    else:
                        # No HTML found, use plain text
                        params["text"] = message.body
                else:
                    params["text"] = message.body
                
                # Send via Resend
                response = resend.Emails.send(params)
                
                if response.get('id'):
                    num_sent += 1
                    logger.info(f"Email sent via Resend: {message.to}")
                else:
                    logger.error(f"Resend error: {response}")
                    if not self.fail_silently:
                        raise Exception(f"Resend API error: {response}")
                        
            except Exception as e:
                logger.error(f"Failed to send email via Resend: {str(e)}")
                if not self.fail_silently:
                    raise
                    
        self.close()
        return num_sent
