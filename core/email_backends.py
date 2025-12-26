"""
Custom Django email backend for Resend API
Security: API keys are never logged, email addresses are masked in logs
"""

from django.core.mail.backends.base import BaseEmailBackend
from django.conf import settings
import resend
import logging
import re

logger = logging.getLogger('core')


def mask_email(email):
    """Mask email address for safe logging: user@domain.com -> u***@d***.com"""
    if not email or '@' not in email:
        return '[invalid]'
    local, domain = email.split('@', 1)
    masked_local = local[0] + '***' if local else '***'
    domain_parts = domain.split('.')
    masked_domain = domain_parts[0][0] + '***' if domain_parts[0] else '***'
    return f"{masked_local}@{masked_domain}.{''.join(domain_parts[1:])}"


def sanitize_email_content(text):
    """Basic sanitization to prevent header injection attacks
    
    Removes newlines and carriage returns that could be used for
    email header injection attacks.
    """
    if not text:
        return text
    # Remove characters that could be used for header injection
    return re.sub(r'[\r\n]', ' ', str(text))


class ResendBackend(BaseEmailBackend):
    """Email backend using Resend API
    
    Security features:
    - API keys never logged
    - Email addresses masked in logs
    - Content sanitized against header injection
    """
    
    def __init__(self, fail_silently=False, **kwargs):
        super().__init__(fail_silently=fail_silently, **kwargs)
        self.api_key = None
        
    def open(self):
        """Set up Resend API key"""
        import os
        logger.info("[RESEND-OPEN] Opening Resend email backend connection...")
        
        self.api_key = os.environ.get('RESEND_API_KEY')
        # Security: Never log API keys, even partially
        logger.info(f"[RESEND-OPEN] API Key configured: {'YES' if self.api_key else 'NO'}")
        
        if not self.api_key:
            logger.error("[RESEND-OPEN] ❌ RESEND_API_KEY not set in environment variables")
            if not self.fail_silently:
                raise ValueError("RESEND_API_KEY not configured")
        
        try:
            resend.api_key = self.api_key
            logger.info("[RESEND-OPEN] ✅ Resend API key configured successfully")
        except Exception as e:
            # Don't log full exception which might contain key
            logger.error("[RESEND-OPEN] ❌ Failed to configure Resend API")
        
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
                # Get recipient email
                recipient = message.to[0] if isinstance(message.to, list) else message.to
                
                # Sanitize subject to prevent header injection
                safe_subject = sanitize_email_content(message.subject)
                
                # Prepare email data - use settings for from address
                params = {
                    "from": getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@vakverse.com'),
                    "to": recipient,
                    "subject": safe_subject,
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
                    # Security: Mask email in logs
                    logger.info(f"Email sent via Resend to: {mask_email(recipient)}")
                else:
                    # Security: Don't log full API response
                    logger.error(f"Resend error: Failed to send email (no ID returned)")
                    if not self.fail_silently:
                        raise Exception("Resend API error: email send failed")
                        
            except Exception as e:
                # Security: Don't expose internal error details
                logger.error(f"Failed to send email via Resend to {mask_email(recipient)}")
                if not self.fail_silently:
                    raise
                    
        self.close()
        return num_sent

