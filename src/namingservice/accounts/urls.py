from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('namingservice.accounts.views',
    url(r'^my/$', 'account', name='my_account'),
    url(r'^withdraw/$', 'withdraw', name='withdraw'),
    # url(r'^add/$', 'add_funds', name='add_funds'),
)