from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

from webapi import views

urlpatterns = patterns('',
    (r'^$', views.api_index),
    (r'^actuator/(?P<actuator_id>\d+)/$', views.show_actuator),
    (r'^devices/(limit/(?P<limit>\d+)/)?$', views.list_devices),
    (r'^device/(?P<device_id>\d+)/$', views.show_device),
    (r'^device/(?P<device_id>\d+)/actuators/(limit/(?P<limit>\d+)/)?$', views.list_actuators),
    (r'^device/(?P<device_id>\d+)/sensors/(limit/(?P<limit>\d+)/)?$', views.list_sensors),
    (r'^device/(?P<device_id>\d+)/entries/(start/(?P<start>\d+)/)?(end/(?P<end>\d+)/)?(limit/(?P<limit>\d+)/)?$', views.list_entries),
    (r'^device/(?P<device_id>\d+)/set/$', views.set_device),
    (r'^entry/(?P<entry_id>\d+)/$', views.show_entry),
    (r'^login/$', views.api_login),
    (r'^logout/$', views.api_logout),
    (r'^sensor/(?P<sensor_id>\d+)/$', views.show_sensor),
    (r'^sensor/(?P<sensor_id>\d+)/entries/(start/(?P<start>\d+)/)?(end/(?P<end>\d+)/)?(limit/(?P<limit>\d+)/)?$', views.list_sensor_entries),
    (r'^status/$', views.api_status),

    url(r'^admin/', include(admin.site.urls)),
)
