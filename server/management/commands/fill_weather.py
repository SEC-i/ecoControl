from django.core.management.base import BaseCommand
from os import listdir
from os.path import isfile, join
from server.settings import BASE_DIR
from datetime import datetime
import json
from server.models import WeatherValue, RealWeatherValue
from django.utils.timezone import utc

class Command(BaseCommand):
    help = 'fill weather from files into the database'

    def handle(self, *args, **options):
        directory  = join(BASE_DIR,"server","forecasting","devices","data","weatherforecast")
        
        
        
        files = [ f for f in listdir(directory) if (isfile(join(directory,f)) and f.startswith("history") ) ]
        for f_path in files:
            with open(join(directory,f_path),"r") as _file:
                date_string = f_path.split("_")[1].split(".")[0]
                try:
                    (year,month,day) = (int(date_string[:4]),int(date_string[4:6]),int(date_string[6:]))
                    
                    content = json.loads(_file.read() )
                    print f_path
                    observations = content["history"]["observations"]
                    for ob in observations:
                        _date = ob["date"]
                        ob_time = datetime(year=int(_date["year"]),
                                           month=int(_date["mon"]),
                                           day=int(_date["mday"]),
                                           hour=int(_date["hour"]),
                                           minute=int(_date["min"])).replace(tzinfo=utc)
                                           
                        value = float(ob["tempm"])
        
                        entry = RealWeatherValue(temperature=value, timestamp=ob_time)
                        entry.save()
                except:
                    print "error for ", date_string

        files = [ f for f in listdir(directory) if (isfile(join(directory,f)) and f.startswith("hourly10day") ) ]
        for f_path in files:
            with open(join(directory,f_path),"r") as _file:
                creation_time = datetime.fromtimestamp(int(f_path.split("_")[1].split(".")[0])).replace(tzinfo=utc)
                content = json.loads(_file.read() )
                print f_path
                forecasts = content["hourly_forecast"]
                for forecast in forecasts:
                    forecast_time = datetime.fromtimestamp(int(forecast["FCTTIME"]["epoch"])).replace(tzinfo=utc)
                    value = float(forecast["temp"]["metric"])
    
                    entry = WeatherValue(temperature=value, timestamp=creation_time, target_time=forecast_time)
                    entry.save()
                    
