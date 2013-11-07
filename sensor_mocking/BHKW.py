import Device
from Device import Sensor
import math
import time
from  threading import Thread
import random
import unittest


TIME_STEP = 0.05
"""@doc please read the technical datasheet of vitobloc_200_EM,
which contains all the data which we are mocking here"""
class BHKW(Device.Device):

	

 	def __init__(self,device_id):
 		Device.Device.__init__(self,device_id)


 		self.currentWorkload 		=  Sensor(name="workload",id=0,value=0)
 		self.currentElectricalPower =  Sensor(name="electricalPower",id=1,value=0)
 		self.currentThermalPower 	=  Sensor(name="thermalPower",id=2,value=0)
 		self.currentGasInput 		=  Sensor(name="gasInput",id=3,value=0)

 		#index corresponds to sensor id
 		self.sensors = [self.currentWorkload,self.currentElectricalPower,self.currentThermalPower,self.currentGasInput]

 		self.givenData = []
 		#workload in percent, other data in kW
 		self.givenData.append(InputData(workload=0,electricalPower=0,thermalPower=0,gasInput=0))
 		self.givenData.append(InputData(workload=25,electricalPower=12.5,thermalPower=20,gasInput=43))
 		self.givenData.append(InputData(workload=50,electricalPower=25,thermalPower=46,gasInput=86))
 		self.givenData.append(InputData(workload=75,electricalPower=38,thermalPower=64,gasInput=118))
 		self.givenData.append(InputData(workload=100,electricalPower=50,thermalPower=81,gasInput=145))


 		#specificationData
 		self.voltage = 400
 		self.electricalCurrent = 72

 		#internalState
 		self.changingWorkload = False
 		self.changingWorkloadThread = None
 		# is only set to false if mainloop is stopped
 		self.mainloopRunning = True
 		self.mainloop = Thread(target=self.mainloop,args=())
 		self.mainloop.start()




 	def turnOn(self): 		
 		print "turning on BHKW, please wait.."
 		self.setcurrentWorkload(75.0)

 	def turnOff(self):
 		print "turning off BHKW, please wait.."
 	 	self.setcurrentWorkload(0.0)


 	def immediateOff(self):
 		"for testcases"
 		self.changingWorkload = False
 		if self.changingWorkloadThread != None:
 			self.changingWorkloadThread.join()
 		self.setcurrentWorkload(0.0)


 	def _calculate(self,workload):

 		for i in range(len(self.givenData)-1):
 			if workload < self.givenData[i+1]:
 				dataSet1 = self.givenData[i]
 				dataSet2 = self.givenData[i+1]
 				break
 		else:
 			dataSet1 = self.givenData[-2] #last and second to last
 			dataSet2 = self.givenData[-1]

		
		mu = workload-dataSet1.workload
		self.currentElectricalPower.value = cosineInterpolate(dataSet1.electricalPower, dataSet2.electricalPower, mu)
		self.currentGasInput.value     = cosineInterpolate(dataSet1.gasInput, dataSet2.gasInput, mu)
		self.currentThermalPower.value = cosineInterpolate(dataSet1.thermalPower, dataSet2.thermalPower, mu)

	def mainloop(self):
		while self.mainloopRunning:
			if (self.changingWorkload == False and self.currentWorkload.value > 0.0 ):
				self.currentWorkload.value += (random.random() * 2.0 - 1.0) * TIME_STEP
				self.currentWorkload.value  = max(min(self.currentWorkload.value, 100.0), 0.0) #clamp
				self._calculate(self.currentWorkload.value)
			time.sleep(TIME_STEP)




 	def setcurrentWorkload(self,workload):
 		
 		if (self.changingWorkload == True):
 			self.changingWorkload = False
 			self.changingWorkloadThread.join()

 		self.changingWorkloadThread = Thread(target=self.smoothSetToWorkload,args=(workload,))
 		self.changingWorkloadThread.start()


 	def smoothSetToWorkload(self,workload):
 		self.changingWorkload = True
 		last_delta = 0
 		delta = 0
 		while self.currentWorkload.value != workload and self.changingWorkload == True:
 			last_delta = delta
 			delta = TIME_STEP * ((random.random() * 2.0 - 1.0) + 10.0 *  sign(workload - self.currentWorkload.value))
 			#use two last deltas to determine if value oscilating around certain point
 			#print "delta: ", delta, " added: ", abs(delta + last_delta), " workload: ", self.currentWorkload
 			if abs(delta + last_delta) <  TIME_STEP:
 				self.currentWorkload.value = workload
 				self._calculate(workload)
 				break
 			else:
 				self.currentWorkload.value += delta
 				self._calculate(self.currentWorkload.value)
 			time.sleep(TIME_STEP)
 		self.changingWorkload = False

 	def getMappedSensor(self,sID):
 		maxValue = max([sensorSet.toList()[sID] for sensorSet in self.givenData])
 		minValue = min([sensorSet.toList()[sID] for sensorSet in self.givenData])
 		
 		for sensor in self.sensors:
 			if sensor.id == sID:
 				newValue = sensor.value / ((maxValue - minValue) / 100.0)
 				return Sensor(name=sensor.name,id=sID,value=newValue)

 	




class InputData:
	def __init__(self,workload,electricalPower,thermalPower,gasInput):
		self.electricalPower = electricalPower
 		self.thermalPower = thermalPower
 		self.gasInput = gasInput
 		self.workload = workload
 	def __lt__(self,otherInputData):
 		if self.workload < otherInputData:
 			return True
 		else:
 			return False
 	def __gt__(self,otherInputData):
 		if self.workload > otherInputData:
 			return True
 		else:
 			return False
 	def toList(self):
 		return [self.workload,self.electricalPower,self.thermalPower,self.gasInput]

def cosineInterpolate(d1,d2,mu):
	mu /= 25.0
	mu2 = (1-math.cos(mu*math.pi)) / 2.0
	return (d1 * (1-mu2) + d2 * mu2)

def sign(x): 
    return 1 if x >= 0 else -1

