from simulation.systems.data import weekly_electrical_demand_winter, weekly_electrical_demand_summer, warm_water_demand_workday, warm_water_demand_weekend
from datetime import date,datetime,timedelta
#import matplotlib.pyplot as plt
#import matplotlib.dates as md
from holt_winters import multiplicative, additive
from helpers import make_two_year_data



class Forecast:
    
    def __init__(self, env, input_data, sampling_interval = 15, start=None, hw_parameters=(None,None,None)):
        self.hw_parameters = hw_parameters
        data_length = timedelta(minutes=len(input_data) * sampling_interval)
        if start == None:
            start = datetime.fromtimestamp(env.now) - data_length
        
        
        
        
        #demands split into weekdays
        self.demands = self.split_weekdata(input_data)
        
        self.forecasted_values = self.forecast_demands()
        #ending time of input data
        self.time_series_end = start + timedelta(days=365*2)
        self.sampling_interval = sampling_interval
        # wait at least one day before making a new forecast
        self.forecast_interval = 24 * 60 * 60
        self.env = env
        
        
        self.hw_parameters = (0.0000001,0.0,1.0)
        
        
    def forecast_demands(self):
        #alpha = 0.9  #forecastings are weighted more on new data
        #beta = 0 #no slope changes
        #gamma = 1 #estimation of seasonal component based on  recent changes
        forecasted_demands  = []
        
        for demand in self.demands:
            
            #alpha, beta, gamma. if any is None, holt.winters determines them automatically
            #cost-expensive, so only do this once..
            m = self.sampling_interval
            fc = len(demand)
            (alpha,beta,gamma) = self.hw_parameters
            (forecast_values, alpha, beta, gamma, rmse) = multiplicative(demand, m,fc, alpha, beta, gamma)
            if rmse > 0.5:
                #find values automatically
                (forecast_values, alpha, beta, gamma, rmse) = multiplicative(demand, m,fc)
                self.hw_parameters = (alpha,beta,gamma)
            print "holt winters: alpha: ", alpha, "beta: ", beta, "gamma: ", gamma, "rmse: ", rmse
            forecasted_demands.append(list(forecast_values))
        
        return forecasted_demands
    
    def split_weekdata(self, data):
        weekday = 0
        split_array = [[] for i in range(7)]
        #samples per hour
        samples_hour = int(round(60.0/self.sampling_interval))
        for index, element in enumerate(data):
            if index % (24  * samples_hour) == 0:
                weekday = (weekday + 1) % 7
            split_array[index].append(element)
        return split_array
            
    
    
    def append_values(self,data): 
        new_demands = self.split_weekdata(data)
        for index, demand in enumerate(new_demands):
            self.demands[index] += demand
                   
        delta = (self.env.now - self.start_date).total_seconds()
        if delta > self.forecast_interval:
            self.forecasted_values = self.forecast_demands()
            self.time_series_end = self.env.now


    def forecast_at(self,timestamp):
        date = datetime.fromtimestamp(timestamp)
        delta = (date - self.time_series_end).total_seconds() 
        arr_index = (delta / 60) / self.sampling_interval
        return self.forecasted_values[int(arr_index)]