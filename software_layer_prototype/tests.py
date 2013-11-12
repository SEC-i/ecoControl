import main
import unittest
import json

class WebAPITestCase(unittest.TestCase):

	def setUp(self):
		main.app.config['TESTING'] = True
		self.app = main.app.test_client()

	# def tearDown(self):

	# /api/measurements/device/1/ needs to contain 'results'
	def testMeasurements(self):
		rv = self.app.get('/api/measurements/device/1/')
		assert 'results' in json.loads(rv.data)

	# /api/measurements/device/1/(0..9)/ need to have (0..9) results
	def testMeasurementsLimit(self):
		for i in range(0,10):
			rv = self.app.get('/api/measurements/device/1/'+str(i)+'/')
			j = 0
			for sensor in ['return temperature','supply temperature', 'workload', 'electrical power', 'thermal power']:
				assert i == len(json.loads(rv.data)['results'][j][sensor])
				j = j+1

if __name__ == '__main__':
	unittest.main()
