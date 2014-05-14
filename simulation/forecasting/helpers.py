from datetime import date,datetime,timedelta


def perdelta(start, end, delta):
    curr = start
    while curr < end:
        yield curr
        curr += delta
        
def linear_interpolation(a,b,x):
    return a * x + b * (1.0 - x)


def approximate_index(dataset, findvalue):
    length = len(dataset)
    #aproximate index
    i = min(int(findvalue - dataset[0]), length -1)
    while i < length and i >= 0:
        if i == length -1:
            return i if dataset[i] == findvalue else -1
        
        if dataset[i] < findvalue and dataset[i+1] > findvalue:
            return i
        elif dataset[i] > findvalue:
            i-=1
        else:
            i+=1
    return -1


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
