from django.core.management.base import BaseCommand
from server.forecasting import DemoSimulation
import time
from datetime import datetime
from django.utils.timezone import utc


class Command(BaseCommand):
    help = 'fill database with demovalues'

    def handle(self, *args, **options):
        demo_sim = DemoSimulation.start_or_get(print_visible=True)
        demo_sim.forward = 24*3600*1
        while demo_sim.forward > 0:
            time.sleep(1)
            print datetime.fromtimestamp(demo_sim.env.now).replace(tzinfo=utc)
        demo_sim.measurements.flush_data()
        demo_sim.running = False
