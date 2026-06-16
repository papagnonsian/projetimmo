from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import Agence, Agent, Client, Categorie, Bien, Photo, Demande

class PhotoInline(admin.TabularInline):
    model = Photo
    extra = 1

class DemandeInline(admin.TabularInline):
    model = Demande
    extra = 0
    readonly_fields = ['date_demande']

class AgentInline(admin.StackedInline):
    model = Agent
    can_delete = False
    verbose_name_plural = 'Agent'

class ClientInline(admin.StackedInline):
    model = Client
    can_delete = False
    verbose_name_plural = 'Client'

class CustomUserAdmin(UserAdmin):
    inlines = [AgentInline, ClientInline]
    list_display = ['username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active']
    list_filter = ['is_staff', 'is_active', 'date_joined']
    search_fields = ['username', 'email', 'first_name', 'last_name']

try:
    admin.site.unregister(User)
except:
    pass
admin.site.register(User, CustomUserAdmin)

@admin.register(Agence)
class AgenceAdmin(admin.ModelAdmin):
    list_display = ['nom_agence', 'telephone', 'email']
    list_display_links = ['nom_agence']
    search_fields = ['nom_agence', 'email']
    list_filter = ['nom_agence']

@admin.register(Agent)
class AgentAdmin(admin.ModelAdmin):
    list_display = ['prenom', 'nom', 'email', 'telephone', 'agence']
    list_display_links = ['prenom', 'nom']
    list_filter = ['agence']
    search_fields = ['nom', 'prenom', 'email']
    raw_id_fields = ['user']

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ['prenom', 'nom', 'email', 'telephone', 'date_inscription']
    list_display_links = ['prenom', 'nom']
    search_fields = ['nom', 'prenom', 'email']
    readonly_fields = ['date_inscription']
    raw_id_fields = ['user']

@admin.register(Categorie)
class CategorieAdmin(admin.ModelAdmin):
    list_display = ['id', 'nom_categorie']
    list_display_links = ['nom_categorie']
    search_fields = ['nom_categorie']

@admin.register(Bien)
class BienAdmin(admin.ModelAdmin):
    list_display = ['titre', 'type_transaction', 'prix', 'localisation', 'categorie', 'statut', 'agence', 'agent', 'date_creation']
    list_display_links = ['titre']
    list_filter = ['type_transaction', 'statut', 'categorie', 'agence', 'date_creation']
    search_fields = ['titre', 'description', 'localisation']
    readonly_fields = ['date_creation', 'date_modification']
    inlines = [PhotoInline, DemandeInline]

    fieldsets = (
        ('Informations principales', {
            'fields': ('titre', 'description', 'prix', 'localisation', 'type_transaction', 'surface', 'pieces')
        }),
        ('Classification', {
            'fields': ('categorie', 'statut')
        }),
        ('Agence et agent', {
            'fields': ('agence', 'agent')
        }),
        ('Dates', {
            'fields': ('date_creation', 'date_modification'),
            'classes': ('collapse',)
        }),
    )

@admin.register(Photo)
class PhotoAdmin(admin.ModelAdmin):
    list_display = ['id', 'bien', 'est_principale']
    list_display_links = ['bien']
    list_filter = ['est_principale']
    search_fields = ['bien__titre']

@admin.register(Demande)
class DemandeAdmin(admin.ModelAdmin):
    list_display = ['id', 'client', 'bien', 'date_demande', 'statut']
    list_display_links = ['client']
    list_filter = ['statut', 'date_demande']
    search_fields = ['client__nom', 'client__prenom', 'bien__titre']
    readonly_fields = ['date_demande']