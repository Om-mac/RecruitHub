"""
URL configuration for auth_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from django.contrib.auth.views import LogoutView
from django.conf import settings
from django.conf.urls.static import static
from core import error_views
from core.admin import custom_admin
from core.views import StudentLoginView

# Get admin URL path from settings (configurable via ADMIN_URL_PATH env var)
# Security: No hardcoded fallback - settings.py generates random path if not set
ADMIN_URL = getattr(settings, 'ADMIN_URL_PATH', 'admin')

urlpatterns = [
    path(f"{ADMIN_URL}/", custom_admin.urls),
    # Custom login/logout
    path('accounts/login/', StudentLoginView.as_view(), name='login'),
    path('accounts/logout/', LogoutView.as_view(), name='logout'),
    path('', include('core.urls')),
]

# Only serve media files locally in DEBUG mode
# In production, media files are served via S3 presigned URLs
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Error handlers
handler400 = error_views.error_400
handler403 = error_views.error_403
handler404 = error_views.error_404
handler500 = error_views.error_500

