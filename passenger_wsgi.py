import sys
import os

# Chemin relatif a ce fichier : fonctionne quel que soit le dossier
# choisi comme "Application root" dans cPanel.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'immobilier.settings')

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
