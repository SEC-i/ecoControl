import Device
import math
import time
from  threading import Thread
import random
import unittest


TIME_STEP = 0.05
"""@doc please read the technical datasheet of vitobloc_200_EM,
which contains all the data which we are mocking here"""
class BHKW(Device.Device):

	

 	def __init__(self):
 		self.givenData = []
 		#workload in percent, other data in kW
 		self.givenData.append(InputData(workload=0,electricalPower=0,thermalPower=0,gasInput=0))
 		self.givenData.append(InputData(workload=25,electricalPower=12.5,thermalPower=20,gasInput=43))
 		self.givenData.append(InputData(workload=50,electricalPower=25,thermalPower=46,gasInput=86))
 		self.givenData.append(InputData(75,38,64,118))
 		self.givenData.append(InputData(100,50,81,145))

 		self.currentWorkload = 0
 		self.currentElectricalPower = 0
 		self.currentGasInput = 0
 		self.currentThermalPower = 0


 		#specificationData
 		self.voltage = 400
 		self.electricalCurrent = 72

 		#internalState
 		self.changingWorkload = False
 		self.changingWorkloadThread = None


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
		self.currentElectricalPower = cosineInterpolate(dataSet1.electricalPower, dataSet2.electricalPower, mu)
		self.currentGasInput     = cosineInterpolate(dataSet1.gasInput, dataSet2.gasInput, mu)
		self.currentThermalPower = cosineInterpolate(dataSet1.thermalPower, dataSet2.thermalPower, mu)



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
 		while self.currentWorkload != workload and self.changingWorkload == True:
 			last_delta = delta
 			delta = TIME_STEP * (random.randint(-2,2) + 10.0 *  sign(workload - self.currentWorkload))
 			#use two last deltas to determine if value oscilating around certain point
 			#print "delta: ", delta, " added: ", abs(delta + last_delta), " workload: ", self.currentWorkload
 			if abs(delta + last_delta) <  TIME_STEP:
 				self.currentWorkload = workload
 				self._calculate(workload)
 				break
 			else:
 				self.currentWorkload += delta
 				self._calculate(self.currentWorkload)
 			time.sleep(TIME_STEP)
 		self.changingWorkload = False





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

def cosineInterpolate(d1,d2,mu):
	mu /= 25.0
	mu2 = (1-math.cos(mu*math.pi)) / 2.0
	return (d1 * (1-mu2) + d2 * mu2)

def sign(x): 
    return 1 if x >= 0 else -1
