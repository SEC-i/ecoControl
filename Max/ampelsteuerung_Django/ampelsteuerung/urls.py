from django.conf.urls import patterns, include, url
from ampelsteuerung.views import *

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
	url(r'^hello/$',hello),
	url(r'^time/plus/(\d{1,2})/$',current_date),
    url(r'^switch/$',switch),
	url(r'^$',ampel),
    # Examples:
    # url(r'^$', 'ampelsteuerung.views.home', name='home'),
    # url(r'^ampelsteuerung/', include('ampelsteuerung.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)
