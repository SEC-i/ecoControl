from django.core.management.base import BaseCommand
from server.forecasting.forecasting.auto_optimization import simulation_run


class Command(BaseCommand):
    help = 'Refresh materialized views for aggregated sensorvalues in the database'

    def handle(self, *args, **options):
        simulation_run()
