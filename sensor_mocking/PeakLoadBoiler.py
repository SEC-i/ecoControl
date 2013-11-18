import Device
from Device import Sensor
from Device import GeneratorDevice


class PlBoiler(GeneratorDevice):
	
	def __init__(self,device_id,time_step=0.04):
 		GeneratorDevice.__init__(self,device_id,time_step)

 		#faster timestep, PLBoiler changes its temperature faster than BHKW
 		#self.timestep = 0.01

		self.name = "PeakloadBoiler"
		self.currentWorkload 	= Sensor(name="Temperature",id=0,value=0,unit=r"Celsius")
		self.sensors = [self.currentWorkload]



	def mainloop(self):
		pass


	def calculateParameters(self):
		pass


