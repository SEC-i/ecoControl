from django.core.management.base import BaseCommand
from django.db import connection

class Command(BaseCommand):
    help = 'Refresh materialized views for aggregated sensorvalues in the database'

    def handle(self, *args, **options):
        cursor = connection.cursor()
        cursor.execute('''REFRESH MATERIALIZED VIEW server_sensorvaluehourly;''')
        cursor.execute('''REFRESH MATERIALIZED VIEW server_sensorvaluemonthly;''')
        self.stdout.write('Successfully refreshed views')
