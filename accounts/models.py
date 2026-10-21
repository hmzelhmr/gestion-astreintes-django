from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.hashers import make_password
from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone 
from datetime import timedelta

# Create your models here.
class Admin(models.Model):
    username = models.CharField(max_length=100, unique=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)

    def __str__(self):
        return self.username
class Secretaire(models.Model):
    username = models.CharField(max_length=100 , unique=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)  # sera hashé

    def __str__(self):
        return self.username
    
    # 2
class Service(models.Model):
    id_service = models.AutoField(primary_key=True)
    nom_service = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nom_service
class ChefService(models.Model):
    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=100, unique=True)
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    telephone = models.CharField(max_length=20)
    password = models.CharField(max_length=255)
    must_change_password = models.BooleanField(default=True)
    service = models.OneToOneField(
        Service, on_delete=models.CASCADE, related_name="chef",
        null=True, blank=True
    )

    def __str__(self):
        return f"{self.nom} {self.prenom}"
class Collaborateur(models.Model):
    matricule = models.CharField(max_length=50, unique=True, primary_key=True)
    nom = models.CharField(max_length=150)
    prenom = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    telephone = models.CharField(max_length=20)
    service = models.ForeignKey(Service, on_delete=models.SET_NULL, null=True)
    nombre_gardes = models.PositiveIntegerField(default=0)
    added_by_content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    added_by_object_id = models.PositiveIntegerField()
    added_by = GenericForeignKey('added_by_content_type', 'added_by_object_id')

    def __str__(self):
        return f"{self.nom} {self.prenom} {self.email} {self.telephone} ({self.matricule})"
class PlanningWeekend(models.Model):
    date_debut = models.DateField()
    date_fin = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Planning du {self.date_debut} au {self.date_fin}"

    class Meta:
        unique_together = ('date_debut', 'date_fin')
class Garde(models.Model):
    planning = models.ForeignKey(PlanningWeekend, related_name="gardes", on_delete=models.CASCADE)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    collaborateur = models.ForeignKey(Collaborateur, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.service.nom_service} - {self.collaborateur.nom} {self.collaborateur.prenom}"
class ServiceCollaborateur(models.Model):
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    collaborateur = models.ForeignKey(Collaborateur, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('service', 'collaborateur')
class Indisponibilite(models.Model):
    id_indisponibilite = models.AutoField(primary_key=True)
    collaborateur = models.ForeignKey(Collaborateur, on_delete=models.CASCADE)
    date_debut = models.DateField()
    date_fin = models.DateField()
    raison = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    STATUT_CHOICES = [
        ("en_attente", "En attente"),
        ("acceptee", "Acceptée"),
        ("refusee", "Refusée"),
    ]
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default="en_attente")

    def __str__(self):
        return f"{self.collaborateur.nom} {self.collaborateur.prenom} {self.raison} ({self.date_debut} - {self.date_fin})"
class Notification(models.Model):
    FORME_CHOICES = [
        ('email', 'Email'),
        ('sms', 'SMS'),
        ('push', 'Push'),
    ]
    forme = models.CharField(max_length=10, choices=FORME_CHOICES, default='email')
    date_envoie = models.DateTimeField(null=True, blank=True)
    collaborateur = models.ForeignKey(Collaborateur, on_delete=models.SET_NULL, null=True, blank=True)
class PasswordResetCode(models.Model):
    user_email = models.EmailField()
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    role = models.CharField(max_length=20, default="admin")  # admin, secretaire, chef...

    def is_valid(self):
        return timezone.now() < self.created_at + timedelta(minutes=15)  