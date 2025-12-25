import logging
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from django.core.cache import cache
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class RateLimitMiddleware(MiddlewareMixin):
    """Rate limiting middleware to prevent brute force attacks
    
    Configure via environment variables:
    - ENABLE_RATE_LIMITING: Master switch (True/False)
    - RATE_LIMIT_LOGIN_ENABLED: Enable login rate limiting
    - RATE_LIMIT_REGISTRATION_ENABLED: Enable registration rate limiting
    - RATE_LIMIT_OTP_ENABLED: Enable OTP rate limiting
    - RATE_LIMIT_PASSWORD_RESET_ENABLED: Enable password reset rate limiting
    
    Plus: *_ATTEMPTS and *_WINDOW for each endpoint
    """
    
    def get_client_ip(self, request):
        """Extract client IP from request"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR')
    
    def check_rate_limit(self, key, max_attempts, window_seconds, request_method='POST'):
        """Check if request exceeds rate limit
        
        Args:
            key: Cache key for rate limiting
            max_attempts: Max attempts allowed
            window_seconds: Time window in seconds
            request_method: HTTP method to check ('POST', 'GET', etc.)
        
        Returns:
            (is_limited, remaining_attempts, retry_after)
        """
        if request_method != 'POST':
            return False, max_attempts, 0
        
        attempts = cache.get(key, 0)
        
        if attempts >= max_attempts:
            # Get remaining time from cache
            ttl = cache.ttl(key) if hasattr(cache, 'ttl') else window_seconds
            return True, 0, ttl or window_seconds
        
        cache.set(key, attempts + 1, window_seconds)
        return False, max_attempts - attempts - 1, 0
    
    def rate_limit_response(self, request, message, retry_after=900):
        """Return rate limit error response as HTML"""
        import time
        
        # Calculate expiration timestamp (current time + retry_after seconds)
        expires_at = time.time() + retry_after
        
        context = {
            'message': message,
            'retry_after': retry_after,
            'expires_at': expires_at,  # Unix timestamp when rate limit expires
            'redirect_url': request.META.get('HTTP_REFERER', '/'),
        }
        response = render(request, 'errors/429.html', context, status=429)
        response['Retry-After'] = str(retry_after)
        return response
    
    def __call__(self, request):
        # Only apply rate limiting if enabled
        if not getattr(settings, 'ENABLE_RATE_LIMITING', False):
            response = self.get_response(request)
            return response
        
        client_ip = self.get_client_ip(request)
        
        # ===== LOGIN RATE LIMITING =====
        if getattr(settings, 'RATE_LIMIT_LOGIN_ENABLED', False):
            if request.path in ['/accounts/login/', '/hr/login/']:
                if request.method == 'POST':
                    cache_key = f'rate_limit_login_{client_ip}'
                    is_limited, remaining, retry_after = self.check_rate_limit(
                        cache_key,
                        getattr(settings, 'RATE_LIMIT_LOGIN_ATTEMPTS', 5),
                        getattr(settings, 'RATE_LIMIT_LOGIN_WINDOW', 900)
                    )
                    
                    if is_limited:
                        logger.warning(f"Login rate limit exceeded for IP: {client_ip}")
                        return self.rate_limit_response(
                            request,
                            'Too many login attempts. Please try again later.',
                            retry_after or 900
                        )
        
        # ===== REGISTRATION RATE LIMITING =====
        if getattr(settings, 'RATE_LIMIT_REGISTRATION_ENABLED', False):
            if request.path in ['/register/', '/hr/register/']:
                if request.method == 'POST':
                    cache_key = f'rate_limit_registration_{client_ip}'
                    is_limited, remaining, retry_after = self.check_rate_limit(
                        cache_key,
                        getattr(settings, 'RATE_LIMIT_REGISTRATION_ATTEMPTS', 3),
                        getattr(settings, 'RATE_LIMIT_REGISTRATION_WINDOW', 3600)
                    )
                    
                    if is_limited:
                        logger.warning(f"Registration rate limit exceeded for IP: {client_ip}")
                        return self.rate_limit_response(
                            request,
                            'Too many registration attempts. Please try again later.',
                            retry_after or 3600
                        )
        
        # ===== OTP RATE LIMITING =====
        if getattr(settings, 'RATE_LIMIT_OTP_ENABLED', False):
            if '/verify-otp/' in request.path or '/request-otp/' in request.path:
                if request.method == 'POST':
                    cache_key = f'rate_limit_otp_{client_ip}'
                    is_limited, remaining, retry_after = self.check_rate_limit(
                        cache_key,
                        getattr(settings, 'RATE_LIMIT_OTP_ATTEMPTS', 5),
                        getattr(settings, 'RATE_LIMIT_OTP_WINDOW', 600)
                    )
                    
                    if is_limited:
                        logger.warning(f"OTP rate limit exceeded for IP: {client_ip}")
                        return self.rate_limit_response(
                            request,
                            'Too many OTP attempts. Please try again later.',
                            retry_after or 600
                        )
        
        # ===== PASSWORD RESET RATE LIMITING =====
        if getattr(settings, 'RATE_LIMIT_PASSWORD_RESET_ENABLED', False):
            if '/password-reset/' in request.path or '/forgot-password/' in request.path:
                if request.method == 'POST':
                    cache_key = f'rate_limit_password_reset_{client_ip}'
                    is_limited, remaining, retry_after = self.check_rate_limit(
                        cache_key,
                        getattr(settings, 'RATE_LIMIT_PASSWORD_RESET_ATTEMPTS', 3),
                        getattr(settings, 'RATE_LIMIT_PASSWORD_RESET_WINDOW', 3600)
                    )
                    
                    if is_limited:
                        logger.warning(f"Password reset rate limit exceeded for IP: {client_ip}")
                        return self.rate_limit_response(
                            request,
                            'Too many password reset attempts. Please try again later.',
                            retry_after or 3600
                        )
        
        response = self.get_response(request)
        return response
        
        # ===== REGISTRATION RATE LIMITING =====
        if getattr(settings, 'RATE_LIMIT_REGISTRATION_ENABLED', False):
            if request.path in ['/register/', '/hr/register/']:
                if request.method == 'POST':
                    cache_key = f'rate_limit_registration_{client_ip}'
                    is_limited, remaining = self.check_rate_limit(
                        cache_key,
                        getattr(settings, 'RATE_LIMIT_REGISTRATION_ATTEMPTS', 3),
                        getattr(settings, 'RATE_LIMIT_REGISTRATION_WINDOW', 3600)
                    )
                    
                    if is_limited:
                        logger.warning(f"Registration rate limit exceeded for IP: {client_ip}")
                        return HttpResponse(
                            'Too many registration attempts. Please try again in 1 hour.',
                            status=429
                        )
        
        # ===== OTP RATE LIMITING =====
        if getattr(settings, 'RATE_LIMIT_OTP_ENABLED', False):
            if '/verify-otp/' in request.path or '/request-otp/' in request.path:
                if request.method == 'POST':
                    cache_key = f'rate_limit_otp_{client_ip}'
                    is_limited, remaining = self.check_rate_limit(
                        cache_key,
                        getattr(settings, 'RATE_LIMIT_OTP_ATTEMPTS', 5),
                        getattr(settings, 'RATE_LIMIT_OTP_WINDOW', 600)
                    )
                    
                    if is_limited:
                        logger.warning(f"OTP rate limit exceeded for IP: {client_ip}")
                        return HttpResponse(
                            'Too many OTP attempts. Please try again in 10 minutes.',
                            status=429
                        )
        
        # ===== PASSWORD RESET RATE LIMITING =====
        if getattr(settings, 'RATE_LIMIT_PASSWORD_RESET_ENABLED', False):
            if '/password-reset/' in request.path or '/forgot-password/' in request.path:
                if request.method == 'POST':
                    cache_key = f'rate_limit_password_reset_{client_ip}'
                    is_limited, remaining = self.check_rate_limit(
                        cache_key,
                        getattr(settings, 'RATE_LIMIT_PASSWORD_RESET_ATTEMPTS', 3),
                        getattr(settings, 'RATE_LIMIT_PASSWORD_RESET_WINDOW', 3600)
                    )
                    
                    if is_limited:
                        logger.warning(f"Password reset rate limit exceeded for IP: {client_ip}")
                        return HttpResponse(
                            'Too many password reset attempts. Please try again in 1 hour.',
                            status=429
                        )
        
        response = self.get_response(request)
        return response

class ErrorHandlingMiddleware:
    """Middleware to catch and log all errors"""
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            response = self.get_response(request)
        except Exception as e:
            logger.exception(f"Unhandled exception for {request.method} {request.path}: {str(e)}")
            return render(request, 'errors/500.html', status=500)
        
        return response

class SecurityHeadersMiddleware:
    """Add security headers to all responses"""
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        # Only set security headers on proper HttpResponse objects
        if isinstance(response, HttpResponse):
            try:
                # Security headers - only set if not already set
                if 'X-Content-Type-Options' not in response:
                    response['X-Content-Type-Options'] = 'nosniff'
                if 'X-Frame-Options' not in response:
                    response['X-Frame-Options'] = 'DENY'
                if 'X-XSS-Protection' not in response:
                    response['X-XSS-Protection'] = '1; mode=block'
                if 'Referrer-Policy' not in response:
                    response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
                if 'Permissions-Policy' not in response:
                    response['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'
                # HSTS header with preload directive (required for hstspreload.org)
                if 'Strict-Transport-Security' not in response:
                    response['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains; preload'
            except (AttributeError, TypeError) as e:
                logger.debug(f"Could not set security headers: {e}")
        
        return response

class RequestLoggingMiddleware:
    """Log all requests"""
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        logger.info(f"{request.method} {request.path} from {self.get_client_ip(request)}")
        response = self.get_response(request)
        logger.info(f"Response: {response.status_code} for {request.path}")
        return response
    
    @staticmethod
    def get_client_ip(request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

class XSSProtectionMiddleware:
    """Middleware to help prevent XSS attacks"""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        response = self.get_response(request)
        # Add additional XSS protection headers with S3 and CDN support
        if isinstance(response, HttpResponse):
            response['Content-Security-Policy'] = "default-src 'self'; script-src 'self' 'unsafe-inline' cdn.jsdelivr.net cdnjs.cloudflare.com; style-src 'self' 'unsafe-inline' cdn.jsdelivr.net cdnjs.cloudflare.com; img-src 'self' data: https:; font-src 'self' cdn.jsdelivr.net cdnjs.cloudflare.com fonts.googleapis.com fonts.gstatic.com;"
        return response

