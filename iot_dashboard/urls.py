from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect
from dashboard import views as dashboard_views
from ml import urls as ml_urls

def home(request):
    return redirect('landing')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', dashboard_views.landing, name='landing'),
    path('charts/', dashboard_views.charts, name='charts'),
    path('live-data/', dashboard_views.view_live_data, name='view_live_data'),  # Add this line
    path('ml/', include(ml_urls)),
    path('api/latest/', dashboard_views.latest_sensor_data, name='latest_sensor_data'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)