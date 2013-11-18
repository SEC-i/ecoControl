from  threading import Thread
import random
import time

class Device(object):

	def __init__(self,device_id,time_step):
		self.device_id = device_id
		self.name = "Abstract Device"
		self.givenData = []
		self.sensors = []

		self.time_step = time_step
	
	def update(self,time_delta):
		if time_delta < self.time_step:
			# didnt update
 			return False
 		else:
 			return True




	



class GeneratorDevice(Device):

	def __init__(self,device_id,time_step):
		Device.__init__(self,device_id,time_step)

		self.name = "Abstract GeneratorDevice"

		#internalState
 		self.changingWorkload = False
 		self.changingWorkloadThread = None
 		self.targetWorkload  = 0
 		self.last_delta = 0
 		self.workload_delta = 0


	def setcurrentWorkload(self,workload):
 		
 		# if (self.changingWorkload == True):
 		# 	self.changingWorkload = False
 		# 	self.changingWorkloadThread.join()

 		# self.changingWorkloadThread = Thread(target=self.smoothSetToWorkload,args=(workload,))
 		# self.changingWorkloadThread.start()
 		self.last_delta = 0
 		self.workload_delta = 0

 		self.changingWorkload = True
 		self.targetWorkload = workload
 		pass

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
			time.sleep(self.time_step)
 		self.changingWorkload = False

 	def smoothSetToWorkload_Step(self,time_delta): 		
 		if self.currentWorkload.value != self.targetWorkload:
 			self.last_delta = self.workload_delta
 			self.workload_delta = self.time_step * ((random.random() * 2.0 - 1.0) + 10.0 *  sign(self.targetWorkload - self.currentWorkload.value))
 			#use two last deltas to determine if value oscilating around certain point
 			if abs(self.workload_delta + self.last_delta) <  self.time_step:
 				self.currentWorkload.value = self.targetWorkload
 				self.calculateParameters(self.targetWorkload)
 				self.changingWorkload = False
 				print "finished"
 			else:
 				self.currentWorkload.value += self.workload_delta
 				self.calculateParameters(self.currentWorkload.value)
 		return True


 	def getMappedSensor(self,sID):
 		maxValue = max([sensorSet.toList()[sID] for sensorSet in self.givenData])
 		minValue = min([sensorSet.toList()[sID] for sensorSet in self.givenData])
 		
 		for sensor in self.sensors:
 			if sensor.id == sID:
 				newValue = sensor.value / ((maxValue - minValue) / 100.0)
 				return Sensor(name=sensor.name,id=sID,value=newValue,unit=sensor.unit)

 	def immediateOff(self):
 		"for testcases"
 		self.changingWorkload = False
 		if self.changingWorkloadThread != None:
 			self.changingWorkloadThread.join()
 		self.setcurrentWorkload(0.0)

 	def update(self,time_delta):
 		if not super(GeneratorDevice, self).update(time_delta):
 			return False
 		if self.changingWorkload:
 			self.smoothSetToWorkload_Step(time_delta)
 		return True




class Sensor(object):

	def __init__(self,name,id,value,unit,maxValue=None):
		self.id = id
		self.value = value
		self.name = name
		self.unit = unit
		self.maxValue = maxValue


def sign(x): 
    return 1 if x >= 0 else -1

