from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

import views
import manager.hooks

urlpatterns = patterns('',
    (r'^$', views.index),
    (r'^api/configure/$', views.configure),
    (r'^api/data/((?P<start>\d+)/)?$', views.list_values),
    (r'^api/data/daily/((?P<start>\d+)/)?$', views.list_values, {'accuracy': 'day'}),
    (r'^api/export/sensorvalues/$', views.export_sensor_values),
    (r'^api/forecast/$', views.forecast),
    (r'^api/live/$', views.live_data),
    (r'^api/login/$', views.login_user),
    (r'^api/logout/$', views.logout_user),
    (r'^api/manage/thresholds/$', views.handle_threshold),
    (r'^api/notifications/(start/(?P<start>[0-9]+)/)?(end/(?P<end>[0-9]+)/)?$', views.list_notifications),
    (r'^api/sensors/$', views.list_sensors),
    (r'^api/settings/$', views.settings),
    (r'^api/settings/tunable/$', views.get_tunable_device_configurations),
    (r'^api/start/$', views.start_system),
    (r'^api/statistics/$', views.get_statistics),
    (r'^api/statistics/monthly/$', views.get_monthly_statistics),
    (r'^api/status/$', views.status),
    (r'^api/thresholds/$', views.list_thresholds),

    (r'^api2/balance/totals/$', manager.hooks.get_totals),
    (r'^api2/balance/infeed/$', manager.hooks.get_infeed),
    (r'^api2/balance/purchase/$', manager.hooks.get_purchase),
    (r'^api2/balance/maintenance/$', manager.hooks.get_maintenance_costs),
    (r'^api2/consumption/thermal/$', manager.hooks.get_thermal_consumption),
    (r'^api2/consumption/warmwater/$', manager.hooks.get_warmwater_consumption),
    (r'^api2/consumption/electrical/$', manager.hooks.get_electrical_consumption),
    (r'^api2/consumption/cu/$', manager.hooks.get_cu_consumption,),
    (r'^api2/consumption/plb/$', manager.hooks.get_plb_consumption),
    (r'^api2/sums/(sensor/(?P<sensor_id>[0-9]+)/)?(year/(?P<year>[0-9]+)/)?$', manager.hooks.get_sums),
    (r'^api2/avgs/(sensor/(?P<sensor_id>[0-9]+)/)?(year/(?P<year>[0-9]+)/)?$', manager.hooks.get_avgs),
    (r'^api2/history/$', manager.hooks.get_sensorvalue_history_list),
    (r'^api2/sensor/((?P<sensor_id>\d+)/)?$', manager.hooks.get_detailed_sensor_values),
    (r'^api2/loads/$', manager.hooks.get_daily_loads),
    (r'^api2/balance/total/((?P<year>\d+)/)?((?P<month>\d+)/)?$', manager.hooks.get_total_balance),
    (r'^api2/balance/total/latest/$', manager.hooks.get_latest_total_balance),

    url(r'^admin/', include(admin.site.urls)),
)
