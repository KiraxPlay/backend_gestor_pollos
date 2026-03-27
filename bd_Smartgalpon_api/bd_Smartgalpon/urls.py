from django.contrib import admin
from django.urls import path, include

# Grupos de rutas
api_patterns = [
    path('', include('api.urls')),
    path('ponedoras/', include('api.urlsPonedoras')),
    path('auth/', include('api.auth_urls')),
    path('reportes/', include('reportes.urls')),
]

# URLs principales
urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(api_patterns)),
]