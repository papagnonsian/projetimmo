from django.urls import path
from . import views

urlpatterns = [
    # Pages publiques
    path('', views.accueil, name='accueil'),
    path('biens/', views.liste_biens, name='liste_biens'),
    path('agences-recommandees/', views.agences_recommandees, name='agences_recommandees'),
    path('agences-recommandees/<int:agence_id>/', views.biens_agence_recommandee, name='biens_agence_recommandee'),
    path('bien/<int:bien_id>/', views.detail_bien, name='detail_bien'),
    
    # Authentification
    path('inscription/', views.inscription_client, name='inscription'),
    path('inscription-agent/', views.inscription_agent, name='inscription_agent'),
    path('connexion/', views.connexion_view, name='connexion'),
    path('deconnexion/', views.deconnexion_view, name='deconnexion'),
    
    # Demandes de visite
    path('demander-visite/<int:bien_id>/', views.demander_visite, name='demander_visite'),
    
    # Espace Agent
    path('mes-biens/', views.mes_biens, name='mes_biens'),
    path('ajouter-bien/', views.ajouter_bien, name='ajouter_bien'),
    path('modifier-bien/<int:bien_id>/', views.modifier_bien, name='modifier_bien'),
    # Ajouter ces lignes dans urlpatterns
    path('definir-photo-principale/<int:bien_id>/<int:photo_id>/', views.definir_photo_principale, name='definir_photo_principale'),
    path('supprimer-photo/<int:bien_id>/<int:photo_id>/', views.supprimer_photo, name='supprimer_photo'),
    path('supprimer-bien/<int:bien_id>/', views.supprimer_bien, name='supprimer_bien'),
    path('demandes-recues/', views.demandes_recues, name='demandes_recues'),
    path('traiter-demande/<int:demande_id>/', views.traiter_demande, name='traiter_demande'),
    
    # Espace Client
    path('mes-demandes/', views.mes_demandes, name='mes_demandes'),
    path('mes-favoris/', views.mes_favoris, name='mes_favoris'),
    path('discussion/<int:demande_id>/', views.discussion, name='discussion'),
    path('abonnement-premium/', views.demander_abonnement_premium, name='demander_abonnement_premium'),
    path('favoris/toggle/<int:bien_id>/', views.toggle_favori, name='toggle_favori'),
    path('mon-profil/', views.mon_profil, name='mon_profil'),
    path('modifier-profil/', views.modifier_profil, name='modifier_profil'),
    path('supprimer-compte/', views.supprimer_compte, name='supprimer_compte'),
    
    # DASHBOARD ADMIN
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-dashboard/agences/', views.gestion_agences, name='gestion_agences'),
    path('admin-dashboard/agences/modifier/<int:agence_id>/', views.modifier_agence, name='modifier_agence'),
    path('admin-dashboard/agences/supprimer/<int:agence_id>/', views.supprimer_agence, name='supprimer_agence'),
    path('admin-dashboard/agents/', views.gestion_agents, name='gestion_agents'),
    path('admin-dashboard/clients/', views.gestion_clients, name='gestion_clients'),
    path('admin-dashboard/categories/', views.gestion_categories, name='gestion_categories'),
    path('admin-dashboard/categories/modifier/<int:categorie_id>/', views.modifier_categorie, name='modifier_categorie'),
    path('admin-dashboard/categories/supprimer/<int:categorie_id>/', views.supprimer_categorie, name='supprimer_categorie'),
    path('admin-dashboard/biens/', views.gestion_biens, name='gestion_biens'),
    path('admin-dashboard/demandes/', views.gestion_demandes, name='gestion_demandes'),
]