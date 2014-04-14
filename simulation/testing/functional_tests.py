import unittest

import os
parent_directory = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__)))
os.sys.path.insert(0, parent_directory)

import start
import forecast

class ForecastTestCase(unittest.TestCase):

    def test_forecast_api_provides_inaccurracy(self):
        rv = start.app.test_client().get('/api/forecasts/')
        self.assertIn('forecast_inaccurracy', rv.data)
        
    '''def test_forecast_api_provides_inaccurracy(self):
        f = Forecast()'''

if __name__ == '__main__':
    unittest.main()
