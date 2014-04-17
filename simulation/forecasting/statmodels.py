# Python wrapper for R forecast stuff
import numpy as np
from simulation.systems.data import weekly_electrical_demand_winter, weekly_electrical_demand_summer
import matplotlib.pyplot as plt
import matplotlib.dates as md
from datetime import date, datetime, timedelta
from holt_winters import additive, multiplicative

print 'Start importing R.'
from rpy2 import robjects 
from rpy2.robjects.packages import importr
from rpy2.robjects.numpy2ri import numpy2ri
robjects.conversion.py2ri = numpy2ri

base = importr('base')
forecast = importr('forecast')
stats = importr('stats')
ts = robjects.r['ts']
print 'Finished importing R.'




        




def ets(y):
    print forecast.ets.formals()
    fit = forecast.ets(y, model="MAM")
    print fit
    forecast_result = forecast.forecast(fit)
    return forecast_result
  
  

def plot_dataset(sensordata):
    fig, ax = plt.subplots()
    for name, sensorvals in sensordata.items():
        if name != "time":
            ax.plot(range(len(sensorvals)), sensorvals, label=name)
    
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
    plt.show(block=True)



# Example
#data = np.array(weekly_electrical_demand_winter)
        
    
data =  np.array(make_two_year_data())


y = make_two_year_data()
alpha = 0.30 #forecastings are weighted more on past data
beta = 0.00 #very little slope changes
gamma = 0.8 #estimation of seasonal component based on  recent changes
i = "start"
m = int(len(y) * 0.2) #value sampling shift.. somehow
fc = len(y) # whole data length

(forecast_values, alpha, beta, gamma, rmse) = multiplicative(y, m, fc,alpha, beta, gamma)
values ={ 'forcasting':list(forecast_values), 'simulation':data}
plot_dataset(values)


# series = ts(data,start=2013, deltat=(1/(365* 12.0 * 24.0 * 15 )))
# 
# horizon = 100
# # res = do_forecast(series, horizon=horizon, exog=(exog_train, exog_test))
# print "-------------------------------"
# forecast_result = ets(series)
# 
# forecast_values = forecast_result.rx2("mean")
# values ={ 'forcasting':list(forecast_values), 'simulation':data}
# 
# plot_dataset(values)



# r = robjects.r
# r.X11()
# #  
# r.layout(r.matrix(robjects.IntVector([1,2,3,2]), nrow=2, ncol=2))
# r.plot(forecast_result)  
# #  
# plot_dataset(values)
#    
# fit = forecast.tbats(series)
# forecast_result = forecast.forecast(fit, h=200)
# r.layout(r.matrix(robjects.IntVector([1,2,3,2]), nrow=2, ncol=2))
# r.plot(forecast_result)
# #  
# values ={ 'forcasting':list(forecast_result.rx2("mean")), 'simulation':data}
# #  
# plot_dataset(values)

# fit = stats.HoltWinters(series)
# forecast_result = forecast.forecast(fit, h=2000)
#  
# r.layout(r.matrix(robjects.IntVector([1,2,3,2]), nrow=2, ncol=2))
# r.plot(forecast_result)
#  
# values ={ 'forcasting':list(forecast_result.rx2("mean")), 'simulation':data}
# plot_dataset(values)
