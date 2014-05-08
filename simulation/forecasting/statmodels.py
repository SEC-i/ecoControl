# Python wrapper for R forecast stuff


"""max: some examples of using R in python"""

import numpy as np
from simulation.systems.data import weekly_electrical_demand_winter, weekly_electrical_demand_summer, warm_water_demand_weekend, warm_water_demand_workday, electrical_demand_su_fr, electrical_demand_wi_fr
from dataloader import DataLoader
import matplotlib.pyplot as plt
from pylab import *
from matplotlib.widgets import Slider, Button, RadioButtons
from datetime import date, datetime, timedelta
from holt_winters import additive, multiplicative
from simulation.forecasting import Forecast
# 
# print 'Start importing R.'
# from rpy2 import robjects 
# from rpy2.robjects.packages import importr
# from rpy2.robjects.numpy2ri import numpy2ri
# robjects.conversion.py2ri = numpy2ri
#   
# base = importr('base')
# forecast = importr('forecast')
# stats = importr('stats')
# ts = robjects.r['ts']
# print 'Finished importing R.'




        
def perdelta(start, end, delta):
    curr = start
    while curr < end:
        yield curr
        curr += delta
        
def linear_interpolation(a,b,x):
    return a * x + b * (1.0 - x)

def make_two_year_data(dataset_winter, dataset_summer, sampling_interval, start, map_weekday=lambda x: x):
    wholeyear_data = []
    one_year = timedelta(days=365)
    winter = datetime(year=start.year, month=1,day=1)
    summer = winter + timedelta(days=365/2)
    season_delta = (summer - winter).total_seconds()
    
    
    
    
    for t in perdelta(start, start+one_year, timedelta(minutes=sampling_interval)):
        arr_index = map_weekday(t.weekday()) + t.hour + (t.minute / sampling_interval)
        summer_value = dataset_winter[arr_index]
        winter_value = dataset_summer[arr_index]
        
        if t > summer + one_year / 2:
            summer = summer + one_year #always take summer of current year
        
        delta = (summer - t).total_seconds()
        mix_factor = abs(delta/season_delta)
        mix_factor = min(max(mix_factor,0.0),1.0)
        
        result_value = linear_interpolation( summer_value, winter_value, mix_factor)
        
        wholeyear_data.append(result_value)
    twoyear = wholeyear_data + wholeyear_data
    return wholeyear_data



def make_day_data(days, data0, data1):
    weekday_data = []
    current = 0
    while current < days:
        for i in range(len(data0)):
            result = linear_interpolation(data0[i], data1[i], current/float(days) )
            weekday_data.append(result)
        current += 1
    return weekday_data
            
        
    
def split_weekdata(data, samples_per_hour):
    weekday = 0
    split_array = [[] for i in range(7)]
    for index, element in enumerate(data):
        if index % (24  * samples_per_hour) == 0:
            weekday = (weekday + 1) % 7
        split_array[weekday].append(element)
    return split_array
    
    
def ets(y):
    print forecast.ets.formals()
    fit = forecast.ets(y, model="MAM")
    print fit
    forecast_result = forecast.forecast(fit)
    return forecast_result
  
  

def plot_dataset(sensordata,block=True):
    fig, ax = plt.subplots()
    
    sim_plot, = ax.plot(range(len(sensordata["forcasting"])), sensordata["forcasting"], label="forcasting")
    forecast_plot, = ax.plot(range(len(sensordata["simulation"])), sensordata["simulation"], label="simulation")
    
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
    plt.xticks(rotation=90)
    plt.grid(True)
    
    
    return (fig, sim_plot,forecast_plot)



# Example
#data = np.array(weekly_electrical_demand_winter)
        

#data =  np.array(make_two_year_data(weekly_electrical_demand_winter,weekly_electrical_demand_summer, 15, datetime(year=2012,month=4,day=24)))
#input = make_day_data(4,  electrical_demand_wi_fr,electrical_demand_su_fr)
raw_data = DataLoader.load_from_file("../tools/Strom_2013.csv", "Strom - Verbrauchertotal (Aktuell)",delim="\t")
kW_data = [float(val) / 1000.0 for val in raw_data] #cast to float and convert to kW
input = Forecast.make_hourly(kW_data,6)
input = split_weekdata(input,1)[1]

data = np.array(input)
print data, len(data)

#series = ts(data,start=2013, frequency=(1/))
#
#series = data
 
# horizon = 100
# # res = do_forecast(series, horizon=horizon, exog=(exog_train, exog_test))
# print "-------------------------------"
#forecast_result = ets(series)
#  
#forecast_values = forecast_result.rx2("mean")
#values ={ 'forcasting':list(forecast_values), 'simulation':data}
#  

alpha = 0.0000001
beta = 0.0
gamma = 1.0
#plot_dataset(values)
m = 24
#forecast length
fc = int(len(data))
(forecast_values, alpha, beta, gamma, rmse) = multiplicative(input, m,fc, alpha, beta, gamma)
values ={ 'forcasting':forecast_values, 'simulation':input}

(fig, sim_plot,forecast_plot) = plot_dataset(values)

axcolor = 'lightgoldenrodyellow'
axalpa = axes([0.25, 0.0, 0.65, 0.03], axisbg=axcolor)
axbeta  = axes([0.25, 0.05, 0.65, 0.03], axisbg=axcolor)
axgamma  = axes([0.25, 0.1, 0.65, 0.03], axisbg=axcolor)

alpha_slider = Slider(axalpa, 'Alpha', 0.0, 1.0, valinit=alpha)
beta_slider = Slider(axbeta, 'Beta', 0.0, 1.0, valinit=beta)
gamma_slider = Slider(axgamma, 'Gamma', 0.0, 1.0, valinit=gamma)

def HoltWinters(val):
    alpha = alpha_slider.val
    beta = beta_slider.val
    gamma = gamma_slider.val
    print alpha, beta, gamma
    #season length
    m = 24
    #forecast length
    fc = int(len(data))
    (forecast_values, alpha, beta, gamma, rmse) = multiplicative(input, m,fc, alpha, beta, gamma)
    values ={ 'forcasting':forecast_values, 'simulation':input}
    
    forecast_plot.set_ydata(forecast_values)
    sim_plot.set_ydata(input)
    fig.canvas.draw_idle()
    
    

alpha_slider.on_changed(HoltWinters)
beta_slider.on_changed(HoltWinters)
gamma_slider.on_changed(HoltWinters)

plt.show()

# r = robjects.r
# r.X11()
  
# fit = forecast.tbats(series, periods=24*4)
# forecast_result = forecast.forecast(fit, horizon=400)
# forecast_result = ets(series)
# r.layout(r.matrix(robjects.IntVector([1,2,3,2]), nrow=2, ncol=2))
# r.plot(forecast_result)
#  #  
# values ={ 'forcasting':list(forecast_result.rx2("mean")), 'simulation':series}
#    
# plot_dataset(values)
      

#  