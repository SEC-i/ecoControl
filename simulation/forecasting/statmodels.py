# Python wrapper for R forecast stuff
import numpy as np
from simulation.systems.data import weekly_electrical_demand_winter
import matplotlib.pyplot as plt
import matplotlib.dates as md

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


def nparray2rmatrix(x):
  nr, nc = x.shape
  xvec = robjects.FloatVector(x.transpose().reshape((x.size)))
  xr = robjects.r.matrix(xvec, nrow=nr, ncol=nc)
  return xr

def nparray2rmatrix_alternative(x):
  nr, nc = x.shape
  xvec = robjects.FloatVector(x.reshape((x.size)))
  print nr, nc
  dimnames = ["xAxis", "yAxis"]
  xr = robjects.r.matrix(xvec, nrow=nr, ncol=nc, byrow=True)
  return xr

def do_forecast(series, frequency=None, horizon=30, summary=False, exog=None):
  if frequency:
    series = ts(series, frequency=frequency)
  else:
    series = ts(series)
  if exog:
    exog_train, exog_test = exog
    r_exog_train = nparray2rmatrix_alternative(exog_train)
    r_exog_test = nparray2rmatrix_alternative(exog_test)
    order = robjects.IntVector([1, 0, 2])  # c(1,0,2) # TODO find right model
    fit = forecast.Arima(series, order=order, xreg=r_exog_train)
    forecast_result = forecast.forecast(fit, h=horizon, xreg=r_exog_test)
  else:
    # fit = forecast.auto_arima(series)
    # robjects.r.plot(series)
    fit = stats.HoltWinters(series)
    forecast_result = forecast.forecast(fit, h=horizon)
  if summary:
    modsummary = base.summary(fit)
    print modsummary
  forecast_values = np.array(list(forecast_result.rx2('mean')))
  return forecast_values

def ets(y):
    fit = forecast.ets(y)
    print fit
    forecast_result = forecast.forecast(fit,h=100)
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
data = np.array(weekly_electrical_demand_winter)

series = ts(data)
exog_train = np.ones((100, 2))
exog_test = np.ones((100, 2))
horizon = 100
# res = do_forecast(series, horizon=horizon, exog=(exog_train, exog_test))
print "-------------------------------"
forecast_result = ets(series)
forecast_values = forecast_result.rx2("mean")
values ={ 'forcasting':forecast_values, 'simulation':data}

    
r = robjects.r
r.X11()

r.layout(r.matrix(robjects.IntVector([1,2,3,2]), nrow=2, ncol=2))
r.plot(forecast_result)
g = raw_input("wai")




#plot_dataset(values)
