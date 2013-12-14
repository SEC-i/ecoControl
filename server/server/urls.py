from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

import models
from webapi import views

urlpatterns = patterns('',
    (r'^$', views.index),
    (r'^api/$', views.api_index),
    (r'^api/actuator/(?P<item_id>\d+)/$', views.show_item, {'model': models.Actuator}),
    (r'^api/devices/(limit/(?P<limit>\d+)/)?$', views.list_items, {'model': models.Device}),
    (r'^api/device/(?P<item_id>\d+)/$', views.show_item, {'model': models.Device}),
    (r'^api/device/(?P<device_id>\d+)/actuators/(limit/(?P<limit>\d+)/)?$', views.list_items, {'model': models.Actuator}),
    (r'^api/device/(?P<device_id>\d+)/data/$', views.receive_device_data),
    (r'^api/device/(?P<device_id>\d+)/entries/(start/(?P<start>\d+)/)?(end/(?P<end>\d+)/)?(limit/(?P<limit>\d+)/)?$', views.list_entries),
    (r'^api/device/(?P<device_id>\d+)/sensors/(limit/(?P<limit>\d+)/)?$', views.list_items, {'model': models.Sensor}),
    (r'^api/device/(?P<device_id>\d+)/set/$', views.set_device),
    (r'^api/entry/(?P<item_id>\d+)/$', views.show_item, {'model': models.SensorEntry}),
    (r'^api/login/$', views.api_login),
    (r'^api/logout/$', views.api_logout),
    (r'^api/sensor/(?P<item_id>\d+)/$', views.show_item, {'model': models.Sensor}),
    (r'^api/status/$', views.api_status),

    url(r'^admin/', include(admin.site.urls)),
)
