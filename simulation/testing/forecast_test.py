import unittest

from simulation.forecasting import Forecast
from simulation.forecasting.dataloader import DataLoader
from simulation.core.environment import ForwardableRealtimeEnvironment
from simulation.tools.plotting import Plotting


class ForecastTests(unittest.TestCase):
    
    def setUp(self):
        #dataset containing one year of data, sampled in 10 minute intervals
        raw_dataset = DataLoader.load_from_file("../tools/Strom_2013.csv", "Strom - Verbrauchertotal (Aktuell)","\t")
        self.dataset = [float(val) / 1000.0 for val in raw_dataset] #cast to float and convert to kW
        
    def test_data(self):
        date_dataset = DataLoader.load_from_file("../tools/Strom_2013.csv", "Datum","\t")
        ten_min = 10 * 60
        epsilon = 10 #10 secs
        for index, date in enumerate(date_dataset):
            if index < len(date_dataset) - 1:
                diff = int(date_dataset[index+1]) - int(date_dataset[index]) 
                self.assertTrue(abs(diff - ten_min) > epsilon,"a jump of " + str(diff) + " seconds at index " + str(index))
    
    def test_make_hourly(self):
        hourly_data = Forecast.make_hourly(self.dataset, 10)
         
        average = 0
        for i in range(10):
            average += self.dataset[i]
        average /= 10
         
         
        self.assertEqual(hourly_data[0], average, "calculated average not the same as function average")
        self.assertTrue(len(hourly_data) == 24 * 365, "only data for "+ str(len(hourly_data) / 24) + " days")
     
     
    def test_split_week_data(self):
        hourly_data = Forecast.make_hourly(self.dataset, 10)
        env = ForwardableRealtimeEnvironment()
        fc = Forecast(env, hourly_data, 1, None, (0.0000001,0.0,1.0))
        for i in range(7):
            Plotting.plot_dataset({'measured' : fc.demands[i], 'forecasted': fc.forecasted_demands[i]})
        #week_split_series = fc.split_weekdata(hourly_data)
         
        self.assertTrue(len(fc.demands) == 7, "week_split does not contain 7 series")
        print len(fc.demands[0]) / 24
        self.assertTrue(len(fc.demands[0]) / 24 >= 50, "the day series only contains " + str(len(fc.demands[0]) / 24) + " days, not 52 (or at least more than 50)")
     


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()