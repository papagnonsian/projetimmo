from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('annonces.urls')),
]

# Fichiers statiques en développement
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Médias (uploads utilisateurs) toujours servis par Django en local
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)