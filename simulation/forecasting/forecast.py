from simulation.systems.data import weekly_electrical_demand_winter, weekly_electrical_demand_summer, warm_water_demand_workday, warm_water_demand_weekend
from datetime import date,datetime,timedelta
import matplotlib.pyplot as plt
import matplotlib.dates as md
from holt_winters import multiplicative, additive

def perdelta(start, end, delta):
    curr = start
    while curr < end:
        yield curr
        curr += delta
        
def linear_interpolation(a,b,x):
    return a * x + b * (1.0 - x)


class Forecast:
    
    def __init__(self):
        self.twoyear_electrical_demand = self.make_two_year_data(weekly_electrical_demand_winter, 
                                                                     weekly_electrical_demand_summer, 
                                                                     sampling_interval = 15,
                                                                     start = datetime(2012,1,1,0,0,0))
        # map workdays to 0 and weekends to 1
        map_week_to_index = lambda x: 0 if x < 5 else 1
        input_data = warm_water_demand_workday + warm_water_demand_weekend
        self.wholeyear_warmwater_demand = self.make_two_year_data(input_data, 
                                                                     input_data,
                                                                     sampling_interval = 15,
                                                                     start = datetime(2013,1,1,0,0,0),
                                                                     map_weekday=map_week_to_index)
    def forecast_electrical_demand(self):
        y = self.twoyear_electrical_demand
        alpha = 0.9  #forecastings are weighted more on new data
        beta = 0 #no slope changes
        gamma = 1 #estimation of seasonal component based on  recent changes
        m = int(len(y) * 0.5) #value sampling shift.. somehow
        fc = len(y) * 2 # whole data length
        (forecast_values, alpha, beta, gamma, rmse) = multiplicative(y, m, fc,alpha, beta, gamma)
        values ={ 'forcasting':list(forecast_values), 'simulation':y}
        self.plot_dataset(values)
    
    def forecast_warmwater_demand(self):
        pass
        

    """function interpolates between summer and winterset, returning a year of data sampled at sampling interval, begining at start
    assuming a sub-hour sampled dataset.
    map_weekday is a function which maps each weekday to an array index, so a array with only a workday and a weekend day
    will be map_weekday = lambda x: 0 if x < 5 else 1"""
    def make_two_year_data(self,dataset_winter, dataset_summer, sampling_interval, start, map_weekday=lambda x: x):
        wholeyear = []
        winter = start
        summer = start + timedelta(days=365 / 2.0)
        season_delta = (summer - winter).total_seconds()
        for t in perdelta(start, start+timedelta(days=365), timedelta(minutes=sampling_interval)):
            arr_index = map_weekday(t.weekday()) + t.hour + (t.minute / sampling_interval)
            summer_value = dataset_winter[arr_index]
            winter_value = dataset_summer[arr_index]
            delta = (summer - t).total_seconds() #returns timedelta
            
            mix_factor = abs(delta/season_delta)
            mix_factor = min(max(mix_factor,0.0),1.0)
            result_value = linear_interpolation( summer_value, winter_value, mix_factor)
            
            wholeyear.append(result_value)
        twoyear = wholeyear + wholeyear
        return twoyear
    
    
    def plot_dataset(self,sensordata):
    
            fig, ax = plt.subplots()
            for name,sensorvals in sensordata.items():
                if name != "time":
                    ax.plot(range(len(sensorvals)),sensorvals,label=name)
            
            # Now add the legend with some customizations.
            legend = ax.legend(loc='upper center', shadow=True)
            
            # The frame is matplotlib.patches.Rectangle instance surrounding the legend.
            frame = legend.get_frame()
            frame.set_facecolor('0.90')
            
            # Set the fontsize
            for label in legend.get_texts():
                label.set_fontsize('medium')
            
            for label in legend.get_lines():
                label.set_linewidth(1.5)
    
            plt.subplots_adjust(bottom=0.2)
            plt.xlabel('Simulated time in seconds')
            plt.xticks( rotation=90 )
            plt.grid(True)
            plt.show(block=True)


f = Forecast()
f.forecast_electrical_demand()