import logging
from django.http import JsonResponse
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
        
        # Security headers
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
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
