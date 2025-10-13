from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect
from dashboard import views as dashboard_views  # import your dashboard views
from ml import urls as ml_urls                 # ML app urls

# Optional: redirect root '/' to landing page
def home(request):
    return redirect('landing')

urlpatterns = [
    path('admin/', admin.site.urls),

    # Landing page
    path('', dashboard_views.landing, name='landing'),

    # Charts page
    path('charts/', dashboard_views.charts, name='charts'),

    # ML app URLs
    path('ml/', include(ml_urls)),

    # API endpoint for latest sensor data
    path('api/latest/', dashboard_views.latest_sensor_data, name='latest_sensor_data'),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
