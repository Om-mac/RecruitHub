import logging
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render

logger = logging.getLogger(__name__)

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
