from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

# Gerenciador de Usuário Personalizado
class UsuarioManager(BaseUserManager):
    def create_user(self, email, nome, password=None):
        if not email:
            raise ValueError('O usuário deve ter um endereço de e-mail')
        user = self.model(email=self.normalize_email(email), nome=nome)
        user.set_password(password)  # Senha armazenada de forma segura
        user.save(using=self._db)
        return user

    def create_superuser(self, email, nome, password=None):
        user = self.create_user(email, nome, password)
        user.is_admin = True
        user.save(using=self._db)
        return user

# Modelo de Usuário
class Usuario(AbstractBaseUser):
    nome = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    telefone = models.CharField(max_length=20, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    profile_picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True)
    objects = UsuarioManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nome']

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    @property
    def is_staff(self):
        return self.is_admin



# Modelo de Oferta de Carona
class OfertaCarona(models.Model):
    motorista = models.ForeignKey(Usuario, on_delete=models.PROTECT, related_name='ofertas')  # Protegido contra exclusão
    origem = models.CharField(max_length=100)
    destino = models.CharField(max_length=100)
    data_hora = models.DateTimeField()  # Combina data e hora da viagem
    vagas_ofertadas = models.PositiveIntegerField(default=0)  # Valor padrão definido como 0
    descricao = models.TextField(blank=True, null=True)
    status = models.CharField(
        max_length=20,
        choices=[('aberta', 'Aberta'), ('encerrada', 'Encerrada'), ('cancelada', 'Cancelada')],
        default='aberta'
    )
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)

    def vagas_disponiveis(self):
         # Calcula as vagas restantes
        reservas = ReservaCarona.objects.filter(oferta=self).count()  # Conta as reservas para esta oferta
        vagas_restantes = self.vagas_ofertadas - reservas
        return max(vagas_restantes, 0)
    
    def __str__(self):
        return f"{self.origem} -> {self.destino} ({self.data_hora})"

# Modelo de Reserva de Carona
class ReservaCarona(models.Model):
    oferta = models.ForeignKey(OfertaCarona, on_delete=models.PROTECT, related_name='reservas')  # Protegido contra exclusão
    passageiro = models.ForeignKey(Usuario, on_delete=models.PROTECT, related_name='reservas')  # Protegido contra exclusão
    data_reserva = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20)
    def save(self, *args, **kwargs):
        # Verifica se há vagas disponíveis
        if self.oferta.vagas_disponiveis() > 0:
            super().save(*args, **kwargs)  # Salva a reserva
            # Decrementa o número de vagas na oferta de carona
            self.oferta.vagas_ofertadas -= 1
            self.oferta.save()
        else:
            raise ValueError("Não há vagas disponíveis para esta carona.")

    def __str__(self):
        return f"Reserva de {self.passageiro.nome} para a carona {self.oferta.origem} -> {self.oferta.destino}"
    class Meta:
        unique_together = ('oferta', 'passageiro')  # Evita reservas duplicadas para a mesma carona

    def __str__(self):
        return f"Reserva de {self.passageiro.nome} em {self.oferta.origem} -> {self.oferta.destino}"
