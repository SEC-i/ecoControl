from django.core.management.base import BaseCommand
from server.forecasting.forecasting.auto_optimization import simulation_run
from server.management.commands.helpers import export_csv, export_rows
import calendar
from datetime import datetime, timedelta
from multiprocessing.process import Process

def target_func(start, name):
    norm,optim = simulation_run(start=start)
    export_csv([norm],"halfyear/normal_run_" + name + ".csv", "all")
    export_rows([norm],"halfyear/normal_run_" + name + ".txt", "all")
    export_csv([optim],"halfyear/optimized_run_" + name + ".csv", "all")
    export_rows([optim],"halfyear/optimized_run_" + name + ".txt", "all")


class Command(BaseCommand):
    help = 'Refresh materialized views for aggregated sensorvalues in the database'
    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument('date', nargs='+', type=int)
        
    

        
    def handle(self, *args, **options):
        jobs= []
        timestamp = calendar.timegm(datetime(year=2014,month=1,day=1).timetuple())
        for month in ["jan","feb","march","april","may","june"]:
            jobs.append(Process(target=target_func, args=(timestamp,month)))
            timestamp += timedelta(days=30).total_seconds()
        
        
        for job in jobs: job.start()
        for job in jobs: job.join()
        #norm,optim = simulation_run(options)
        
        #export_csv([norm],"normal_run_2weekhourly.csv", "all")
        #export_rows([norm],"normal_run_2weekhourly.txt", "all")
        #export_csv([optim],"optimized_run_2weekhourly.csv", "all")
        #export_rows([optim],"optimized_run_2weekhourly.txt", "all")
        
    
