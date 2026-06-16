from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Agence, Agent, Client, Bien, Photo, Demande, Categorie

# Formulaire inscription client
class InscriptionClientForm(UserCreationForm):
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
class InscriptionAgentForm(UserCreationForm):
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

class ConnexionForm(forms.Form):
    username = forms.CharField(max_length=100)
    password = forms.CharField(widget=forms.PasswordInput)

class BienForm(forms.ModelForm):
    class Meta:
        model = Bien
        fields = ['titre', 'description', 'prix', 'localisation', 'surface', 'pieces', 'categorie', 'statut']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})

class DemandeVisiteForm(forms.ModelForm):
    class Meta:
        model = Demande
        fields = ['message', 'date_visite_souhaitee']
        widgets = {
            'message': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Votre message...'}),
            'date_visite_souhaitee': forms.DateInput(attrs={'type': 'date'}),
        }
        labels = {
            'message': 'Message (optionnel)',
            'date_visite_souhaitee': 'Date souhaitée (optionnelle)',
        }

class FiltreBiensForm(forms.Form):
    categorie = forms.ModelChoiceField(
        queryset=Categorie.objects.all(),
        required=False,
        empty_label="Toutes les catégories",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    commune = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Commune'})
    )
    prix_min = forms.IntegerField(
        required=False,
        min_value=0,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Prix min'})
    )
    prix_max = forms.IntegerField(
        required=False,
        min_value=0,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Prix max'})
    )

# Formulaires admin
class AgenceForm(forms.ModelForm):
    class Meta:
        model = Agence
        fields = ['nom_agence', 'adresse', 'telephone', 'email']
        widgets = {
            'adresse': forms.Textarea(attrs={'rows': 3}),
        }

class AgentForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, required=False)
    
    class Meta:
        model = Agent
        fields = ['nom', 'prenom', 'telephone', 'email', 'agence']

class CategorieForm(forms.ModelForm):
    class Meta:
        model = Categorie
        fields = ['nom_categorie']

class ModifierProfilClientForm(forms.ModelForm):
    first_name = forms.CharField(max_length=30, required=False, label="Prénom")
    last_name = forms.CharField(max_length=30, required=False, label="Nom")
    email = forms.EmailField(required=True)
    
    class Meta:
        model = Client
        fields = ['nom', 'prenom', 'telephone', 'email']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})