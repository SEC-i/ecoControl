import unittest
from datetime import datetime

from simulation.forecasting import Forecast
from simulation.forecasting.dataloader import DataLoader
from simulation.core.environment import ForwardableRealtimeEnvironment
from simulation.tools.plotting import Plotting


class ForecastTests(unittest.TestCase):

    def setUp(self):
        # dataset containing one year of data, sampled in 10 minute intervals
        raw_dataset = DataLoader.load_from_file("../tools/Strom_2013.csv", "Strom - Verbrauchertotal (Aktuell)", "\t")
        #cast to float and convert to kW
        self.dataset = [float(val) / 1000.0 for val in raw_dataset]
        pass

    def test_data(self):
        print "--------- test data ------------------"
        date_dataset = DataLoader.load_from_file("../tools/Strom_2013.csv", "Datum", "\t")
        ten_min = 10 * 60
        epsilon = 599  # maximal 599 seconds deviatiation from samplinginterval
        print len(date_dataset)
        for index, date in enumerate(date_dataset):
            if index < len(date_dataset) - 1:
                diff = int(date_dataset[index + 1]) - int(date_dataset[index])
                self.assertTrue(abs(diff - ten_min) < epsilon, "a jump of " + str(
                    diff - ten_min) + " seconds at index " + str(index))

    def test_make_hourly(self):
        print "--------- test make_hourly ------------------"
        hourly_data = Forecast.make_hourly(self.dataset, 6)

        average = 0
        for i in range(6):
            average += self.dataset[i]
        average /= 6

        self.assertEqual(hourly_data[0], average, 
                         "calculated average not the same as function average")
        self.assertAlmostEqual(len(hourly_data), 24 * 365, delta=23,
                               msg="only data for " + str(len(hourly_data) / 24) + " days")

    def test_split_week_data(self):
        print "--------- test split_week_data ------------------"
        hourly_data = Forecast.make_hourly(self.dataset, 6)
        env = ForwardableRealtimeEnvironment()
        fc = Forecast(env, hourly_data, 1, None, (0.0000000, 0.0,1.0))

        self.assertTrue(
            len(fc.demands) == 7, "week_split does not contain 7 series")
        
        self.assertTrue(len(fc.demands[0]) / 24 >= 50, "the day series only contains " + str(
            len(fc.demands[0]) / 24) + " days, not 52 (or at least more than 50)")
        
        for i in range(7):
            #Plotting.plot_dataset({'measured': fc.demands[i], 'forecasted': fc.forecasted_demands[i]})
            self.assertTrue(fc.calculated_parameters[i]["rmse"] < 10.0, "RMSE of " + str(
                fc.calculated_parameters[i]["rmse"]) + "for day" + str(i) + " is way too high")
            
    def test_forecast_at(self):
        print "--------- test forecast_at ------------------"
        hourly_data = Forecast.make_hourly(self.dataset, 6)
        env = ForwardableRealtimeEnvironment()
        fc = Forecast(env, hourly_data, 1, None, (0.0000000, 0.0,1.0), hw_optimization="None")
        
        (at_now, day_index, hour_index)  = fc._forecast_at(env.now)
        
        self.assertTrue(day_index == 0, "day should be 0 but was " +str(day_index))
        self.assertTrue(hour_index == 0, "day should be 0 but was " +str(hour_index))
        
        forward = 60 * 60 * 24
        
        print datetime.fromtimestamp(env.now), datetime.fromtimestamp(env.now + forward)
        (at_now, day_index, hour_index)  = fc._forecast_at(env.now + forward)
        
        self.assertTrue(day_index == 1, "day should be 1 but was " +str(day_index))
        self.assertTrue(hour_index == 2, "day should be 1 but was " +str(hour_index))
        


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
