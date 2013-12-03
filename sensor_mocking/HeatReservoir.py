import Device
from Device import Sensor
from Device import GeneratorDevice


""" Heat Reservoir based on Vaillant UNISTOR VIH Q 120 """
class HeatReservoir(Device.Device):

	def __init__(self, device_id, time_step=0.05):
 		Device.Device.__init__(self, device_id, time_step)

 		self.name = "HeatReservoir"

		self.storage_capacity = 112 #l

		self.current_pressure = Sensor(name="pressure", id=0, value=0, unit=r"bar", max_value=10)
		self.current_warmwater_temp = Sensor(name="warmwater temperature", id=1, value=0, unit=r"C", max_value=85)
		self.current_boilerwater_temp = Sensor(name="boilerwater temperature", id=2, value=0, unit=r"C", max_value=110)

		self.water_inflow1 = 0
		self.water_inflow2 = 0

		self.sensors = [self.current_pressure,self.current_warmwater_temp,self.current_boilerwater_temp]
 		

