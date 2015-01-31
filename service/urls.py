from django.conf.urls import patterns, include, url
from django.contrib.auth.views import login, logout
from django.contrib import admin


admin.autodiscover()


urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'service.views.home', name='home'),

    url(r'^zaloguj/$', login, {'template_name': 'registration/login.html'}, name='login'),
    url(r'^wyloguj/$', logout, {'template_name': 'registration/logout.html'}, name='logout'),
    url(r'^admin/', include(admin.site.urls)),

    url(r'^zgloszenie/', include('product.urls')),
    url(r'^raporty/', include('statement.urls')),
    url(r'^klient/', include('person.urls')),
)
