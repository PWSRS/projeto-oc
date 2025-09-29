from django.contrib import admin
from django.urls import path, include
from controle import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("controle.urls")),
    path("", views.home, name="home"),
    path("organograma/", include("controle.urls")),
]

# Adiciona URLs para servir arquivos de mídia durante o desenvolvimento
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


handler404 = "controle.views.not_found"
