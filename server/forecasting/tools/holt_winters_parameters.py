import numpy as np
try:
    from matplotlib.widgets import Slider, Button, RadioButtons
    import matplotlib.pyplot as plt
    from pylab import *
except:
    pass
from datetime import date, datetime, timedelta



def RMSE(input, forecast):
    rmse = sqrt(sum([(m - n) ** 2 for m, n in zip(input, forecast[:-1])]) / len(input))
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
    start = datetime.datetime(year=2014,month=1,day=1)
    dates = [date for date in perdelta(start,start+timedelta(hours=len(sensordata["measured"])), timedelta(hours=1)) ]
    forecast_plot, = ax.plot(dates[forecast_start:], sensordata["forecasting"], label="forecasting", linewidth=1.5) #range(forecast_start,len(sensordata["forecasting"])+forecast_start)
    sim_plot, = ax.plot(dates, sensordata["measured"], label="measured", linewidth=1.5)
    
    # Now add the legend with some customizations.
    legend = ax.legend(loc='upper center', shadow=True,prop={'size':18})
    
    # The frame is matplotlib.patches.Rectangle instance surrounding the legend.
    frame = legend.get_frame()
    frame.set_facecolor('0.90')
    
    # Set the fontsize
    for label in legend.get_texts():
        label.set_fontsize('large')
    
    for label in legend.get_lines():
        label.set_linewidth(5.5)
    
    plt.subplots_adjust(bottom=0.2)
    #plt.xlabel('Simulated time in seconds')
    #plt.xticks(rotation=90)
    plt.tick_params(axis='both', which='major', labelsize=16)
    plt.tick_params(axis='both', which='minor', labelsize=14)
    plt.grid(True)
    
    
    return (fig, sim_plot,forecast_plot)


""" a tool for finding the right alpha, beta and gamma parameter for holt winters"""
def value_changer():
    from dataloader import DataLoader
    from holt_winters import additive, multiplicative
    raw_data = DataLoader.load_from_file("../systems/data/Electricity_2013.csv", "Strom - Verbrauchertotal (Aktuell)",delim="\t")
    ind = len(raw_data) / 2
    kW_data = [float(val) / 1000.0 for val in raw_data] #cast to float and convert to kW
    input = make_hourly(kW_data,6)[-24*7:]
    #input = Forecast.split_weekdata(input,1)[1]
    training_data = input[:len(input)/2]
    testing_data = input[len(input)/2:]
      

    alpha = 0.0000001
    beta = 0.0
    gamma = 1.0
    #plot_dataset(values)
    m = 24
    #forecast length
    fc = int(len(testing_data))
    (forecast_values, alpha, beta, gamma, rmse) = multiplicative(training_data, m,fc, alpha, beta, gamma)
    print forecast_values
    values ={ 'forecasting':forecast_values, 'measured':input}
    
    (fig, sim_plot,forecast_plot) = plot_dataset(values, forecast_start=len(training_data))
    
    axcolor = 'lightgoldenrodyellow'
    axalpa = axes([0.25, 0.02, 0.65, 0.02], axisbg=axcolor)
    axbeta  = axes([0.25, 0.06, 0.65, 0.02], axisbg=axcolor)
    axgamma  = axes([0.25, 0.1, 0.65, 0.02], axisbg=axcolor)
    
    alpha_slider = Slider(axalpa, 'Alpha', 0.0, 1.0, valinit=alpha)
    beta_slider = Slider(axbeta, 'Beta', 0.0, 1.0, valinit=beta)
    gamma_slider = Slider(axgamma, 'Gamma', 0.0, 1.0, valinit=gamma)
    
    def update_hw(val):
        alpha = alpha_slider.val
        beta = beta_slider.val
        gamma = gamma_slider.val
        
        
        (forecast_values, alpha, beta, gamma, rmse) = multiplicative(training_data, m,fc, alpha, beta, gamma)
        values ={ 'forecasting':forecast_values, 'measured':input}
        
        forecast_plot.set_ydata(forecast_values)
        sim_plot.set_ydata(input)
        fig.canvas.draw_idle()
        
        print alpha, beta, gamma, RMSE(testing_data, forecast_values)
        
        
    alpha_slider.on_changed(update_hw)
    beta_slider.on_changed(update_hw)
    gamma_slider.on_changed(update_hw)
    
    plt.show()

value_changer()
