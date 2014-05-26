import numpy as np
from matplotlib.widgets import Slider, Button, RadioButtons
from datetime import date, datetime, timedelta
import matplotlib.pyplot as plt
from pylab import *

from server.forecasting.forecasting.dataloader import DataLoader
from server.forecasting.forecasting.forecasting.holt_winters import additive, multiplicative


def plot_dataset(sensordata,forecast_start=0,block=True):
    fig, ax = plt.subplots()
    forecast_plot, = ax.plot(range(forecast_start,len(sensordata["forcasting"])+forecast_start), sensordata["forcasting"], label="forcasting")
    sim_plot, = ax.plot(range(len(sensordata["simulation"])), sensordata["simulation"], label="simulation")
    
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


""" a tool for finding the right alpha, beta and gamma parameter for holt winters"""
def value_changer():
    raw_data = DataLoader.load_from_file("../tools/Electricity_2013.csv", "Strom - Verbrauchertotal (Aktuell)",delim="\t")
    ind = len(raw_data) / 2
    kW_data = [float(val) / 1000.0 for val in raw_data] #cast to float and convert to kW
    input = Forecast.make_hourly(kW_data,6)
    input = Forecast.split_weekdata(input,1)[1]
    training_data = input[:len(input)/2]
    testing_data = input[len(input)/4 * 3:]
    
    data = np.array(training_data)
    print data, len(data)
    
    
    alpha = 0.0000001
    beta = 0.0
    gamma = 1.0
    #plot_dataset(values)
    m = 24
    #forecast length
    fc = int(len(data))
    (forecast_values, alpha, beta, gamma, rmse) = multiplicative(testing_data, m,fc, alpha, beta, gamma)
    values ={ 'forcasting':forecast_values, 'simulation':input}
    
    (fig, sim_plot,forecast_plot) = plot_dataset(values)
    
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
        print alpha, beta, gamma
        
        (forecast_values, alpha, beta, gamma, rmse) = multiplicative(testing_data, m,fc, alpha, beta, gamma)
        values ={ 'forcasting':forecast_values, 'simulation':input}
        
        forecast_plot.set_ydata(forecast_values)
        sim_plot.set_ydata(input)
        fig.canvas.draw_idle()
        
        
    alpha_slider.on_changed(update_hw)
    beta_slider.on_changed(update_hw)
    gamma_slider.on_changed(update_hw)
    
    plt.show()

value_changer()
