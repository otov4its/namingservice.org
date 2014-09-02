import os, sys

dn = os.path.dirname
PROJECT_ROOT = os.path.abspath( dn(dn(dn(__file__))) )
sys.path.append( PROJECT_ROOT )

os.environ['DJANGO_SETTINGS_MODULE'] = 'namingservice.settings'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()