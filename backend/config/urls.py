"""URL configuration for AI Car Mechanic project."""

from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include

urlpatterns = [
    path('api/chat/', include('conversations.urls')),
    path('api/upload/', include('media_uploads.urls')),
    path('api/diagnosis/', include('diagnosis.urls')),
    path('api/booking/', include('bookings.urls')),
    path('api/conversations/', include('conversations.history_urls')),
]

if settings.DEBUG and not settings.USE_S3_MEDIA:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
