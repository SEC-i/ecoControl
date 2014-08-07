from django.core.management.base import BaseCommand
import time
from datetime import datetime
from django.utils.timezone import utc
from cStringIO import StringIO

from server.forecasting import Forecast, get_initial_time
from server.forecasting.measurementstorage import MeasurementStorage

class Command(BaseCommand):
    help = 'run a forecast (for profiling)'

    def handle(self, *args, **options):


        #profile = LineProfiler(Forecast.step)
        self.fc = Forecast(get_initial_time(), forward=24*3600*14)
        profiled_functions = [Forecast.step, MeasurementStorage.take_and_cache]
        self.profile_lines(profiled_functions,"self.fc.run()")

    def profile_lines(self, functions, statement):
        from line_profiler import LineProfiler
        import __builtin__

        profile = LineProfiler(*functions)
        # Add the profiler to the builtins for @profile.. 
        # will probably not work for all modules in ecoControl, 
        # as they are already imported before and @profile will then throw an error
        if 'profile' in __builtin__.__dict__:
            had_profile = True
            old_profile = __builtin__.__dict__['profile']
        else:
            had_profile = False
            old_profile = None
        __builtin__.__dict__['profile'] = profile

        try:
            try:
                profile.runctx(statement, globals(), locals())
                message = ''
            except SystemExit:
                message = """*** SystemExit exception caught in code being profiled."""
            except KeyboardInterrupt:
                message = ("*** KeyboardInterrupt exception caught in code being "
                    "profiled.")
        finally:
            if had_profile:
                __builtin__.__dict__['profile'] = old_profile

        # Trap text output.
        stdout_trap = StringIO()
        profile.print_stats(stdout_trap)
        output = stdout_trap.getvalue()
        output = output.rstrip()

        pfile = open("profile.txt", 'a')
        pfile.write("\n\n" + 20 * "=" + "*********====================== profile at time " + 
            time.strftime("%b %d %Y %H:%M:%S", time.gmtime(time.time())) +
             "==================================\n\n")
        pfile.write(output)
        pfile.close()
        print '\n*** Profile printout saved to text file profile.txt', message