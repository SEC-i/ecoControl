from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

import views

urlpatterns = patterns('',
    (r'^config/$', views.configure),
    (r'^forecast/$', views.forecast),
    (r'^login/$', views.login),
    (r'^logout/$', views.logout),
    (r'^status/$', views.status),

    url(r'^admin/', include(admin.site.urls)),
)
