from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'cadastros'

urlpatterns = [
    path('cadastro_usuario/', views.cadastro_usuario, name='cadastro_usuario'),
    path('oferta_carona/', views.oferta_carona, name='oferta_carona'),
    path('minhas_ofertas/', views.minhas_ofertas, name='minhas_ofertas'),
    path('perfil_usuario/',views.perfil_usuario,name='perfil_usuario'),
    path('editar_perfil/', views.editar_perfil, name='editar_perfil'),
    path('alterar_status_oferta/', views.alterar_status_oferta, name='alterar_status_oferta'),
    path('reservar_carona/', views.reservar_carona, name='reservar_carona'),
    path('aceita_reserva/', views.aceita_reserva, name='aceita_reserva'),
    path('minhas_reservas/', views.minhas_reservas, name='minhas_reservas'),
    path('cancelar_reserva/', views.cancelar_reserva, name='cancelar_reserva'),
   # path('finalizar_oferta/', views.finalizar_oferta, name='finalizar_oferta'),
   
]
    

