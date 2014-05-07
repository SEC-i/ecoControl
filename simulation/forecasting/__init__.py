from datetime import date,datetime,timedelta
from holt_winters import multiplicative, additive



class Forecast:
    
    def __init__(self, env, input_data, samples_per_hour = 1, start=None, hw_parameters=()):
        if hw_parameters == ():
            self.hw_parameters = (None,None,None)
        else:
            self.hw_parameters = hw_parameters # default hw alpha, beta, gamma
        
        
        self.samples_per_hour = samples_per_hour
        self.env = env
        
        data_length = timedelta(hours=len(input_data)  / samples_per_hour)
        if start == None:
            start = datetime.fromtimestamp(env.now) - data_length

        #demands split into weekdays
        self.demands = self.split_weekdata(input_data, samples_per_hour)
        
        self.forecasted_demands = self.forecast_demands()
        #ending time of input data
        self.time_series_end = start + timedelta(days=365)

        # wait at least one day before making a new forecast
        self.forecast_interval = 24 * 60 * 60


        
        
    def forecast_demands(self):
        forecasted_demands  = []
        
        for demand in self.demands:
            
            #alpha, beta, gamma. if any is None, holt.winters determines them automatically
            #cost-expensive, so only do this once..
            m = 24
            fc = len(demand)
            (alpha,beta,gamma) = self.hw_parameters
            (forecast_values_manual, alpha, beta, gamma, rmse_manual) = multiplicative(demand, m,fc, alpha, beta, gamma)
            rmse_auto = 10 ** 6 #some really high value, wil be overwritten
            if rmse_manual > 1.5:
                #find values automatically
                (forecast_values_auto, alpha, beta, gamma, rmse_auto) = multiplicative(demand, m,fc)
                #print "HW parameters - found automatically: alpha: ", alpha," beta: ", beta," gamma: ",  gamma," RMSE: ",  rmse_auto
            
            if rmse_manual > rmse_auto:
                forecast_values = forecast_values_auto
                print "use auto HW with RMSE", rmse_auto
            else:
                forecast_values = forecast_values_manual 
                print "use manual HW with RMSE", rmse_manual
            
            forecasted_demands.append(list(forecast_values))
            
        return forecasted_demands
    
    @classmethod
    def split_weekdata(self, data, samples_per_hour):
        weekday = 0
        split_array = [[] for i in range(7)]
        for index, element in enumerate(data):
            if index % (24  * samples_per_hour) == 0:
                weekday = (weekday + 1) % 7
            split_array[weekday].append(element)
        return split_array
    
    @classmethod
    def make_hourly(cls, data, samples_per_hour):
        def avg(hour):
            sum = 0
            for i in range(samples_per_hour):
                sum += data[hour*samples_per_hour + i]
            return sum / samples_per_hour

        hours = len(data) / samples_per_hour
        return [avg(i) for i in range(hours)]
            
    
    
    def append_values(self,data): 
        new_demands = Forecast.split_weekdata(data,self.samples_per_hour)
        for index, demand in enumerate(new_demands):
            self.demands[index] += demand
                   
        delta = (self.env.now - self.start_date).total_seconds()
        if delta > self.forecast_interval:
            self.forecasted_demands = self.forecast_demands()
            self.time_series_end = self.env.now


    def forecast_at(self,timestamp):
        date = datetime.fromtimestamp(timestamp)
        delta = (date - self.time_series_end).total_seconds() 
        arr_index = (delta / 60) / self.samples_per_hour
        return self.forecasted_demands[int(arr_index)]
    