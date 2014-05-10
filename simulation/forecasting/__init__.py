from datetime import date, datetime, timedelta
from holt_winters import multiplicative, additive
import numpy as np
from multiprocessing import Pool
import time


class Forecast:

    """
    @param input_data: list of consecutive values sampled in samples_per_hour
    @param start: start date of input data
    @param hw_parameters: tuple with (alpha, beta, gamma)
    @param hw_optimisation: "None" --> given hw_parameters are always used (fastest, hw_parameters required)
                            "RMSE" --> Root Mean Square Error used as optimization parameter for Holt-Winters (slow)
                            "MASE" --> Mean Absolute Scaled Error is used. Yields most accurate results (slowest)
    """

    def __init__(self, env, input_data, samples_per_hour=1, start=None, hw_parameters=(), hw_optimization="RMSE"):
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
            start = datetime.fromtimestamp(env.now) - data_length
            
        #always set to start of day
        start = start.replace(hour=0,minute=0) 
        
        #only forecast with this many weeks of data, approx 4 months
        self.input_weeks = 16
        #the forecast will cover 8 weeks of future data
        self.output_weeks = 8

        # demands split into weekdays
        self.demands = Forecast.split_weekdata(input_data, samples_per_hour, start)
        #self.demands = self.demands[:self.input_weeks*24*self.samples_per_hour]
        
        #forecast all demands.. might take long
        self.forecasted_demands = self.forecast_demands()
       
        # ending time of input data
        self.time_series_end = datetime.fromtimestamp(env.now)
        
        # wait at least one day before making a new forecast
        self.forecast_update_interval = 24 * 60 * 60
        


    def forecast_demand(self, demand):
        #seasonality length -- one day
        m = 24
        #forecast_length
        fc = len(demand)
        # alpha, beta, gamma. if any is None, holt.winters determines them automatically
        # cost-expensive, so only do this once..
        (alpha, beta, gamma) = self.hw_parameters

        (forecast_values_manual, alpha, beta, gamma, rmse_manual) = multiplicative(
            demand, m, fc, alpha, beta, gamma)

        rmse_auto = 10 ** 6  # some really high value, wil be overwritten
        mase_auto = 10 ** 6
        mase_manual = Forecast.MASE(demand, demand, forecast_values_manual)
        if self.hw_optimization != "None" and (rmse_manual > 6 or mase_manual > 4):
            # find values automatically
            # check with MASE error measure
            (forecast_values_auto1, alpha1, beta1, gamma1, rmse_auto1) = multiplicative(
                demand, m, fc, optimization_type=self.hw_optimization)
            
            mase_auto1 = Forecast.MASE(demand, demand,  forecast_values_auto1)

            (forecast_values_auto2, alpha2, beta2, gamma2, rmse_auto2) = multiplicative(demand, m, fc, 
                initial_values_optimization=[0.02, 0.01, 0.08], optimization_type=self.hw_optimization)

            mase_auto2 = Forecast.MASE(demand, demand, forecast_values_auto2)
            
            if mase_auto1 > mase_auto2:
                (forecast_values_auto, alpha, beta, gamma, rmse_auto) = (
                    forecast_values_auto2, alpha2, beta2, gamma2, rmse_auto2)
                mase_auto = mase_auto2
            else:
                (forecast_values_auto, alpha, beta, gamma, rmse_auto) = (
                    forecast_values_auto1, alpha1, beta1, gamma1, rmse_auto1)
                mase_auto = mase_auto1


        if mase_manual > mase_auto:
            forecast_values = forecast_values_auto
            calculated_parameters = {
                "alpha": alpha, "beta": beta, "gamma": gamma, "rmse": rmse_auto}
            print "use auto HW with RMSE", rmse_auto, " and MASE ", mase_auto
        else:
            forecast_values = forecast_values_manual
            calculated_parameters = {
                "alpha": alpha, "beta": beta, "gamma": gamma, "rmse": rmse_manual}
            print "use manual HW with RMSE", rmse_manual, " and MASE ", mase_manual

        return (forecast_values, calculated_parameters)

    def forecast_demands(self):
        forecasted_demands = []
        forecasts = []

        # multiprocessing with processes, to use multiple processors
        pool = Pool(processes=len(self.demands))
        # pass class instance, which will call the __call__ method. This is done, because instance methods are not
        # pickeable and cant be used with with processes
        forecasts = pool.map(self, self.demands)

        self.calculated_parameters = []
        for fc_tuple in forecasts:
            forecasted_demands.append(list(fc_tuple[0]))
            self.calculated_parameters.append(fc_tuple[1])

        return forecasted_demands

    # callable class
    def __call__(self, demand):
        return self.forecast_demand(demand)

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
        max_data = self.input_weeks * 24 * self.samples_per_hour
        
        for index, demand in enumerate(new_demands):
            self.demands[index] += demand
        if len(self.demands[index]) > max_data:
            #only keep number of input_weeks
            #start_index = len(self.demands[index]) - max_data
            #self.demands[index] = self.demands[index][start_index:]
            pass
            

        delta = (datetime.fromtimestamp(self.env.now) - self.time_series_end).total_seconds()
        if delta > self.forecast_update_interval:
            self.forecasted_demands = self.forecast_demands()
            self.time_series_end = self.env.now

    def _forecast_at(self, timestamp):
        date = datetime.fromtimestamp(timestamp)
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
