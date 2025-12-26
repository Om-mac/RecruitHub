from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.views.decorators.cache import never_cache
import logging
import re

logger = logging.getLogger(__name__)


def _sanitize_path(path):
    """Sanitize path for logging - remove sensitive info and limit length"""
    if not path:
        return '[empty]'
    # Limit length to prevent log injection
    path = path[:200]
    # Remove potential sensitive query params patterns
    path = re.sub(r'(token|key|password|secret|otp|auth)[=:][^&\s]*', r'\1=[REDACTED]', path, flags=re.IGNORECASE)
    # Remove any control characters
    path = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', path)
    return path


@never_cache
def error_400(request, exception=None):
    """Handle 400 Bad Request errors"""
    logger.warning(f"400 Bad Request: {_sanitize_path(request.path)}")
    return render(request, 'errors/400.html', status=400)


@never_cache
def error_403(request, exception=None):
    """Handle 403 Forbidden errors"""
    # Log user info for security audit (without exposing in response)
    user_info = request.user.username if request.user.is_authenticated else 'anonymous'
    logger.warning(f"403 Forbidden: {_sanitize_path(request.path)} | User: {user_info}")
    return render(request, 'errors/403.html', status=403)


@never_cache
def error_404(request, exception=None):
    """Handle 404 Not Found errors"""
    logger.warning(f"404 Not Found: {_sanitize_path(request.path)}")
    # Don't pass request.path to template - security risk
    return render(request, 'errors/404.html', status=404)


@never_cache
def error_500(request):
    """Handle 500 Server errors"""
    # Log detailed error for debugging (server-side only)
    logger.error(f"500 Server Error: {_sanitize_path(request.path)}", exc_info=True)
    return render(request, 'errors/500.html', status=500)


@never_cache
def error_502(request):
    """Handle 502 Bad Gateway errors"""
    logger.error(f"502 Bad Gateway: {_sanitize_path(request.path)}")
    return render(request, 'errors/502.html', status=502)


@never_cache
def error_503(request):
    """Handle 503 Service Unavailable errors"""
    logger.error(f"503 Service Unavailable: {_sanitize_path(request.path)}")
    return render(request, 'errors/503.html', status=503)
