from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.template.loader import render_to_string
import logging

logger = logging.getLogger(__name__)

def error_400(request, exception=None):
    """Handle 400 Bad Request errors"""
    logger.warning(f"400 Bad Request: {request.path}")
    return render(request, 'errors/400.html', status=400)

def error_403(request, exception=None):
    """Handle 403 Forbidden errors"""
    logger.warning(f"403 Forbidden: {request.path}")
    return render(request, 'errors/403.html', status=403)

def error_404(request, exception=None):
    """Handle 404 Not Found errors"""
    logger.warning(f"404 Not Found: {request.path}")
    return render(request, 'errors/404.html', status=404)

def error_500(request):
    """Handle 500 Server errors"""
    logger.error(f"500 Server Error: {request.path}")
    return render(request, 'errors/500.html', status=500)

def error_502(request):
    """Handle 502 Bad Gateway errors"""
    logger.error(f"502 Bad Gateway: {request.path}")
    return render(request, 'errors/502.html', status=502)

def error_503(request):
    """Handle 503 Service Unavailable errors"""
    logger.error(f"503 Service Unavailable: {request.path}")
    return render(request, 'errors/503.html', status=503)
