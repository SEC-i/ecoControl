from django.core.management.base import BaseCommand
from server.forecasting.forecasting.auto_optimization import simulation_run
from server.management.commands.helpers import export_csv, export_rows


class Command(BaseCommand):
    help = 'Refresh materialized views for aggregated sensorvalues in the database'

    def handle(self, *args, **options):
        norm,optim = simulation_run()
        
        #norm["dataset_name"] = "normal"
        export_csv([norm],"normal_run_1weekhourly.csv", "all")
        export_rows([norm],"normal_run_1weekhourly.txt", "all")
        #optim["dataset_name"] = "optim"
        export_csv([optim],"optimized_run_1weekhourly.csv", "all")
        export_rows([optim],"optimized_run_1weekhourly.txt", "all")
        
    
