from django.core.management.base import BaseCommand
from server.forecasting.forecasting.auto_optimization import simulation_run
from server.forecasting import get_forecast
from server.functions import get_past_time
import calendar
from server.models import SensorValue
from time import time
import cProfile


class Command(BaseCommand):
    help = 'Refresh materialized views for aggregated sensorvalues in the database'

    def handle(self, *args, **options):
        try:
            latest_timestamp = get_past_time()
            initial_time = calendar.timegm(latest_timestamp.timetuple())
        except SensorValue.DoesNotExist:
            initial_time = time()
        
        output = get_forecast(initial_time)
        #cProfile.runctx("get_forecast(initial_time)",globals(),locals(),filename="profile.profile")
        
