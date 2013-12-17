import sys, time
from django.core.management.base import BaseCommand, CommandError
from server.planner import Planner

class Command(BaseCommand):
    args = ''
    help = 'Start planner thread'

    def handle(self, *args, **options):
        self.stdout.write('Starting planner thread...')
        Planner()
        # wait until KeyboardInterrupt
        while True:
            try:
                time.sleep(1)
            except KeyboardInterrupt:
                self.stdout.write('Stopping planner...')
                sys.exit(1)