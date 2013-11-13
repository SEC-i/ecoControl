from  threading import Thread
import random
import time

class Device(object):

	def __init__(self,device_id):
		self.device_id = device_id
		self.givenData = []
		self.sensors = []

		self.time_step = 0.05

		 #internalState
 		self.changingWorkload = False
 		self.changingWorkloadThread = None

	

 	def setcurrentWorkload(self,workload):
 		
 		if (self.changingWorkload == True):
 			self.changingWorkload = False
 			self.changingWorkloadThread.join()

 		self.changingWorkloadThread = Thread(target=self.smoothSetToWorkload,args=(workload,))
 		self.changingWorkloadThread.start()

 	def calculateParameters(self,workload):
 		pass


 	def smoothSetToWorkload(self,workload):
 		self.changingWorkload = True
 		last_delta = 0
 		delta = 0
 		while self.currentWorkload.value != workload and self.changingWorkload == True:
 			last_delta = delta
 			delta = self.time_step * ((random.random() * 2.0 - 1.0) + 10.0 *  sign(workload - self.currentWorkload.value))
 			#use two last deltas to determine if value oscilating around certain point
 			#print "delta: ", delta, " added: ", abs(delta + last_delta), " workload: ", self.currentWorkload
 			if abs(delta + last_delta) <  self.time_step:
 				self.currentWorkload.value = workload
 				self.calculateParameters(workload)
 				break
 			else:
 				self.currentWorkload.value += delta
 				self.calculateParameters(self.currentWorkload.value)
 			try:
				time.sleep(self.time_step)
			except KeyboardInterrupt:
				sys.exit(1)
 		self.changingWorkload = False

 	def getMappedSensor(self,sID):
 		maxValue = max([sensorSet.toList()[sID] for sensorSet in self.givenData])
 		minValue = min([sensorSet.toList()[sID] for sensorSet in self.givenData])
 		
 		for sensor in self.sensors:
 			if sensor.id == sID:
 				newValue = sensor.value / ((maxValue - minValue) / 100.0)
 				return Sensor(name=sensor.name,id=sID,value=newValue)



class Sensor(object):

	def __init__(self,name,id,value,unit,maxValue=None):
		self.id = id
		self.value = value
		self.name = name
		self.unit = unit
		self.maxValue = maxValue


def sign(x): 
    return 1 if x >= 0 else -1

