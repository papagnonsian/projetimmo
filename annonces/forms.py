import datetime

from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.utils import timezone
from .models import Agence, Agent, Client, Bien, Photo, Demande, Categorie

HEURE_OUVERTURE = datetime.time(8, 0)
HEURE_FERMETURE = datetime.time(18, 0)


class StyleFormMixin:
    """Applique la classe CSS form-control à tous les champs du formulaire."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            classes = field.widget.attrs.get('class', '')
            if 'form-control' not in classes:
                field.widget.attrs['class'] = f'{classes} form-control'.strip()


# Formulaire inscription client
class InscriptionClientForm(StyleFormMixin, UserCreationForm):
    nom = forms.CharField(max_length=100, required=True)
    prenom = forms.CharField(max_length=100, required=True)
    telephone = forms.CharField(max_length=20, required=True)
    email = forms.EmailField(required=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Cet email est déjà utilisé.")
        return email
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            Client.objects.create(
                user=user,
                nom=self.cleaned_data['nom'],
                prenom=self.cleaned_data['prenom'],
                telephone=self.cleaned_data['telephone'],
                email=self.cleaned_data['email']
            )
        return user

# Formulaire inscription agent
class InscriptionAgentForm(StyleFormMixin, UserCreationForm):
    nom = forms.CharField(max_length=100, required=True)
    prenom = forms.CharField(max_length=100, required=True)
    telephone = forms.CharField(max_length=20, required=True)
    email = forms.EmailField(required=True)
    agence_nom = forms.CharField(max_length=200, required=True, label="Nom de l'agence")
    agence_adresse = forms.CharField(widget=forms.Textarea, required=True, label="Adresse de l'agence")
    agence_telephone = forms.CharField(max_length=20, required=True, label="Téléphone de l'agence")
    agence_email = forms.EmailField(required=True, label="Email de l'agence")
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Cet email est déjà utilisé.")
        return email
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            agence = Agence.objects.create(
                nom_agence=self.cleaned_data['agence_nom'],
                adresse=self.cleaned_data['agence_adresse'],
                telephone=self.cleaned_data['agence_telephone'],
                email=self.cleaned_data['agence_email']
            )
            Agent.objects.create(
                user=user,
                nom=self.cleaned_data['nom'],
                prenom=self.cleaned_data['prenom'],
                telephone=self.cleaned_data['telephone'],
                email=self.cleaned_data['email'],
                agence=agence
            )
        return user

class ConnexionForm(StyleFormMixin, forms.Form):
    username = forms.CharField(max_length=100)
    password = forms.CharField(widget=forms.PasswordInput)

class BienForm(StyleFormMixin, forms.ModelForm):
    surface = forms.IntegerField(required=False, min_value=0, label="Surface (m²)")
    pieces = forms.IntegerField(required=False, min_value=0, label="Nombre de pièces")

    class Meta:
        model = Bien
        fields = ['titre', 'description', 'prix', 'localisation', 'type_transaction', 'surface', 'pieces', 'categorie', 'statut']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['surface'].widget.attrs.update({'min': '0'})
        self.fields['pieces'].widget.attrs.update({'min': '0'})

class DemandeVisiteForm(StyleFormMixin, forms.ModelForm):
    class Meta:
        model = Demande
        fields = ['message', 'date_visite_souhaitee', 'heure_visite_souhaitee']
        widgets = {
            'message': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Votre message...'}),
            'date_visite_souhaitee': forms.DateInput(attrs={
                'type': 'date',
                'min': timezone.localdate().isoformat(),
            }),
            'heure_visite_souhaitee': forms.TimeInput(attrs={
                'type': 'time',
                'min': HEURE_OUVERTURE.strftime('%H:%M'),
                'max': HEURE_FERMETURE.strftime('%H:%M'),
            }),
        }
        labels = {
            'message': 'Message (optionnel)',
            'date_visite_souhaitee': 'Date souhaitée (optionnelle)',
            'heure_visite_souhaitee': 'Heure souhaitée (optionnelle, entre 8h et 18h)',
        }

    def clean_date_visite_souhaitee(self):
        date = self.cleaned_data.get('date_visite_souhaitee')
        if date and date < timezone.localdate():
            raise forms.ValidationError("La date de visite ne peut pas être dans le passé.")
        return date

    def clean_heure_visite_souhaitee(self):
        heure = self.cleaned_data.get('heure_visite_souhaitee')
        if heure and not (HEURE_OUVERTURE <= heure <= HEURE_FERMETURE):
            raise forms.ValidationError("L'heure de visite doit être comprise entre 8h et 18h.")
        return heure

    def clean(self):
        cleaned_data = super().clean()
        date = cleaned_data.get('date_visite_souhaitee')
        heure = cleaned_data.get('heure_visite_souhaitee')
        if heure and not date and 'date_visite_souhaitee' not in self.errors:
            raise forms.ValidationError("Précisez une date pour l'heure de visite choisie.")
        if date == timezone.localdate() and heure and heure < timezone.localtime().time():
            raise forms.ValidationError("L'heure de visite est déjà passée pour aujourd'hui.")
        return cleaned_data

class FiltreBiensForm(StyleFormMixin, forms.Form):
    q = forms.CharField(
        required=False,
        label="Recherche",
        widget=forms.TextInput(attrs={'placeholder': 'Titre, description...'})
    )
    categorie = forms.ModelChoiceField(
        queryset=Categorie.objects.all(),
        required=False,
        empty_label="Toutes les catégories",
    )
    type_transaction = forms.ChoiceField(
        choices=[('', 'Vente et location')] + Bien.TYPE_TRANSACTION_CHOICES,
        required=False,
    )
    commune = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Commune'})
    )
    prix_min = forms.IntegerField(
        required=False,
        min_value=0,
        widget=forms.NumberInput(attrs={'placeholder': 'Prix min'})
    )
    prix_max = forms.IntegerField(
        required=False,
        min_value=0,
        widget=forms.NumberInput(attrs={'placeholder': 'Prix max'})
    )

# Formulaires admin
class AgenceForm(StyleFormMixin, forms.ModelForm):
    class Meta:
        model = Agence
        fields = ['nom_agence', 'adresse', 'telephone', 'email', 'premium_jusqu_au']
        widgets = {
            'adresse': forms.Textarea(attrs={'rows': 3}),
            'premium_jusqu_au': forms.DateInput(attrs={'type': 'date'}),
        }

class AgentForm(StyleFormMixin, forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, required=False)

    class Meta:
        model = Agent
        fields = ['nom', 'prenom', 'telephone', 'email', 'agence']

class CategorieForm(StyleFormMixin, forms.ModelForm):
    class Meta:
        model = Categorie
        fields = ['nom_categorie']

class ModifierProfilClientForm(StyleFormMixin, forms.ModelForm):
    first_name = forms.CharField(max_length=30, required=False, label="Prénom")
    last_name = forms.CharField(max_length=30, required=False, label="Nom")
    email = forms.EmailField(required=True)

    class Meta:
        model = Client
        fields = ['nom', 'prenom', 'telephone', 'email']