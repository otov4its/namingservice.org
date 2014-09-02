from django.conf.urls.defaults import *
from django.conf import settings
from namingservice.orders.views import orders

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
                       
    url(r'^$', orders, {'subset': 'all'}, name='home_page'),
    
    (r'^accounts/', include('namingservice.accounts.urls')),
    (r'^orders/', include('namingservice.orders.urls')),
    (r'^profiles/', include('namingservice.profiles.urls')),
    
    (r'^admin/doc/', include('django.contrib.admindocs.urls')),
    (r'^admin/', include(admin.site.urls)),
    
)

if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
    )
