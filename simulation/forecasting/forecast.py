from simulation.systems.data import weekly_electrical_demand_winter, weekly_electrical_demand_summer, warm_water_demand_workday, warm_water_demand_weekend
from datetime import date,datetime,timedelta
#import matplotlib.pyplot as plt
#import matplotlib.dates as md
from holt_winters import multiplicative, additive
from helpers import make_two_year_data



class Forecast:
    """a Forecast with two seasons. The seasons will be extended (copied) into a 2 year array, then holtwinters will forecast from this timepoint on
    @param: season1, season2 datasets, which contain weekly data"""
    def __init__(self, week_season1, week_season2=None,  sample_type="daily", sampling_interval = 15, start=datetime(2012,1,1,0,0,0), hw_parameters=(None,None,None)):
        self.hw_parameters = hw_parameters
        
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
    
    def get_value_at(self):
        pass