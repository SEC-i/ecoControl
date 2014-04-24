from simulation.systems.data import weekly_electrical_demand_winter, weekly_electrical_demand_summer, warm_water_demand_workday, warm_water_demand_weekend
from datetime import date,datetime,timedelta
#import matplotlib.pyplot as plt
#import matplotlib.dates as md
from holt_winters import multiplicative, additive
from helpers import make_two_year_data



class Forecast:
    """a Forecast with two seasons. The seasons will be extended (copied) into a 2 year array, then holtwinters will forecast from this timepoint on
    @param: season1, season2 datasets, which contain weekly data"""
    def __init__(self, env, week_season1, week_season2=None,  sample_type="daily", sampling_interval = 15, start=None, hw_parameters=(None,None,None)):
        self.hw_parameters = hw_parameters
        if start == None:
            start = datetime.fromtimestamp(env.now) - timedelta(days = 2 * 365) #2years before now
        
        if sample_type == "daily":
            map_week_to_index = lambda x : x
        elif sample_type =="workday_weekend":
            # map workdays to 0 and weekends to 1
            map_week_to_index = lambda x: 0 if x < 5 else 1
        else:
            raise NotImplementedError
        
        w2 = week_season2 if week_season2 != None else week_season1
            
        self.twoyear_demand = make_two_year_data(week_season1,w2,
                                                             sampling_interval = sampling_interval,
                                                             start = start,
                                                             map_weekday=map_week_to_index)
        
        self.forecasted_values = self.forecast_demand()
        #ending time of input data
        self.time_series_end = start + timedelta(days=365*2)
        self.sampling_interval = sampling_interval
        # wait at least one day before making a new forecast
        self.forecast_interval = 24 * 60 * 60
        self.env = env
        
        
        
    def forecast_demand(self):
        y = self.twoyear_demand
        #alpha = 0.9  #forecastings are weighted more on new data
        #beta = 0 #no slope changes
        #gamma = 1 #estimation of seasonal component based on  recent changes
       
        #alpha, beta, gamma. if any is None, holt.winters determines them automatically
        #cost-expensive, so only do this once..
        (alpha,beta,gamma) = self.hw_parameters
        m = int(len(y) * 0.5) #value sampling shift.. somehow
        fc = len(y) * 2 # f
        (forecast_values, alpha, beta, gamma, rmse) = multiplicative(y, m, fc,alpha,beta,gamma)
        self.hw_parameters = (alpha,beta,gamma)
        
        return list(forecast_values)
    
    def append_values(self,data):
        if type(data) == list:
            self.twoyear_demand += data
        else:
            for val in data:
                self.twoyear_demand.append(val)
                
        delta = (self.env.now - self.start_date).total_seconds()
        if delta > self.forecast_interval:
            self.forecasted_values = self.forecast_demand()
            self.time_series_end = self.env.now

        
        
                
    def forecast_at(self,timestamp):
        date = datetime.fromtimestamp(timestamp)
        delta = (date - self.time_series_end).total_seconds() 
        arr_index = (delta / 60) / self.sampling_interval
        if int(arr_index) % 1000 == 0.0:
            print arr_index, date
        return self.forecasted_values[int(arr_index)]

        
            