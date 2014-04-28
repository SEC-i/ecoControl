from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

import views

urlpatterns = patterns('',
    (r'^$', views.index),
    (r'^api/configure/$', views.configure),
    (r'^api/forecast/$', views.forecast),
    (r'^api/login/$', views.login_user),
    (r'^api/logout/$', views.logout_user),
    (r'^api/status/$', views.status),

    url(r'^admin/', include(admin.site.urls)),
)
