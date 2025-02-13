from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'cadastros'

urlpatterns = [
    path('cadastro_usuario/', views.cadastro_usuario, name='cadastro_usuario'),
    path('cadastro_veiculo/',views.cadastro_veiculo, name='cadastro_veiculo'),
    path('oferta_carona/',views.oferta_carona, name='oferta_carona'),
    path('listar_caronas/',views.listar_caronas, name='listar_caronas')
]
    

