from datetime import date, datetime, timedelta
from holt_winters import multiplicative, additive
import numpy as np
from multiprocessing import Pool
import time
from multiprocessing.process import Process
import multiprocessing
from sys import platform as _platform
import cPickle as pickle
import logging

from django.utils.timezone import utc

logger = logging.getLogger('simulation')

class Forecast:

    """
    @param input_data: list of consecutive values sampled in samples_per_hour
    @param start: start date of input data
    @param hw_parameters: tuple with (alpha, beta, gamma)
    @param hw_optimisation: "None" --> given hw_parameters are always used (fastest, hw_parameters required)
                            "RMSE" --> Root Mean Square Error used as optimization parameter for Holt-Winters (slow)
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
        self.input_hours = self.input_weeks*24*self.samples_per_hour
        #the forecast will cover 8 weeks of future data
        self.output_weeks = 8
               
        # ending time of input data
        self.time_series_end = datetime.utcfromtimestamp(self.env.now).replace(tzinfo=utc)
        
        # wait one week before making a new forecast
        self.forecast_update_interval = 7 * 24 * 60 * 60
        
        if "try_cache" in kwargs:
            try_cache = kwargs["try_cache"]
        else:
            try_cache = True

        # demands split into weekdays
        self.demands = Forecast.split_weekdata(input_data, samples_per_hour, start)
        self.demands = [demand[-self.input_hours:] for demand in self.demands]
        
        #forecast all demands.. might take long
        self.forecasted_demands = self.forecast_demands(try_cache=try_cache)
        
    def forecast_demand(self, demand, index, result_queue):
        #seasonality length -- one day
        m = 24
        #forecast_length
        fc = len(demand)
        # alpha, beta, gamma. if any is None, holt.winters determines them automatically
        # cost-expensive, so only do this once..
        (alpha, beta, gamma) = self.hw_parameters
        print "find holt winter parameters for day: ", index
        if None not in self.hw_parameters:
            (forecast_values_manual, alpha, beta, gamma, rmse_manual) = multiplicative(
                demand, m, fc, alpha, beta, gamma)
            mase_manual = Forecast.MASE(demand, demand, forecast_values_manual)
        else:
            #set to high value, so it will be overwritten 
            #(if algorithms totally fails, there will be an error though..)
            mase_manual = 1000 
        rmse_auto = 10 ** 3
        mase_auto = 10 ** 3
        if self.hw_optimization != "None":
            # find values automatically
            # check with MASE error measure
            (forecast_values_auto, alpha, beta, gamma, rmse_auto) = multiplicative(
                demand, m, fc, optimization_type="MASE")
             
            mase_auto = Forecast.MASE(demand, demand,  forecast_values_auto)
            print mase_auto
            
            
        if mase_manual > mase_auto:
            forecast_values = forecast_values_auto
            calculated_parameters = {
                "alpha": alpha, "beta": beta, "gamma": gamma, "rmse": rmse_auto, "mase": mase_auto}
            print "use auto HW with RMSE", rmse_auto, " and MASE ", mase_auto , " with index: " , index
        else:
            forecast_values = forecast_values_manual
            calculated_parameters = {
                "alpha": alpha, "beta": beta, "gamma": gamma, "rmse": rmse_manual, "mase": mase_manual}
            print "use manual HW with RMSE", rmse_manual, " and MASE ", mase_manual, " with index: " , index
        
        result_queue.put((forecast_values, calculated_parameters, index))

    def forecast_demands(self, try_cache=True):
        split_results = [[] for i in range(7)]
        unordered_forecasts = []
        
        if try_cache:
            try:
                values = pickle.load(open( "cache/cached_forecasts.p", "rb" ))
                diff_time = datetime.utcfromtimestamp(values["date"]).replace(tzinfo=utc) - self.time_series_end
                if diff_time.total_seconds() < 24 * 60 * 60: #12 hours epsilon
                    forecasted_demands = values["forecasts"]
                    self.calculated_parameters = values["parameters"] 
                    logger.info("reading forecastings from cache")
                    return forecasted_demands
            except IOError as e:
                logger.info(str(e) + " .. creating new cache file")

        #[self.forecast_demand(d, i, result_queue) for i,d in enumerate(self.demands)]
        
        #share results in a multiaccess queue
        #note: this queue can not hold unlimited elements and will hang up with no warning if there are too many elements
        #12 weeks 1hourly will work, 20 not
        result_queue = multiprocessing.Queue()
        # use multiple processes instead of pool.map to circumvent a hangup caused
        # by a multiprocessing/django incompabatility
        #call class as Functor because class methods are not pickeable

        jobs = [Process(target=self, args=(demand,index,result_queue)) for index, demand in enumerate(self.demands)]
        for job in jobs: job.start()
        for job in jobs: job.join()
         
        while not result_queue.empty():
            unordered_forecasts.append(result_queue.get())
        for fc_triple in unordered_forecasts:
            split_results[fc_triple[2]] = (fc_triple[0],fc_triple[1])
            
        forecasted_demands = []
        self.calculated_parameters = []
        for fc_tuple in split_results:
            #Plotting.plot_dataset({"forecasted": fc_tuple[0], "measured": self.demands[i]} , len(self.demands[i]), True)
            forecasted_demands.append(list(fc_tuple[0]))
            self.calculated_parameters.append(fc_tuple[1])
            
        pickle.dump( {"forecasts" :forecasted_demands, "parameters" : self.calculated_parameters, "date": self.env.now },
                      open("cache/cached_forecasts.p", "wb" ) ) 

        return forecasted_demands
    


    # callable class
    def __call__(self, demand, index, result_queue):
        self.forecast_demand(demand, index, result_queue)

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

    @classmethod
    def make_hourly(cls, data, samples_per_hour):
        def avg(hour):
            sum = 0
            for i in range(samples_per_hour):
                sum += data[hour * samples_per_hour + i]
            return sum / samples_per_hour

        hours = len(data) / samples_per_hour
        return [avg(i) for i in range(hours)]

    def append_values(self, data, start_date=None):
        new_demands = Forecast.split_weekdata(data, self.samples_per_hour, start_date)
        
        for index, demand in enumerate(new_demands):
            self.demands[index] += demand
        if len(self.demands[index]) > self.input_hours:
            #only keep number of input_weeks
            print "appending"
            start_index = len(self.demands[index]) - self.input_hours
            self.demands[index] = self.demands[index][start_index:]
            pass
            
        now = datetime.utcfromtimestamp(self.env.now).replace(tzinfo=utc)
        delta = (now - self.time_series_end).total_seconds()
        if delta > self.forecast_update_interval:
            self.forecasted_demands = self.forecast_demands(try_cache=False)
            self.time_series_end = datetime.utcfromtimestamp(self.env.now).replace(tzinfo=utc)

    def _forecast_at(self, timestamp):
        date = datetime.utcfromtimestamp(timestamp).replace(tzinfo=utc)
        delta = (date - self.time_series_end).total_seconds()
        arr_index = int((delta / (60.0 * 60.0)) * self.samples_per_hour)
        week_index = int(arr_index / (7 * 24))
        hour_index = arr_index % 24
        return (self.forecasted_demands[date.weekday()][week_index * 24 + hour_index], week_index, hour_index)

    def get_forecast_at(self, timestamp):
        return self._forecast_at(timestamp)[0]

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
