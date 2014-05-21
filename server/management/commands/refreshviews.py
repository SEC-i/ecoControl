from django.core.management.base import BaseCommand
from django.db import connection

from server.worker.functions import refresh_views

class Command(BaseCommand):
    help = 'Refresh materialized views for aggregated sensorvalues in the database'

    def handle(self, *args, **options):
        refresh_views()
