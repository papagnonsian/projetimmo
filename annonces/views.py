from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.contrib.auth.models import User
from django.db.models import Q, Count, Sum
from django.core.paginator import Paginator
from .models import Agence, Agent, Client, Bien, Categorie, Photo, Demande
from .forms import (
    InscriptionClientForm, InscriptionAgentForm, ConnexionForm, BienForm,
    DemandeVisiteForm, FiltreBiensForm, AgenceForm, AgentForm, CategorieForm,
    ModifierProfilClientForm
)

# Vérification admin
def is_admin(user):
    return user.is_superuser or user.is_staff

# Pages publiques
def accueil(request):
    derniers_biens = Bien.objects.filter(statut='publie').order_by('-date_creation')[:6]
    categories = Categorie.objects.annotate(nb_biens=Count('biens'))
    total_biens = Bien.objects.filter(statut='publie').count()
    total_agences = Agence.objects.count()
    
    return render(request, 'annonces/accueil.html', {
        'derniers_biens': derniers_biens,
        'categories': categories,
        'total_biens': total_biens,
        'total_agences': total_agences,
    })

def liste_biens(request):
    biens = Bien.objects.filter(statut='publie')
    form = FiltreBiensForm(request.GET or None)

    if form.is_valid():
        if form.cleaned_data.get('categorie'):
            biens = biens.filter(categorie=form.cleaned_data['categorie'])
        if form.cleaned_data.get('commune'):
            biens = biens.filter(localisation__icontains=form.cleaned_data['commune'])
        if form.cleaned_data.get('prix_min'):
            biens = biens.filter(prix__gte=form.cleaned_data['prix_min'])
        if form.cleaned_data.get('prix_max'):
            biens = biens.filter(prix__lte=form.cleaned_data['prix_max'])

    total_biens = biens.count()
    paginator = Paginator(biens, 9)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    return render(request, 'annonces/liste_biens.html', {
        'biens': page_obj,
        'page_obj': page_obj,
        'form': form,
        'total_biens': total_biens,
        'get_params': request.GET.urlencode(),
    })

def detail_bien(request, bien_id):
    bien = get_object_or_404(Bien, id=bien_id, statut='publie')
    deja_demande = False
    if request.user.is_authenticated and hasattr(request.user, 'client'):
        deja_demande = Demande.objects.filter(client=request.user.client, bien=bien).exists()
    
    return render(request, 'annonces/detail_bien.html', {
        'bien': bien,
        'photos': bien.photos.all(),
        'photo_principale': bien.photos.filter(est_principale=True).first() or bien.photos.first(),
        'demandes_form': DemandeVisiteForm(),
        'deja_demande': deja_demande,
    })

# Authentification
def inscription_client(request):
    if request.user.is_authenticated:
        return redirect('accueil')
    if request.method == 'POST':
        form = InscriptionClientForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Inscription réussie !")
            return redirect('accueil')
    else:
        form = InscriptionClientForm()
    return render(request, 'annonces/inscription.html', {'form': form})

def inscription_agent(request):
    if request.user.is_authenticated:
        return redirect('accueil')
    if request.method == 'POST':
        form = InscriptionAgentForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Agence créée avec succès !")
            return redirect('mes_biens')
    else:
        form = InscriptionAgentForm()
    return render(request, 'annonces/inscription_agent.html', {'form': form})

def connexion_view(request):
    if request.user.is_authenticated:
        return redirect('accueil')
    if request.method == 'POST':
        form = ConnexionForm(request.POST)
        if form.is_valid():
            user = authenticate(
                request,
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password']
            )
            if user:
                login(request, user)
                messages.success(request, f"Bonjour {user.username} !")
                if hasattr(user, 'agent'):
                    return redirect('mes_biens')
                return redirect('accueil')
            messages.error(request, "Identifiants incorrects.")
    else:
        form = ConnexionForm()
    return render(request, 'annonces/connexion.html', {'form': form})

def deconnexion_view(request):
    logout(request)
    messages.info(request, "Vous êtes déconnecté.")
    return redirect('accueil')

# Espace Agent
@login_required
def mes_biens(request):
    if not hasattr(request.user, 'agent'):
        messages.error(request, "Accès réservé aux agents.")
        return redirect('accueil')
    
    biens = Bien.objects.filter(agent=request.user.agent)
    return render(request, 'annonces/mes_biens.html', {
        'biens': biens,
        'total_biens': biens.count(),
        'biens_publies': biens.filter(statut='publie').count(),
        'biens_brouillon': biens.filter(statut='brouillon').count(),
    })

@login_required
def ajouter_bien(request):
    if not hasattr(request.user, 'agent'):
        messages.error(request, "Accès réservé aux agents.")
        return redirect('accueil')
    
    if request.method == 'POST':
        form = BienForm(request.POST)
        if form.is_valid():
            bien = form.save(commit=False)
            bien.agent = request.user.agent
            bien.agence = request.user.agent.agence
            bien.save()
            
            for i, photo in enumerate(request.FILES.getlist('photos')):
                Photo.objects.create(
                    url_photo=photo,
                    bien=bien,
                    est_principale=(i == 0)
                )
            messages.success(request, "Bien ajouté avec succès !")
            return redirect('mes_biens')
    else:
        form = BienForm()
    
    return render(request, 'annonces/ajouter_bien.html', {'form': form})


@login_required
def modifier_bien(request, bien_id):
    if not hasattr(request.user, 'agent'):
        messages.error(request, "Accès réservé aux agents.")
        return redirect('accueil')
    
    bien = get_object_or_404(Bien, id=bien_id, agent=request.user.agent)
    
    if request.method == 'POST':
        form = BienForm(request.POST, instance=bien)
        if form.is_valid():
            form.save()
            
            # Gestion des nouvelles photos
            photos = request.FILES.getlist('photos')
            for i, photo in enumerate(photos):
                # Si c'est la première nouvelle photo et qu'il n'y a pas de photo principale
                has_principal = Photo.objects.filter(bien=bien, est_principale=True).exists()
                Photo.objects.create(
                    url_photo=photo,
                    bien=bien,
                    est_principale=(not has_principal and i == 0)
                )
            
            messages.success(request, "Bien modifié avec succès !")
            return redirect('mes_biens')
    else:
        form = BienForm(instance=bien)
    
    return render(request, 'annonces/modifier_bien.html', {
        'form': form,
        'bien': bien,
        'photos': bien.photos.all()
    })
@login_required
def definir_photo_principale(request, bien_id, photo_id):
    """Définir une photo comme principale"""
    if not hasattr(request.user, 'agent'):
        messages.error(request, "Accès réservé aux agents.")
        return redirect('accueil')
    
    bien = get_object_or_404(Bien, id=bien_id, agent=request.user.agent)
    photo = get_object_or_404(Photo, id=photo_id, bien=bien)
    
    # Enlever le flag principale de toutes les photos du bien
    Photo.objects.filter(bien=bien).update(est_principale=False)
    
    # Définir cette photo comme principale
    photo.est_principale = True
    photo.save()
    
    messages.success(request, "Photo principale mise à jour.")
    return redirect('modifier_bien', bien_id=bien_id)

@login_required
def supprimer_photo(request, bien_id, photo_id):
    """Supprimer une photo"""
    if not hasattr(request.user, 'agent'):
        messages.error(request, "Accès réservé aux agents.")
        return redirect('accueil')
    
    bien = get_object_or_404(Bien, id=bien_id, agent=request.user.agent)
    photo = get_object_or_404(Photo, id=photo_id, bien=bien)
    
    # Si la photo supprimée était principale, définir une autre photo comme principale
    was_principal = photo.est_principale
    photo.delete()
    
    if was_principal:
        other_photo = Photo.objects.filter(bien=bien).first()
        if other_photo:
            other_photo.est_principale = True
            other_photo.save()
    
    messages.success(request, "Photo supprimée avec succès.")
    return redirect('modifier_bien', bien_id=bien_id)
@login_required
def supprimer_bien(request, bien_id):
    if not hasattr(request.user, 'agent'):
        messages.error(request, "Accès réservé aux agents.")
        return redirect('accueil')
    
    bien = get_object_or_404(Bien, id=bien_id, agent=request.user.agent)
    if request.method == 'POST':
        bien.delete()
        messages.success(request, "Bien supprimé avec succès !")
        return redirect('mes_biens')
    
    return render(request, 'annonces/supprimer_bien.html', {'bien': bien})

@login_required
def demandes_recues(request):
    if not hasattr(request.user, 'agent'):
        messages.error(request, "Accès réservé aux agents.")
        return redirect('accueil')
    
    demandes = Demande.objects.filter(bien__agent=request.user.agent).order_by('-date_demande')
    return render(request, 'annonces/demandes_recues.html', {
        'demandes': demandes,
        'total_demandes': demandes.count(),
        'en_attente': demandes.filter(statut='en_attente').count(),
    })

@login_required
def traiter_demande(request, demande_id, action):
    if not hasattr(request.user, 'agent'):
        messages.error(request, "Accès réservé aux agents.")
        return redirect('accueil')
    
    demande = get_object_or_404(Demande, id=demande_id, bien__agent=request.user.agent)
    demande.statut = 'acceptee' if action == 'accepter' else 'refusee'
    demande.save()
    messages.success(request, f"Demande {action}ée avec succès.")
    return redirect('demandes_recues')

@login_required
def demander_visite(request, bien_id):
    if not hasattr(request.user, 'client'):
        messages.error(request, "Vous devez être client.")
        return redirect('connexion')
    
    bien = get_object_or_404(Bien, id=bien_id)
    if Demande.objects.filter(client=request.user.client, bien=bien).exists():
        messages.warning(request, "Demande déjà envoyée.")
        return redirect('detail_bien', bien_id=bien_id)
    
    if request.method == 'POST':
        form = DemandeVisiteForm(request.POST)
        if form.is_valid():
            demande = form.save(commit=False)
            demande.client = request.user.client
            demande.bien = bien
            demande.save()
            messages.success(request, f"Demande envoyée pour {bien.titre}")
    return redirect('detail_bien', bien_id=bien_id)

@login_required
def mes_demandes(request):
    if not hasattr(request.user, 'client'):
        messages.error(request, "Accès réservé aux clients.")
        return redirect('accueil')
    
    demandes = Demande.objects.filter(client=request.user.client).order_by('-date_demande')
    return render(request, 'annonces/mes_demandes.html', {'demandes': demandes})

# Profil Client
@login_required
def mon_profil(request):
    if not hasattr(request.user, 'client'):
        messages.error(request, "Accès réservé aux clients.")
        return redirect('accueil')
    return render(request, 'annonces/mon_profil.html', {'client': request.user.client})

@login_required
def modifier_profil(request):
    if not hasattr(request.user, 'client'):
        messages.error(request, "Accès réservé aux clients.")
        return redirect('accueil')
    
    client = request.user.client
    if request.method == 'POST':
        form = ModifierProfilClientForm(request.POST, instance=client)
        if form.is_valid():
            user = request.user
            user.email = form.cleaned_data['email']
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            user.save()
            form.save()
            messages.success(request, "Profil mis à jour !")
            return redirect('mon_profil')
    else:
        form = ModifierProfilClientForm(instance=client)
        form.fields['first_name'].initial = request.user.first_name
        form.fields['last_name'].initial = request.user.last_name
        form.fields['email'].initial = request.user.email
    
    return render(request, 'annonces/modifier_profil.html', {'form': form})

@login_required
def supprimer_compte(request):
    if not hasattr(request.user, 'client'):
        messages.error(request, "Accès réservé aux clients.")
        return redirect('accueil')
    
    if request.method == 'POST':
        user = request.user
        user.delete()
        messages.success(request, "Compte supprimé.")
        return redirect('accueil')
    
    return render(request, 'annonces/supprimer_compte.html')

# DASHBOARD ADMIN
@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    stats = {
        'total_agences': Agence.objects.count(),
        'total_agents': Agent.objects.count(),
        'total_clients': Client.objects.count(),
        'total_categories': Categorie.objects.count(),
        'total_biens': Bien.objects.count(),
        'total_demandes': Demande.objects.count(),
        'demandes_en_attente': Demande.objects.filter(statut='en_attente').count(),
        'biens_publies': Bien.objects.filter(statut='publie').count(),
    }
    derniers_biens = Bien.objects.all().order_by('-date_creation')[:5]
    dernieres_demandes = Demande.objects.all().order_by('-date_demande')[:5]
    
    return render(request, 'annonces/admin_dashboard.html', {
        'stats': stats,
        'derniers_biens': derniers_biens,
        'dernieres_demandes': dernieres_demandes,
    })

@login_required
@user_passes_test(is_admin)
def gestion_agences(request):
    agences = Agence.objects.all().annotate(nb_agents=Count('agents'), nb_biens=Count('biens'))
    if request.method == 'POST':
        form = AgenceForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Agence créée avec succès !")
            return redirect('gestion_agences')
    else:
        form = AgenceForm()
    
    return render(request, 'annonces/gestion_agences.html', {'agences': agences, 'form': form})

@login_required
@user_passes_test(is_admin)
def modifier_agence(request, agence_id):
    agence = get_object_or_404(Agence, id=agence_id)
    if request.method == 'POST':
        form = AgenceForm(request.POST, instance=agence)
        if form.is_valid():
            form.save()
            messages.success(request, "Agence modifiée !")
            return redirect('gestion_agences')
    else:
        form = AgenceForm(instance=agence)
    
    return render(request, 'annonces/modifier_agence.html', {'form': form, 'agence': agence})

@login_required
@user_passes_test(is_admin)
def supprimer_agence(request, agence_id):
    agence = get_object_or_404(Agence, id=agence_id)
    if request.method == 'POST':
        agence.delete()
        messages.success(request, "Agence supprimée !")
        return redirect('gestion_agences')
    return render(request, 'annonces/supprimer_agence.html', {'agence': agence})

@login_required
@user_passes_test(is_admin)
def gestion_agents(request):
    agents = Agent.objects.all().select_related('agence', 'user')
    if request.method == 'POST':
        form = AgentForm(request.POST)
        if form.is_valid():
            agent = form.save(commit=False)
            username = f"{agent.prenom.lower()}.{agent.nom.lower()}"
            password = request.POST.get('password')
            user = User.objects.create_user(
                username=username,
                email=agent.email,
                password=password,
                first_name=agent.prenom,
                last_name=agent.nom
            )
            agent.user = user
            agent.save()
            messages.success(request, "Agent créé !")
            return redirect('gestion_agents')
    else:
        form = AgentForm()
    
    return render(request, 'annonces/gestion_agents.html', {'agents': agents, 'form': form})

@login_required
@user_passes_test(is_admin)
def gestion_clients(request):
    clients = Client.objects.all().select_related('user')
    return render(request, 'annonces/gestion_clients.html', {'clients': clients})

@login_required
@user_passes_test(is_admin)
def gestion_categories(request):
    categories = Categorie.objects.all().annotate(nb_biens=Count('biens'))
    if request.method == 'POST':
        form = CategorieForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Catégorie ajoutée !")
            return redirect('gestion_categories')
    else:
        form = CategorieForm()
    
    return render(request, 'annonces/gestion_categories.html', {'categories': categories, 'form': form})

@login_required
@user_passes_test(is_admin)
def modifier_categorie(request, categorie_id):
    categorie = get_object_or_404(Categorie, id=categorie_id)
    if request.method == 'POST':
        form = CategorieForm(request.POST, instance=categorie)
        if form.is_valid():
            form.save()
            messages.success(request, "Catégorie modifiée !")
            return redirect('gestion_categories')
    else:
        form = CategorieForm(instance=categorie)
    return render(request, 'annonces/modifier_categorie.html', {'form': form, 'categorie': categorie})

@login_required
@user_passes_test(is_admin)
def supprimer_categorie(request, categorie_id):
    categorie = get_object_or_404(Categorie, id=categorie_id)
    if request.method == 'POST':
        categorie.delete()
        messages.success(request, "Catégorie supprimée !")
        return redirect('gestion_categories')
    return render(request, 'annonces/supprimer_categorie.html', {'categorie': categorie})

@login_required
@user_passes_test(is_admin)
def gestion_biens(request):
    biens = Bien.objects.all().select_related('categorie', 'agence', 'agent')
    return render(request, 'annonces/gestion_biens.html', {'biens': biens})

@login_required
@user_passes_test(is_admin)
def gestion_demandes(request):
    demandes = Demande.objects.all().select_related('client', 'bien').order_by('-date_demande')
    return render(request, 'annonces/gestion_demandes.html', {'demandes': demandes})