
class Device(object):

	def __init__(self,device_id):
		self.device_id = device_id
		self.givenData = []
	
	def readValue(self):
		return None

	def turnOn(self):
		pass
	def turnOff(self):
		pass


	def customSignal(self,signal,value):
		pass



class Sensor(object):

	def __init__(self,name,id,value):
		self.id = id
		self.value = value
		self.name = name
