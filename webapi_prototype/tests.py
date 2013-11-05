import main
import unittest
import json

class WebAPITestCase(unittest.TestCase):

	def setUp(self):
		main.app.config['TESTING'] = True
		self.app = main.app.test_client()

	# def tearDown(self):

	def testMeasurements(self):
		rv = self.app.get('/api/measurements/')
		assert 'results' in json.loads(rv.data)

	def testMeasurementsLimit(self):
		for i in range(0,10):
			rv = self.app.get('/api/measurements/'+str(i)+'/')
			assert i == len(json.loads(rv.data)['results'])

if __name__ == '__main__':
	unittest.main()