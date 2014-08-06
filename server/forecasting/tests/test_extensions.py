import unittest
import os
import numpy
from server.forecasting.dataloader import DataLoader
from server.settings import BASE_DIR, CYTHON_SUPPORT
from server.forecasting.statistical import StatisticalForecast
from server.forecasting.statistical.holt_winters import double_seasonal, multiplicative
import time


sep = os.path.sep
DATA_PATH = BASE_DIR + sep + "server" + sep + \
    "forecasting" + sep + "simulation" + sep + "demodata"


@unittest.skipIf(not CYTHON_SUPPORT, "cython support not activated")
class ExtensionsTest(unittest.TestCase):

    """ Test if cython extensions deliver the same results as their python counterparts"""

    @classmethod
    def setUpClass(cls):
        from server.forecasting.statistical.build_extension import build_holtwinters_extension
        # compile and link holtwinters_fast module
        build_holtwinters_extension()
        #make them accessible everywhere
        global Cdouble_seasonal, Cmultiplicative
        from server.forecasting.statistical.holtwinters_fast import double_seasonal as Cdouble_seasonal
        from server.forecasting.statistical.holtwinters_fast import multiplicative as Cmultiplicative

    def setUp(self):
        # dataset containing one year of data, sampled in 10 minute intervals
        # really important to reset, because other devices could have added
        # data which is unwanted
        DataLoader.cached_csv = {}
        path = DATA_PATH + sep + "demo_electricity_2013.csv"
        raw_dataset = DataLoader.load_from_file(
            path, "Strom - Verbrauchertotal (Aktuell)", "\t")
        # cast to float and convert to kW
        self.dataset = StatisticalForecast.make_hourly(
            [float(val) / 1000.0 for val in raw_dataset], 6)

    def rmse(self, testdata, forecast):
        return sum([(m - n) ** 2 for m, n in zip(testdata, forecast)]) / len(testdata)

    def test_doubleseasonal(self):
        input_length = 24 * 7 * 8
        forecast = 24 * 7 * 4

        for a in [0.0, 0.5, 1.0]:
            for b in [0.0, 0.5, 1.0]:
                py_forecast, p, insample = double_seasonal(
                    self.dataset[:-input_length], 24, 24 * 7, forecast,
                    alpha=a, beta=0.0, gamma=a, delta=a, autocorrelation=b)
                cy_forecast, p, insample = Cdouble_seasonal(
                    self.dataset[:-input_length], 24, 24 * 7, forecast,
                    alpha=a, beta=0.0, gamma=a, delta=a, autocorrelation=b)

                # exclude very high values from testing, as these will have
                # floating point accuracy issues
                if abs(numpy.mean(py_forecast)) < 10 ** 9:
                    self.assertTrue(self.rmse(py_forecast, cy_forecast) < 0.5,
                                    "python and cython dshw-forecasts differ significantly.")

    def test_multiplicative(self):
        input_length = 24 * 7 * 8
        forecast = 24 * 7 * 4
        for a in [0.0, 0.5, 1.0]:
            for b in [0.0, 0.5, 1.0]:
                py_forecast, p, insample = multiplicative(
                    self.dataset[:-input_length], 24, forecast,
                    alpha=a, beta=b, gamma=b)
                cy_forecast, p, insample = Cmultiplicative(
                    self.dataset[:-input_length], 24,  forecast,
                    alpha=a, beta=b, gamma=b)

                # exclude very high values from testing, as these will have
                # floating point accuracy issues
                if abs(numpy.mean(py_forecast)) < 10 ** 9:
                    self.assertTrue(self.rmse(py_forecast, cy_forecast) < 0.5,
                                    "python and cython multiplicative-forecasts differ significantly.")

    def test_performance(self):
        input_length = 24 * 7 * 8
        forecast = 24 * 7 * 4
        t = time.time()
        for i in range(100):
            double_seasonal(self.dataset[:-input_length], 24, 24 * 7, forecast,
                            alpha=0.5, beta=0.0, gamma=0.5, delta=0, autocorrelation=0.2)
        py_timing = time.time() - t

        t2 = time.time()
        for i in range(100):
            Cdouble_seasonal(
                self.dataset[:-input_length], 24, 24 * 7, forecast,
                alpha=0.5, beta=0.0, gamma=0.5, delta=0, autocorrelation=0.2)
        cy_timing = time.time() - t2
        # print py_timing, cy_timing
        self.assertTrue(
            cy_timing < py_timing, "cython version is slower than python. WTF?")
