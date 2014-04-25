from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

import views

urlpatterns = patterns('',
    (r'^$', views.index),
    (r'^configure/$', views.configure),
    (r'^forecast/$', views.forecast),
    (r'^login/$', views.login_user),
    (r'^logout/$', views.logout_user),
    (r'^status/$', views.status),

    url(r'^admin/', include(admin.site.urls)),
)
