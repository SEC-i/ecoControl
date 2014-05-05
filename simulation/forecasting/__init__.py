from datetime import date,datetime,timedelta
from holt_winters import multiplicative, additive



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
        self.time_series_end = start + timedelta(days=365)
        self.sampling_interval = sampling_interval
        # wait at least one day before making a new forecast
        self.forecast_interval = 24 * 60 * 60
        self.env = env
        
        
        self.hw_parameters = (0.0000001,0.0,1.0)
        
        
    def forecast_demands(self):
        forecasted_demands  = []
        
        for demand in self.demands:
            
            #alpha, beta, gamma. if any is None, holt.winters determines them automatically
            #cost-expensive, so only do this once..
            m = self.sampling_interval
            fc = len(demand)
            (alpha,beta,gamma) = self.hw_parameters
            (forecast_values_manual, alpha, beta, gamma, rmse_manual) = multiplicative(demand, m,fc, alpha, beta, gamma)
            if rmse_manual > 1.0:
                #find values automatically
                (forecast_values_auto, alpha, beta, gamma, rmse_auto) = multiplicative(input, m,fc)
                print "HW parameters - found automatically: alpha: ", alpha," beta: ", beta," gamma: ",  gamma," RMSE: ",  rmse_auto
            
            if rmse_manual > rmse_auto:
                forecast_values = forecast_values_auto
                print "use auto HW"
            else:
                forecast_values = forecast_values_manual 
                print "use manual HW"
            
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
    
    @classmethod
    def make_hourly(cls, data, samples_per_hour):
        avg = lambda i: sum(data[i:i+samples_per_hour])/float(samples_per_hour)
        hours = len(data) / samples_per_hour
        return [avg(i) for i in range(hours)]
            
    
    
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
    