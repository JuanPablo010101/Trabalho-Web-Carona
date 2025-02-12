from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('', include('autenticacao.urls')),
    path('admin/', admin.site.urls),
    path('core/', include('core.urls')),
    path('cadastros/', include('cadastros.urls')),
]