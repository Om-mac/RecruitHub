# core/utils.py
"""Utility functions for security and rate limiting"""

def get_client_ip(request):
    """
    Get client IP address from request, handling proxies
    
    Checks headers in order:
    1. X-Forwarded-For (set by proxies)
    2. X-Real-IP (set by nginx)
    3. REMOTE_ADDR (direct connection)
    
    Returns the first IP address found
    """
    # Check for X-Forwarded-For header (proxy chain, use first IP)
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
        return ip
    
    # Check for X-Real-IP header (nginx reverse proxy)
    x_real_ip = request.META.get('HTTP_X_REAL_IP')
    if x_real_ip:
        return x_real_ip
    
    # Fallback to REMOTE_ADDR
    return request.META.get('REMOTE_ADDR', '127.0.0.1')
