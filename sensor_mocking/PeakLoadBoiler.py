import Device


class PeakLoadBoiler(Device.Device):
	def __init__(self):
		self.currentWorkload 	= Sensor(name="workload",id=0,value=0,unit=r"%")
		self.currentTemperature = Sensor(name="Temperature",id=1,value=0,unit="Celsius")
		self.name = "PeakLoadBoiler"



	def mainloop(self):
		pass


