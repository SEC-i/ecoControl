from datetime import date,datetime,timedelta


def perdelta(start, end, delta):
    curr = start
    while curr < end:
        yield curr
        curr += delta
        
def linear_interpolation(a,b,x):
    return a * x + b * (1.0 - x)


"""function interpolates between summer and winterset, returning a year of data sampled at sampling interval, begining at start
assuming a sub-hour sampled dataset.
map_weekday is a function which maps each weekday to an array index, so a array with only a workday and a weekend day
will be map_weekday = lambda x: 0 if x < 5 else 1"""
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
    return twoyear


def plot_dataset(sensordata):
    import matplotlib.pyplot as plt
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

def test_dataset():
    from simulation.systems.data import weekly_electrical_demand_winter, weekly_electrical_demand_summer, warm_water_demand_workday, warm_water_demand_weekend
    from holt_winters import multiplicative
    y = make_two_year_data(weekly_electrical_demand_winter,weekly_electrical_demand_summer, 15, datetime(year=2012,month=4,day=24))
    
    m = int(len(y) * 0.5) #value sampling shift.. somehow
    fc = len(y) * 2 # whole data length
    
    (forecast_values, alpha, beta, gamma, rmse) = multiplicative(y, m, fc,None, None, None)
    values ={ 'forcasting':list(forecast_values), 'simulation':y}
    plot_dataset(values)