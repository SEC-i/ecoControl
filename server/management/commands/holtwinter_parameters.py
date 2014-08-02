from django.core.management.base import BaseCommand
from server.forecasting.forecasting.auto_optimization import simulation_run
from server.forecasting import DemoSimulation
import time
from datetime import datetime
from django.utils.timezone import utc
from server.forecasting.tools.holt_winters_parameters import value_changer

class Command(BaseCommand):
    help = 'see the changes of parameters for holt winters'

    def handle(self, *args, **options):
        value_changer()
        