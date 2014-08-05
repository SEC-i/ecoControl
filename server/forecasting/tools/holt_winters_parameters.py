import numpy as np
from server.forecasting.tools.plotting import show_plotting
from server.forecasting.dataloader import DataLoader
from server.forecasting.helpers import approximate_index
import calendar
from server.forecasting.statistical import StatisticalForecast
from server.settings import BASE_DIR, CYTHON_SUPPORT

import os

""""try to import compiled holtwinters (double seasonal) extension by building it. 
if this fails, the standard holtwinters is used. """
fast_hw = False
if (CYTHON_SUPPORT):
    try:
        from server.forecasting.statistical.build_extension import build_holtwinters_extension
        try:
            t0 = time.time()
            build_holtwinters_extension() #compile and link
            #if function takes less than 10 seconds, the module was probably already built before
            fresh_build = time.time() - t0 > 10 
            from server.forecasting.statistical.holtwinters_fast import double_seasonal, multiplicative
            fast_hw = True
            if fresh_build:
                print "cython extension built and imported"
        except Exception as e:
            print "error while building. ", e
            print "check ecoControl.log"
    except Exception as e:
        print "cython probably not installed", e
    
if not fast_hw:
    if (CYTHON_SUPPORT):
        print "falling back to python holt-winters"
    from server.forecasting.statistical.holt_winters import double_seasonal, multiplicative, additive
else:
    #!TODO: additive is not accelerated (yet)
    from server.forecasting.statistical.holt_winters import additive


    
from datetime import date, datetime, timedelta
import matplotlib.pyplot as plt


def MSE(input, forecast):
    rmse = sum([(m - n) ** 2 for m, n in zip(input, forecast[:-1])]) / len(input)
    #penalty = mean_below_penalty(np.array(forecast[:-1]))
    
    return rmse# + penalty

def perdelta(start, end, delta):
    curr = start
    while curr < end:
        yield curr
        curr += delta
        
        
def make_hourly(data, samples_per_hour):
    def avg(hour):
        sum = 0
        for i in range(samples_per_hour):
            sum += data[hour * samples_per_hour + i]
        return sum / samples_per_hour

    hours = len(data) / samples_per_hour
    return [avg(i) for i in range(hours)]

def plot_dataset(sensordata,forecast_start=0,block=True):
    fig, ax = plt.subplots()
    start = datetime(year=2014,month=1,day=1)
    dates = [date for date in perdelta(start,start+timedelta(hours=len(sensordata["measured"])), timedelta(hours=1)) ]
    forecast_plot, = ax.plot(dates[forecast_start:], sensordata["forecasting"], label="forecasting", linewidth=1.5) #range(forecast_start,len(sensordata["forecasting"])+forecast_start)
    sim_plot, = ax.plot(dates, sensordata["measured"], label="measured", linewidth=1.5)
    
    show_plotting(plt, ax, block)
    
    
    return (fig, sim_plot,forecast_plot)


""" a tool for finding the right alpha, beta and gamma parameter for holt winters"""
def value_changer():
    try:
        from matplotlib.widgets import Slider, Button, RadioButtons
        
        from pylab import axes
    except:
        print "ljdlj"
    sep = os.path.sep
    path = os.path.join(BASE_DIR, "server" + sep + "forecasting" + sep + "devices" + sep + "data" + sep + "Electricity_1.1-12.6.2014.csv")
    raw_data = DataLoader.load_from_file(path, "Strom - Verbrauchertotal (Aktuell)",delim="\t")
    ind = len(raw_data) / 2
    kW_data = StatisticalForecast.make_hourly([float(val) / 1000.0 for val in raw_data],6) #cast to float and convert to kW
    dates = [int(d) for d in DataLoader.load_from_file(path, "Datum", "\t")]
    input = make_hourly(kW_data,6)[-24*7:]
    start = calendar.timegm(datetime(year=2014,month=1,day=2).timetuple())
    start_index = approximate_index(dates, start)
    train_len= 24*7*8
    trainingdata = kW_data[start_index:start_index+train_len]
    test_start = start_index+train_len 
    testdata = kW_data[test_start:test_start+7*24*2]
    start_forecast = test_start*3600
    end_forecast = start_forecast + len(testdata) * 3600
      

    alpha = 0.0000001
    beta = 0.0
    gamma = 0.05
    delta = 0.01
    autocorr = 0.01
    #plot_dataset(values)
    m = 24
    m2 = 24 * 7
    #forecast length
    fc = int(len(testdata))
    forecast_values, params, insample = double_seasonal(trainingdata, m,m2,fc, alpha, beta, gamma,delta,autocorr)
    values ={ 'forecasting':forecast_values, 'measured':testdata}
    
    (fig, sim_plot,forecast_plot) = plot_dataset(values, 0,block=False)
    
    axcolor = 'lightgoldenrodyellow'
    axalpa = axes([0.25, 0.02, 0.65, 0.02], axisbg=axcolor)
    axautocorr  = axes([0.25, 0.05, 0.65, 0.02], axisbg=axcolor)
    axgamma  = axes([0.25, 0.08, 0.65, 0.02], axisbg=axcolor)
    axdelta  = axes([0.25, 0.11, 0.65, 0.02], axisbg=axcolor)
    
    alpha_slider = Slider(axalpa, 'Alpha', 0.0, 1.0, valinit=alpha)
    gamma_slider = Slider(axgamma, 'Gamma', 0.0, 1.0, valinit=gamma)
    delta_slider = Slider(axdelta, 'Delta', 0.0, 1.0, valinit=delta)
    autocorr_slider = Slider(axautocorr, 'autocorr_slider', 0.0, 1.0, valinit=autocorr)
    
    def update_hw(val):
        alpha = alpha_slider.val
        autocorr = autocorr_slider.val
        beta = 0.0
        gamma = gamma_slider.val
        delta = delta_slider.val
        
        
        forecast_values, params, insample = double_seasonal(trainingdata, m,m2,fc, alpha, beta, gamma,delta,autocorr)
        values ={ 'forecasting':forecast_values, 'measured':testdata}
        
        forecast_plot.set_ydata(forecast_values)
        sim_plot.set_ydata(testdata)
        fig.canvas.draw_idle()
        
        print alpha, autocorr, gamma, MSE(testdata, forecast_values)
        
        
    alpha_slider.on_changed(update_hw)
    autocorr_slider.on_changed(update_hw)
    gamma_slider.on_changed(update_hw)
    delta_slider.on_changed(update_hw)
    
    plt.show()