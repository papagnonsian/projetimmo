import sys
import os

sys.path.insert(0, '/home4/sc7zds18/immo/public/immo/immobilier')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'immobilier.settings')
os.environ.setdefault('DJANGO_SECRET_KEY', 'REMPLACE-PAR-UNE-CLE-SECRETE-LONGUE-ET-ALEATOIRE')
os.environ.setdefault('DJANGO_DEBUG', 'False')
os.environ.setdefault('DJANGO_ALLOWED_HOSTS', 'vianey.demo.sc7zds18.universe.wf')

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
