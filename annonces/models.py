import os
from io import BytesIO

from django.core.files.base import ContentFile
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.urls import reverse
from django.utils import timezone
from PIL import Image

class Agence(models.Model):
    nom_agence = models.CharField(max_length=200)
    adresse = models.TextField()
    telephone = models.CharField(max_length=20)
    email = models.EmailField()
    premium_jusqu_au = models.DateField(
        null=True, blank=True,
        verbose_name="Premium jusqu'au",
        help_text="Date de fin de l'abonnement premium (mis en avant sur le site). Laisser vide si l'agence n'est pas abonnée."
    )

    def __str__(self):
        return self.nom_agence

    @property
    def est_premium(self):
        return bool(self.premium_jusqu_au and self.premium_jusqu_au >= timezone.localdate())

    class Meta:
        verbose_name = "Agence"
        verbose_name_plural = "Agences"

class Agent(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='agent')
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    telephone = models.CharField(max_length=20)
    email = models.EmailField()
    agence = models.ForeignKey(Agence, on_delete=models.CASCADE, related_name='agents')
    
    def __str__(self):
        return f"{self.prenom} {self.nom} - {self.agence.nom_agence}"
    
    class Meta:
        verbose_name = "Agent"
        verbose_name_plural = "Agents"

class Client(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='client')
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    telephone = models.CharField(max_length=20)
    email = models.EmailField()
    date_inscription = models.DateTimeField(auto_now_add=True, null=True, blank=True)  # ← Ajoute null=True
    
    def __str__(self):
        return f"{self.prenom} {self.nom}"
    
    class Meta:
        verbose_name = "Client"
        verbose_name_plural = "Clients"
        
class Categorie(models.Model):
    nom_categorie = models.CharField(max_length=100)
    
    def __str__(self):
        return self.nom_categorie
    
    class Meta:
        verbose_name = "Catégorie"
        verbose_name_plural = "Catégories"

class Bien(models.Model):
    STATUT_CHOICES = [
        ('brouillon', 'Brouillon'),
        ('publie', 'Publié'),
        ('desactive', 'Désactivé'),
    ]
    TYPE_TRANSACTION_CHOICES = [
        ('vente', 'Vente'),
        ('location', 'Location'),
    ]

    titre = models.CharField(max_length=200)
    description = models.TextField()
    prix = models.DecimalField(max_digits=12, decimal_places=0)
    localisation = models.CharField(max_length=200, help_text="Ex: Cocody, Abidjan")
    type_transaction = models.CharField(max_length=10, choices=TYPE_TRANSACTION_CHOICES, default='vente')
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='brouillon')
    surface = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(0)], help_text="Surface en m²")
    pieces = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(0)], help_text="Nombre de pièces")
    
    agence = models.ForeignKey(Agence, on_delete=models.CASCADE, related_name='biens')
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE, related_name='biens')
    categorie = models.ForeignKey(Categorie, on_delete=models.CASCADE, related_name='biens')
    
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.titre} - {self.prix} FCFA"
    
    def get_absolute_url(self):
        return reverse('detail_bien', args=[str(self.id)])
    
    class Meta:
        verbose_name = "Bien"
        verbose_name_plural = "Biens"
        ordering = ['-date_creation']

class Photo(models.Model):
    # Dimension max (en px) et qualité JPEG appliquées à l'upload pour garder
    # des pages rapides malgré les photos brutes de smartphone (4-8 Mo).
    DIMENSION_MAX = 1920
    QUALITE_JPEG = 85

    url_photo = models.ImageField(upload_to='biens/%Y/%m/%d/')
    bien = models.ForeignKey(Bien, on_delete=models.CASCADE, related_name='photos')
    est_principale = models.BooleanField(default=False)

    def __str__(self):
        return f"Photo - {self.bien.titre}"

    def save(self, *args, **kwargs):
        if self.est_principale:
            Photo.objects.filter(bien=self.bien).update(est_principale=False)
        if self.url_photo and self._state.adding:
            self._compresser_image()
        super().save(*args, **kwargs)

    def _compresser_image(self):
        image = Image.open(self.url_photo)
        image = image.convert('RGB')
        image.thumbnail((self.DIMENSION_MAX, self.DIMENSION_MAX), Image.LANCZOS)

        buffer = BytesIO()
        image.save(buffer, format='JPEG', quality=self.QUALITE_JPEG, optimize=True)

        nom_fichier = os.path.splitext(os.path.basename(self.url_photo.name))[0] + '.jpg'
        self.url_photo = ContentFile(buffer.getvalue(), name=nom_fichier)
    
    class Meta:
        verbose_name = "Photo"
        verbose_name_plural = "Photos"

class Favori(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='favoris')
    bien = models.ForeignKey(Bien, on_delete=models.CASCADE, related_name='favoris')
    date_ajout = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('client', 'bien')
        verbose_name = "Favori"
        verbose_name_plural = "Favoris"
        ordering = ['-date_ajout']

    def __str__(self):
        return f"{self.client} ♥ {self.bien.titre}"


class Demande(models.Model):
    STATUT_CHOICES = [
        ('en_attente', 'En attente'),
        ('acceptee', 'Acceptée'),
        ('refusee', 'Refusée'),
        ('annulee', 'Annulée'),
    ]
    
    date_demande = models.DateTimeField(auto_now_add=True)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='en_attente')
    message = models.TextField(blank=True, null=True)
    reponse_agent = models.TextField(blank=True, null=True, verbose_name="Réponse de l'agent")
    date_visite_souhaitee = models.DateField(null=True, blank=True)
    heure_visite_souhaitee = models.TimeField(null=True, blank=True, help_text="Heure souhaitée (entre 8h et 18h)")
    
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='demandes')
    bien = models.ForeignKey(Bien, on_delete=models.CASCADE, related_name='demandes')
    
    def __str__(self):
        return f"Demande de {self.client.prenom} {self.client.nom} - {self.bien.titre}"
    
    class Meta:
        verbose_name = "Demande"
        verbose_name_plural = "Demandes"
        ordering = ['-date_demande']


class Message(models.Model):
    demande = models.ForeignKey(Demande, on_delete=models.CASCADE, related_name='messages')
    auteur = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    contenu = models.TextField()
    date_envoi = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Message"
        verbose_name_plural = "Messages"
        ordering = ['date_envoi']

    def __str__(self):
        return f"{self.auteur.username} → demande#{self.demande_id} ({self.date_envoi:%d/%m %H:%M})"