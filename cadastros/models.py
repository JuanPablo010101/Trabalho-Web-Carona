from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db.models import ProtectedError

# Gerenciador de Usuário Personalizado
class UsuarioManager(BaseUserManager):
    def create_user(self, email, nome, password=None):
        if not email:
            raise ValueError('O usuário deve ter um endereço de e-mail')
        user = self.model(email=self.normalize_email(email), nome=nome)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, nome, password=None):
        user = self.create_user(email, nome, password)
        user.is_admin = True
        user.save(using=self._db)
        return user

# Modelo de Usuário
class Usuario(AbstractBaseUser):
    nome = models.CharField(max_length=300)
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

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

# Modelo de Veículo
class Veiculo(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.PROTECT, related_name='veiculos')  # Protegido contra exclusão
    marca = models.CharField(max_length=100)
    modelo = models.CharField(max_length=100)
    placa = models.CharField(max_length=10, unique=True)
    cor = models.CharField(max_length=50)
    ano = models.PositiveIntegerField()
    capacidade = models.PositiveIntegerField()  # Quantidade máxima de passageiros (excluindo o motorista)

    def __str__(self):
        return f"{self.marca} {self.modelo} - {self.placa}"

# Modelo de Oferta de Carona
class OfertaCarona(models.Model):
    motorista = models.ForeignKey(Usuario, on_delete=models.PROTECT, related_name='ofertas')  # Protegido contra exclusão
    veiculo = models.ForeignKey(Veiculo, on_delete=models.PROTECT, related_name='caronas')  # Protegido contra exclusão
    origem = models.CharField(max_length=255)
    destino = models.CharField(max_length=255)
    data_hora = models.DateTimeField()
    descricao = models.TextField(blank=True, null=True)
    vagas = models.PositiveIntegerField()
    status = models.CharField(
        max_length=20,
        choices=[('aberta', 'Aberta'), ('encerrada', 'Encerrada'), ('cancelada', 'Cancelada')],
        default='aberta'
    )
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.origem} -> {self.destino} ({self.data_hora})"

# Modelo de Reserva de Carona
class ReservaCarona(models.Model):
    oferta = models.ForeignKey(OfertaCarona, on_delete=models.PROTECT, related_name='reservas')  # Protegido contra exclusão
    passageiro = models.ForeignKey(Usuario, on_delete=models.PROTECT, related_name='reservas')  # Protegido contra exclusão
    data_reserva = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20,
        choices=[('pendente', 'Pendente'), ('confirmada', 'Confirmada'), ('cancelada', 'Cancelada')],
        default='pendente'
    )

    class Meta:
        unique_together = ('oferta', 'passageiro')  # Evita reservas duplicadas para a mesma carona

    def __str__(self):
        return f"Reserva de {self.passageiro.nome} em {self.oferta.origem} -> {self.oferta.destino}"
