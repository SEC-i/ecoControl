from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

import hooks
import manager.hooks
import technician.hooks

urlpatterns = patterns('',
    # general hooks
    (r'^$', hooks.index),
    (r'^api/$', hooks.index),
    (r'^api/export/$', hooks.export_csv),
    (r'^api/login/$', hooks.login_user),
    (r'^api/logout/$', hooks.logout_user),
    (r'^api/notifications/(start/(?P<start>[0-9]+)/)?(end/(?P<end>[0-9]+)/)?$', hooks.list_notifications),
    (r'^api/sensors/$', hooks.list_sensors),
    (r'^api/settings/$', hooks.list_settings),
    (r'^api/status/$', hooks.status),

    # technician hooks
    (r'^api/configure/$', technician.hooks.configure),
    (r'^api/data/((?P<start>\d+)/)?$', technician.hooks.list_sensor_values),
    (r'^api/data/daily/((?P<start>\d+)/)?$', technician.hooks.list_sensor_values, {'accuracy': 'day'}),
    (r'^api/forecast/$', technician.hooks.forecast),
    (r'^api/forward/$', technician.hooks.forward),
    (r'^api/live/$', technician.hooks.live_data),
    (r'^api/manage/thresholds/$', technician.hooks.handle_threshold),
    (r'^api/settings/tunable/$', technician.hooks.get_tunable_device_configurations),
    (r'^api/snippets/$', technician.hooks.handle_snippets),
    (r'^api/code/$', technician.hooks.handle_code),
    (r'^api/start/$', technician.hooks.start_system),
    (r'^api/statistics/$', technician.hooks.get_statistics),
    (r'^api/statistics/monthly/$', technician.hooks.get_monthly_statistics),
    (r'^api/thresholds/$', technician.hooks.list_thresholds),

    # manager hooks
    (r'^api/avgs/(sensor/(?P<sensor_id>[0-9]+)/)?(year/(?P<year>[0-9]+)/)?$', manager.hooks.get_avgs),
    (r'^api/balance/total/((?P<year>\d+)/)?((?P<month>\d+)/)?$', manager.hooks.get_total_balance),
    (r'^api/balance/total/latest/$', manager.hooks.get_latest_total_balance),
    (r'^api/history/$', manager.hooks.get_sensorvalue_history_list),
    (r'^api/loads/$', manager.hooks.get_daily_loads),
    (r'^api/sensor/((?P<sensor_id>\d+)/)?$', manager.hooks.get_detailed_sensor_values),
    (r'^api/sums/(sensor/(?P<sensor_id>[0-9]+)/)?(year/(?P<year>[0-9]+)/)?$', manager.hooks.get_sums),

    url(r'^admin/', include(admin.site.urls)),
)
