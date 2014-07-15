import os
import time
import numpy as np
from multiprocessing import Pool
from datetime import date, datetime, timedelta
from multiprocessing.process import Process
import multiprocessing
from sys import platform as _platform
import cPickle as pickle

from django.utils.timezone import utc
from holt_winters import multiplicative, additive
from server.settings import BASE_DIR
import logging
from server.forecasting.forecasting.holt_winters import double_seasonal

logger = logging.getLogger('simulation')

class Forecast:

    """
    @param input_data: list of consecutive values sampled in samples_per_hour
    @param start: start date of input data
    @param hw_parameters: tuple with (alpha, beta, gamma)
    @param hw_optimisation: "None" --> given hw_parameters are always used (fastest, hw_parameters required)
                            "MSE" --> Mean Square Error used as optimization parameter for Holt-Winters
                            "MASE" --> Mean Absolute Scaled Error is used. Yields most accurate results (slowest)
    """

    def __init__(self, env, input_data, samples_per_hour=1, start=None, hw_parameters=(), hw_optimization="MASE", **kwargs):
        if hw_parameters == ():
            self.hw_parameters = (None, None, None)
        else:
            self.hw_parameters = hw_parameters  # default hw alpha, beta, gamma

        self.hw_optimization = hw_optimization
        self.calculated_parameters = []
        self.samples_per_hour = samples_per_hour
        self.env = env

        data_length = timedelta(hours=len(input_data) / samples_per_hour)
        #only use days
        data_length = timedelta(days=data_length.days) 
        if start == None:
            start = datetime.utcfromtimestamp(self.env.now).replace(tzinfo=utc) - data_length
            
        #always set to start of day
        start = start.replace(hour=0,minute=0) 
        
        #only forecast with this many weeks of data, approx 3 months
        self.input_weeks = 12
        self.input_hours = self.input_weeks*24*7*self.samples_per_hour
        #the forecast will cover 8 weeks of future data
        self.output_weeks = 8
               
        # ending time of input data
        self.time_series_end = datetime.utcfromtimestamp(self.env.now).replace(tzinfo=utc)
        

        self.forecast_update_interval = 24 * 60 * 60
        
        if "try_cache" in kwargs:
            self.try_cache = kwargs["try_cache"]
        else:
            self.try_cache = True
            
        self.demands = self.process_inputdata(input_data,samples_per_hour,start)
        self.demands = [demand[-self.input_hours:] for demand in self.demands]
        
        #forecast all demands.. might take long
        self.forecasted_demands = self.forecast_demands()
        
    def get_forecast_at(self, timestamp):
        return self.forecast_at(timestamp)[0]
    
    
    def read_from_cache(self):
        #try reading result from cache
        if self.try_cache: 
            try:
                values = pickle.load(open( os.path.join(BASE_DIR,"cache/cached_forecasts.cache"), "rb" ))
                diff_time = datetime.utcfromtimestamp(values["date"]).replace(tzinfo=utc) - self.time_series_end
                if diff_time.total_seconds() < 24 * 60 * 60: #12 hours epsilon
                    forecasted_demands = values["forecasts"]
                    self.calculated_parameters = values["parameters"] 
                    logger.info("reading forecastings from cache")
                    return forecasted_demands
            except IOError as e:
                logger.info(str(e) + " .. creating new cache file")
        return None
    
    
    def process_inputdata(self, data, samples_per_hour,start):
        raise NotImplementedError
    
    def forecast_demands(self):
        raise NotImplementedError
    
    def update_if_needed(self):
        now = datetime.utcfromtimestamp(self.env.now).replace(tzinfo=utc)
        delta = (now - self.time_series_end).total_seconds()
        if delta > self.forecast_update_interval:
            self.forecasted_demands = self.forecast_demands()
            self.time_series_end = datetime.utcfromtimestamp(self.env.now).replace(tzinfo=utc)

    @classmethod
    def make_hourly(cls, data, samples_per_hour):
        def avg(hour):
            sum = 0
            for i in range(samples_per_hour):
                sum += data[hour * samples_per_hour + i]
            return sum / samples_per_hour

        hours = len(data) / samples_per_hour
        return [avg(i) for i in range(hours)]



    @classmethod
    def MASE(cls, training_series, testing_series, prediction_series):
        """
        Computes the MEAN-ABSOLUTE SCALED ERROR forcast error for univariate time series prediction.
        
        See "Another look at measures of forecast accuracy", Rob J Hyndman
        
        parameters:
            training_series: the series used to train the model, 1d np array
            testing_series: the test series to predict, 1d np array or float
            prediction_series: the prediction of testing_series, 1d np array (same size as testing_series) or float
        """
        training_series = np.array(training_series)
        testing_series = np.array(testing_series)
        prediction_series = np.array(prediction_series)
        n = training_series.shape[0]
        d = np.abs(np.diff(training_series)).sum() / (n - 1)

        errors = np.abs(testing_series - prediction_series)
        return errors.mean() / d


class DSHWForecast(Forecast):
    
    def forecast_at(self, timestamp):
        date = datetime.utcfromtimestamp(timestamp).replace(tzinfo=utc)
        delta = (date - self.time_series_end).total_seconds()
        print int(delta / 3600 * self.samples_per_hour)
        return [self.forecasted_demands[int(delta / 3600 * self.samples_per_hour)]]
    
    def process_inputdata(self, data, samples_per_hour,start):
        return [data]
    
    def forecast_demands(self,verbose=False):
        cached = Forecast.read_from_cache(self)
        if cached != None:
            return cached
        demand = self.demands[0] #dshw demands only contains one dataset
        sph = self.samples_per_hour
        fc = self.output_weeks * 24 * 7 * self.samples_per_hour #forecast_length
        if None not in self.hw_parameters:
            (alpha, beta, gamma, delta, autocorr) = self.hw_parameters
        else:
            (alpha, beta, gamma, delta, autocorr) = (None for i in range(5))
            
        forecast_values, (alpha, beta, gamma, delta, autocorrelation),in_sample = double_seasonal(demand, m=24*sph, m2=24*7*sph,
                                                                           forecast=fc, alpha=alpha, beta=beta, gamma=gamma, delta=delta,
                                                                            autocorrelation=autocorr)
        mase = Forecast.MASE(demand, demand[-fc:],  forecast_values)
        
        calculated_parameters = {
            "alpha": alpha, "beta": beta, "gamma": gamma, "delta":delta, 
            "autocorrelation":autocorrelation, "mse": in_sample, "mase": mase}
        if verbose:
            print "use auto HW ",calculated_parameters
        
        return forecast_values
    
    def append_values(self, data, start_date=None):
        demand = self.demands[0]
        demand += data
        
        if len(demand) > self.input_hours:
            #only keep number of input_weeks
            start_index = len(demand) - self.input_hours
            self.demands[0] = demand[start_index:]
        
        self.update_if_needed()




class DayTypeForecast(Forecast):
    
    @classmethod
    def split_weekdata(cls, data, samples_per_hour, start_date=None):
        if start_date != None:
            weekday = start_date.weekday()
        else:
            weekday = 0
        split_array = [[] for i in range(7)]
        for index, element in enumerate(data):
            if index % (24 * samples_per_hour) == 0:
                weekday = (weekday + 1) % 7
            split_array[weekday].append(element)
        return split_array
        
    def process_inputdata(self, data, samples_per_hour,start):
        return DayTypeForecast.split_weekdata(data, samples_per_hour, start)
  
    def forecast_multiplicative(self, demand, index, result_dict, verbose=False):
        #seasonality length -- one day
        m = 24 * self.samples_per_hour
        fc = self.output_weeks * 24 * 7 *  self.samples_per_hour #forecast_length
        # alpha, beta, gamma. if any is None, holt.winters determines them automatically
        # cost-expensive, so only do this once..
        (alpha, beta, gamma) = self.hw_parameters
        print "find holt winter parameters for day: ", index

        # find values automatically
        # check with MASE error measure
        forecast_values, (alpha, beta, gamma),in_sample = multiplicative(demand, m, fc, optimization_type="MSE")
             
        mase = Forecast.MASE(demand, demand[-fc:],  forecast_values)

        calculated_parameters = {
            "alpha": alpha, "beta": beta, "gamma": gamma, "mse": in_sample, "mase": mase}
        if verbose:
            print "use auto HW ",calculated_parameters
            
        result_dict[index] = (forecast_values, calculated_parameters, index)
        
 
    
    
    def forecast_demands(self):
        cached = Forecast.read_from_cache(self)
        if cached != None:
            return cached
        
        split_results = [[] for i in range(7)]
        #multi processed forecasting
        ## WARNING: hangups:
        #v.1 :  pool.map
        #v.2  use multiple processes instead of pool.map to circumvent a hangup caused
        # by a multiprocessing/django incompabatility
        #share results in a multiaccess queue
        #note: this queue can not hold unlimited elements and will hang up with no warning if there are too many elements
        #12 weeks 1hourly will work, 20 not
        #result_queue = multiprocessing.Queue()
        #v.3 now uses a shared multiprocessing dict, to circumvent hang up problems with queue on windows
        
        mgr = multiprocessing.Manager()
        dict_threadsafe = mgr.dict()

        #call class as Functor because class methods are not pickeable
        jobs = [Process(target=self, args=(demand,index,dict_threadsafe)) for index, demand in enumerate(self.demands)]
        for job in jobs: job.start()
        for job in jobs: job.join()
         
        for index in dict_threadsafe.keys():
            split_results[index] = dict_threadsafe[index]
            
        forecasted_demands = []
        self.calculated_parameters = []
        for fc_tuple in split_results:
            forecasted_demands.append(list(fc_tuple[0]))
            self.calculated_parameters.append(fc_tuple[1])
            
        pickle.dump( {"forecasts" :forecasted_demands, "parameters" : self.calculated_parameters, "date": self.env.now },
                      open(os.path.join(BASE_DIR,"cache/cached_forecasts.cache"), "wb" ) ) 

        return forecasted_demands
    
    
    def forecast_at(self, timestamp):
        date = datetime.utcfromtimestamp(timestamp).replace(tzinfo=utc)
        delta = (date - self.time_series_end).total_seconds()
        arr_index = int((delta / (60.0 * 60.0)) * self.samples_per_hour)
        week_index = int(arr_index / (7 * 24))
        hour_index = arr_index % 24
        return (self.forecasted_demands[date.weekday()][week_index * 24 + hour_index], week_index, hour_index)
    
    
    def append_values(self, data, start_date=None):
        new_demands = DayTypeForecast.split_weekdata(data, self.samples_per_hour, start_date)
        
        for index, demand in enumerate(new_demands):
            self.demands[index] += demand
            
            if len(self.demands[index]) > self.input_hours:
                #only keep number of input_weeks
                start_index = len(self.demands[index]) - self.input_hours
                self.demands[index] = self.demands[index][start_index:]
        self.update_if_needed()
    
    
    # callable class
    def __call__(self, demand, index, result_dict):
        self.forecast_multiplicative(demand, index, result_dict)