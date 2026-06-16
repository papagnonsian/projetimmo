from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.urls import reverse

class Agence(models.Model):
    nom_agence = models.CharField(max_length=200)
    adresse = models.TextField()
    telephone = models.CharField(max_length=20)
    email = models.EmailField()
    
    def __str__(self):
        return self.nom_agence
    
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
    url_photo = models.ImageField(upload_to='biens/%Y/%m/%d/')
    bien = models.ForeignKey(Bien, on_delete=models.CASCADE, related_name='photos')
    est_principale = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Photo - {self.bien.titre}"
    
    def save(self, *args, **kwargs):
        if self.est_principale:
            Photo.objects.filter(bien=self.bien).update(est_principale=False)
        super().save(*args, **kwargs)
    
    class Meta:
        verbose_name = "Photo"
        verbose_name_plural = "Photos"

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
    date_visite_souhaitee = models.DateField(null=True, blank=True)
    
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='demandes')
    bien = models.ForeignKey(Bien, on_delete=models.CASCADE, related_name='demandes')
    
    def __str__(self):
        return f"Demande de {self.client.prenom} {self.client.nom} - {self.bien.titre}"
    
    class Meta:
        verbose_name = "Demande"
        verbose_name_plural = "Demandes"
        ordering = ['-date_demande']