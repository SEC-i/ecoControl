import sys
import datetime

from django.utils.timezone import utc
from django.db import connection, ProgrammingError
from django.db.models.signals import post_syncdb

from server.forecasting.systems.data import outside_temperatures_2013, outside_temperatures_2012
from server.models import Device, Sensor, Configuration, DeviceConfiguration, SensorValueDaily, SensorValueHourly, SensorValueMonthlyAvg, SensorValueMonthlySum, WeatherValue
from server.management import defaults


def initialize_defaults(**kwargs):
    defaults.initialize_default_user()
    defaults.initialize_default_scenario()
    defaults.initialize_views()
    defaults.initialize_weathervalues()

post_syncdb.connect(initialize_defaults)
