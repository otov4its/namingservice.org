from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('namingservice.orders.views',
    url(r'^all/$', 'orders', {'subset': 'all'}, name='orders_all'),
    url(r'^my/$', 'orders', {'subset': 'my'}, name='orders_my'),
    url(r'^my/suggestions/$', 'orders', {'subset': 'suggestions'}, name='orders_suggestions'),
    (r'^id/(?P<order_id>\d+)/$', 'order_details'),
    url(r'^add/$', 'add_order', name='add_order'),
    url(r'^delete/$', 'delete_order', name='delete_order'),
    url(r'^pay/$', 'pay_order', name='pay_order'),
    url(r'^suggestions/add$', 'add_suggestion', name='add_suggestion'),
    url(r'^suggestions/delete$', 'delete_suggestion', name='delete_suggestion'),
    url(r'^suggestions/vote$', 'vote_suggestion', name='vote_suggestion'),
    url(r'^suggestions/win$', 'win_suggestion', name='win_suggestion'),
)