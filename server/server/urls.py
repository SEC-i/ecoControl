from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

from webapi import views

urlpatterns = patterns('',
    (r'^$', views.index),
    (r'^api/$', views.api_index),
    (r'^api/actuator/(?P<actuator_id>\d+)/$', views.show_actuator),
    (r'^api/devices/(limit/(?P<limit>\d+)/)?$', views.list_devices),
    (r'^api/device/(?P<device_id>\d+)/$', views.show_device),
    (r'^api/device/(?P<device_id>\d+)/actuators/(limit/(?P<limit>\d+)/)?$', views.list_actuators),
    (r'^api/device/(?P<device_id>\d+)/sensors/(limit/(?P<limit>\d+)/)?$', views.list_sensors),
    (r'^api/device/(?P<device_id>\d+)/entries/(start/(?P<start>\d+)/)?(end/(?P<end>\d+)/)?(limit/(?P<limit>\d+)/)?$', views.list_entries),
    (r'^api/device/(?P<device_id>\d+)/entrieshc/(start/(?P<start>\d+)/)?(end/(?P<end>\d+)/)?(limit/(?P<limit>\d+)/)?$', views.list_all_entries),
    (r'^api/device/(?P<device_id>\d+)/set/$', views.set_device),
    (r'^api/entry/(?P<entry_id>\d+)/$', views.show_entry),
    (r'^api/login/$', views.api_login),
    (r'^api/logout/$', views.api_logout),
    (r'^api/sensor/(?P<sensor_id>\d+)/$', views.show_sensor),
    (r'^api/sensor/(?P<sensor_id>\d+)/entries/(start/(?P<start>\d+)/)?(end/(?P<end>\d+)/)?(limit/(?P<limit>\d+)/)?$', views.list_sensor_entries),
    (r'^api/status/$', views.api_status),

    url(r'^admin/', include(admin.site.urls)),
)
