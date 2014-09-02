from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('namingservice.profiles.views',
    url(r'^register/$', 'register', name='register_page'),
    url(r'^settings/$', 'settings', name='settings_page'),
    url(r'^changepass/$', 'password_change', name='password_change'),
)

urlpatterns += patterns('django.contrib.auth.views',
    url(r'^login/$', 'login', {'template_name': 'profiles/login.djhtml'}, name='login_page'),
    url(r'^logout/$', 'logout', {'next_page': '/'}, name='logout_page'),
)