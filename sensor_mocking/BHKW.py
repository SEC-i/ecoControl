import Device
from Device import Sensor
from Device import GeneratorDevice
import math
import time
from  threading import Thread
import random
import unittest
import sys



"""@doc please read the technical datasheet of vitobloc_200_EM,
which contains all the data which we are mocking here"""
class BHKW(GeneratorDevice):

	

 	def __init__(self,device_id,time_step=0.10):
 		GeneratorDevice.__init__(self,device_id,time_step)

 		self.name = "BHKW"
 		#self.time_step  =  0.08


 		self.currentWorkload 		=  Sensor(name="workload",id=0,value=0,unit=r"%")
 		self.currentElectricalPower =  Sensor(name="electrical_power",id=1,value=0,unit="kW")
 		self.currentThermalPower 	=  Sensor(name="thermal_power",id=2,value=0,unit="kW")
 		self.currentGasInput 		=  Sensor(name="gas_input",id=3,value=0,unit="kW")

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


 		# is only set to false if mainloop is stopped
 		#self.mainloopRunning = True
 		#self.mainloop = Thread(target=self.mainloop,args=())
 		#self.mainloop.start()




 	def turnOn(self): 		
 		print "turning on BHKW, please wait.."
 		self.setcurrentWorkload(75.0)

 	def turnOff(self):
 		print "turning off BHKW, please wait.."
 	 	self.setcurrentWorkload(0.0)





 	def calculateParameters(self,workload):
 		#get the two datasets in between which the workload resides
 		for i in range(len(self.givenData)-1):
 			if workload < self.givenData[i+1]:
 				dataSet1 = self.givenData[i]
 				dataSet2 = self.givenData[i+1]
 				break
 		else:
 			dataSet1 = self.givenData[-2] #last and second to last
 			dataSet2 = self.givenData[-1]

		# interpolate the values
		mu = workload-dataSet1.workload
		self.currentElectricalPower.value = cosineInterpolate(dataSet1.electricalPower, dataSet2.electricalPower, mu)
		self.currentGasInput.value     = cosineInterpolate(dataSet1.gasInput, dataSet2.gasInput, mu)
		self.currentThermalPower.value = cosineInterpolate(dataSet1.thermalPower, dataSet2.thermalPower, mu)

	def mainloop(self):
		while self.mainloopRunning:
			if (self.changingWorkload == False and self.currentWorkload.value > 0.0 ):
				self.currentWorkload.value += (random.random() * 2.0 - 1.0) * self.time_step * 20.0
				self.currentWorkload.value  = max(min(self.currentWorkload.value, 100.0), 0.0) #clamp
				self.calculateParameters(self.currentWorkload.value)
			time.sleep(self.time_step)

	def update(self,time_delta):
		if not super(BHKW, self).update(time_delta):
			return False

		if (self.changingWorkload == False and self.currentWorkload.value > 0.0 ):
			self.currentWorkload.value = self.targetWorkload + (random.random() * 2.0 - 1.0) * self.time_step
			self.currentWorkload.value  = max(min(self.currentWorkload.value, 100.0), 0.0) #clamp
			self.calculateParameters(self.currentWorkload.value)




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

