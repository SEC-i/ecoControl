import Device
from Device import Sensor
from Device import GeneratorDevice


class PlBoiler(GeneratorDevice):
	
	def __init__(self, device_id):
 		GeneratorDevice.__init__(self, device_id)

 		#faster timestep, PLBoiler changes its temperature faster than BHKW
 		#self.timestep = 0.01

		self.name = "PeakloadBoiler"
		self.current_workload 	= Sensor(name="Temperature", id=0, value=0, unit=r"Celsius")
		self.sensors = [self.current_workload]



	def mainloop(self):
		pass


	def calculate_parameters(self):
		pass


