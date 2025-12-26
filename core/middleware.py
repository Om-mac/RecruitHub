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
    - TRUSTED_PROXY_IPS: Comma-separated list of trusted proxy IPs (e.g., Cloudflare, Render)
    
    Plus: *_ATTEMPTS and *_WINDOW for each endpoint
    """
    
    # Cloudflare IP ranges (IPv4) - these are the only IPs that should send X-Forwarded-For
    # Source: https://www.cloudflare.com/ips/
    CLOUDFLARE_IPS = [
        '173.245.48.0/20', '103.21.244.0/22', '103.22.200.0/22', '103.31.4.0/22',
        '141.101.64.0/18', '108.162.192.0/18', '190.93.240.0/20', '188.114.96.0/20',
        '197.234.240.0/22', '198.41.128.0/17', '162.158.0.0/15', '104.16.0.0/13',
        '104.24.0.0/14', '172.64.0.0/13', '131.0.72.0/22'
    ]
    
    def is_trusted_proxy(self, ip):
        """Check if IP is from a trusted proxy (Cloudflare/Render)"""
        import ipaddress
        try:
            client_ip = ipaddress.ip_address(ip)
            # Check against Cloudflare ranges
            for cidr in self.CLOUDFLARE_IPS:
                if client_ip in ipaddress.ip_network(cidr):
                    return True
            # Check custom trusted proxies from settings
            trusted_proxies = getattr(settings, 'TRUSTED_PROXY_IPS', '').split(',')
            for proxy_ip in trusted_proxies:
                proxy_ip = proxy_ip.strip()
                if proxy_ip and ip == proxy_ip:
                    return True
        except ValueError:
            pass
        return False
    
    def get_client_ip(self, request):
        """Extract client IP from request with spoofing protection
        
        Security: Only trusts X-Forwarded-For header if request comes from
        a known trusted proxy (Cloudflare, Render). This prevents attackers
        from bypassing rate limiting by spoofing this header.
        """
        remote_addr = request.META.get('REMOTE_ADDR', '')
        
        # Only trust X-Forwarded-For if request is from a trusted proxy
        if self.is_trusted_proxy(remote_addr):
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                # Get the rightmost untrusted IP (client IP)
                # Format: client, proxy1, proxy2, ... (leftmost is original client)
                ips = [ip.strip() for ip in x_forwarded_for.split(',')]
                # Return first non-trusted IP from the left (original client)
                for ip in ips:
                    if not self.is_trusted_proxy(ip):
                        return ip
                # If all IPs are trusted (shouldn't happen), use first one
                return ips[0] if ips else remote_addr
        
        # Not from trusted proxy - use REMOTE_ADDR directly
        return remote_addr
    
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
        from urllib.parse import urlparse
        
        # Calculate expiration timestamp (current time + retry_after seconds)
        expires_at = time.time() + retry_after
        
        # Security: Validate redirect_url to prevent open redirect
        referer = request.META.get('HTTP_REFERER', '/')
        try:
            parsed = urlparse(referer)
            # Only allow same-host redirects (no external URLs)
            host = request.get_host()
            if parsed.netloc and parsed.netloc != host:
                redirect_url = '/'
            else:
                # Only keep path, strip query params for safety
                redirect_url = parsed.path or '/'
        except Exception:
            redirect_url = '/'
        
        context = {
            'message': message,
            'retry_after': retry_after,
            'expires_at': expires_at,  # Unix timestamp when rate limit expires
            'redirect_url': redirect_url,
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
    """Log all requests with sensitive data filtering"""
    
    # Patterns to redact from logged paths
    SENSITIVE_PATTERNS = ['token', 'otp', 'password', 'key', 'secret', 'auth']
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Sanitize path to remove sensitive query params
        safe_path = self.sanitize_path(request.path, request.META.get('QUERY_STRING', ''))
        logger.info(f"{request.method} {safe_path} from {self.get_client_ip(request)}")
        response = self.get_response(request)
        logger.info(f"Response: {response.status_code} for {safe_path}")
        return response
    
    def sanitize_path(self, path, query_string):
        """Remove sensitive data from path for logging"""
        if not query_string:
            return path
        
        # Parse and redact sensitive query params
        from urllib.parse import parse_qs, urlencode
        try:
            params = parse_qs(query_string, keep_blank_values=True)
            for key in params:
                if any(pattern in key.lower() for pattern in self.SENSITIVE_PATTERNS):
                    params[key] = ['[REDACTED]']
            safe_query = urlencode(params, doseq=True)
            return f"{path}?{safe_query}" if safe_query else path
        except Exception:
            return path
    
    def get_client_ip(self, request):
        """Extract client IP - use REMOTE_ADDR only (proxy-aware via RateLimitMiddleware)"""
        # For logging, we use REMOTE_ADDR to avoid log injection via X-Forwarded-For
        return request.META.get('REMOTE_ADDR', 'unknown')

class XSSProtectionMiddleware:
    """Middleware to help prevent XSS attacks"""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        response = self.get_response(request)
        # Add comprehensive CSP header with S3 and CDN support
        if isinstance(response, HttpResponse):
            # Build CSP with all security directives
            csp_directives = [
                "default-src 'self'",
                "script-src 'self' 'unsafe-inline' cdn.jsdelivr.net cdnjs.cloudflare.com",
                "style-src 'self' 'unsafe-inline' cdn.jsdelivr.net cdnjs.cloudflare.com fonts.googleapis.com",
                "img-src 'self' data: https: blob:",
                "font-src 'self' cdn.jsdelivr.net cdnjs.cloudflare.com fonts.googleapis.com fonts.gstatic.com",
                "frame-ancestors 'none'",  # Clickjacking protection (stronger than X-Frame-Options)
                "form-action 'self'",  # Prevent form submission to external sites
                "base-uri 'self'",  # Prevent base tag injection
                "object-src 'none'",  # Block Flash/plugins
                "upgrade-insecure-requests",  # Force HTTPS for all resources
            ]
            response['Content-Security-Policy'] = "; ".join(csp_directives)
        return response

