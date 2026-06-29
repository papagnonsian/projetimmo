from django.contrib import admin
from django.urls import path, re_path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('annonces.urls')),
]

# Fichiers statiques en développement
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Médias (uploads utilisateurs) : route explicite servie par Django,
# que DEBUG soit True ou False. static() de Django ne fonctionne
# qu'en DEBUG=True, ce qui empechait les images de s'afficher en
# production (pas de serveur web dedie pour /media/ sur cPanel/Passenger).
urlpatterns += [
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
]