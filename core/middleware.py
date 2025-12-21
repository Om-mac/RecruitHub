import logging
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from django.core.cache import cache
from django.utils.deprecation import MiddlewareMixin
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class RateLimitMiddleware(MiddlewareMixin):
    """Rate limiting middleware to prevent brute force attacks"""
    
    def get_client_ip(self, request):
        """Extract client IP from request"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR')
    
    def __call__(self, request):
        # Rate limit login attempts: 5 attempts per 15 minutes
        if request.path == '/accounts/login/' or request.path == '/hr/login/':
            if request.method == 'POST':
                client_ip = self.get_client_ip(request)
                cache_key = f'login_attempts_{client_ip}'
                attempts = cache.get(cache_key, 0)
                
                if attempts >= 5:
                    logger.warning(f"Rate limit exceeded for login from {client_ip}")
                    return HttpResponse(
                        'Too many login attempts. Please try again in 15 minutes.',
                        status=429
                    )
                
                cache.set(cache_key, attempts + 1, 900)  # 15 minutes
        
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
                if 'Strict-Transport-Security' not in response and not request.is_secure() == False:
                    response['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
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
        # Add additional XSS protection headers
        if isinstance(response, HttpResponse):
            response['Content-Security-Policy'] = "default-src 'self'; script-src 'self' 'unsafe-inline' cdn.jsdelivr.net; style-src 'self' 'unsafe-inline' cdn.jsdelivr.net; img-src 'self' data:; font-src 'self' cdn.jsdelivr.net;"
        return response

