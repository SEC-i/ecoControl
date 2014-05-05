from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

import views

urlpatterns = patterns('',
    (r'^$', views.index),
    (r'^api/configure/$', views.configure),
    (r'^api/data/((?P<start>\d+)/)?$', views.list_values),
    (r'^api/forecast/$', views.forecast),
    (r'^api/live/$', views.live_data),
    (r'^api/login/$', views.login_user),
    (r'^api/logout/$', views.logout_user),
    (r'^api/sensors/$', views.list_sensors),
    (r'^api/settings/$', views.settings),
    (r'^api/statistics/(start/(?P<start>\d+)/)?(end/(?P<end>\d+)/)?$', views.get_statistics),
    (r'^api/statistics/monthly/(start/(?P<start>\d+)/)?(end/(?P<end>\d+)/)?$', views.get_monthly_statistics),
    (r'^api/status/$', views.status),

    url(r'^admin/', include(admin.site.urls)),
)
