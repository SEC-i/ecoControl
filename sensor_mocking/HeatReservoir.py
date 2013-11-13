import Device
from Device import Sensor
from Device import GeneratorDevice


""" Heat Reservoir based on Vaillant UNISTOR VIH Q 120 """
class HeatReservoir(Device.Device):

	def __init__(self,device_id):
 		GeneratorDevice.__init__(self,device_id)

 		self.name = "HeatReservoir"

		self.storageCapacity = 112 #l

		self.currentPressure = Sensor(name="pressure",id=0,value=0,unit=r"bar",maxValue=10)
		self.currentWarmWaterTemp = Sensor(name="warmwater temperature",id=1,value=0,unit=r"C",maxValue=85)
		self.currentBoilerWaterTemp = Sensor(name="boilerwater temperature",id=2,value=0,unit=r"C",maxValue=110)

		self.sensors = [self.currentPressure,self.currentWarmWaterTemp,self.currentBoilerWaterTemp]






	#override defualt workload handling (heatreservoir can't set workload)
 	def calculateParameters(self,workload):
 		pass

