from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls' , namespace='engorde')),
    path('api/ponedoras/', include('api.urlsPonedoras', namespace='ponedoras')),
]
