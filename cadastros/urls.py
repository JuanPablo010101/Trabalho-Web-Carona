from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'cadastros'

urlpatterns = [
    path('cadastro_usuario/', views.cadastro_usuario, name='cadastro_usuario'),
]
    

