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


 		self.current_workload 		=  Sensor(name="workload", id=0, value=0, unit=r"%")
 		self.current_electrical_power =  Sensor(name="electrical_power", id=1, value=0, unit="kW")
 		self.current_thermal_power 	=  Sensor(name="thermal_power", id=2, value=0, unit="kW")
 		self.current_gasinput 		=  Sensor(name="gas_input", id=3, value=0, unit="kW")

 		#index corresponds to sensor id
 		self.sensors = [self.current_workload,self.current_electrical_power,self.current_thermal_power,self.current_gasinput]

 		self.given_data = []
 		#workload in percent, other data in kW
 		self.given_data.append(InputData(workload=0, electrical_power=0, thermal_power=0, gasinput=0))
 		self.given_data.append(InputData(workload=25, electrical_power=12.5, thermal_power=20, gasinput=43))
 		self.given_data.append(InputData(workload=50, electrical_power=25, thermal_power=46, gasinput=86))
 		self.given_data.append(InputData(workload=75, electrical_power=38, thermal_power=64, gasinput=118))
 		self.given_data.append(InputData(workload=100, electrical_power=50, thermal_power=81, gasinput=145))


 		#specificationData
 		self.voltage = 400
 		self.electrical_current = 72


 		# is only set to false if mainloop is stopped
 		#self.mainloop_running = True
 		#self.mainloop = Thread(target=self.mainloop,args=())
 		#self.mainloop.start()




 	def turn_on(self): 		
 		print "turning on BHKW, please wait.."
 		self.set_current_workload(75.0)

 	def turn_off(self):
 		print "turning off BHKW, please wait.."
 		self.set_current_workload(0.0)





 	def calculate_parameters(self,workload):
 		#get the two datasets in between which the workload resides
 		for i in range(len(self.given_data)-1):
 			if workload < self.given_data[i+1]:
 				data_set1 = self.given_data[i]
 				data_set2 = self.given_data[i+1]
 				break
 		else:
 			data_set1 = self.given_data[-2] #last and second to last
 			data_set2 = self.given_data[-1]

		# interpolate the values
		mu = workload-data_set1.workload
		self.current_electrical_power.value = cosine_interpolate(data_set1.electrical_power, data_set2.electrical_power, mu)
		self.current_gasinput.value     = cosine_interpolate(data_set1.gasinput, data_set2.gasinput, mu)
		self.current_thermal_power.value = cosine_interpolate(data_set1.thermal_power, data_set2.thermal_power, mu)

	def mainloop(self):
		while self.mainloop_running:
			if (self.changing_workload == False and self.current_workload.value > 0.0 ):
				self.current_workload.value += (random.random() * 20.0 - 1.0) * self.time_step * 20.0
				self.current_workload.value  = max(min(self.current_workload.value, 100.0), 0.0) #clamp
				self.calculate_parameters(self.current_workload.value)
			time.sleep(self.time_step)

	def update(self,time_delta):
		if not super(BHKW, self).update(time_delta):
			return False

		if (self.changing_workload == False and self.current_workload.value > 0.0 ):
			self.current_workload.value = self.target_workload + (random.random() * 2.0 - 1.0) * self.time_step
			self.current_workload.value  = max(min(self.current_workload.value, 100.0), 0.0) #clamp
			self.calculate_parameters(self.current_workload.value)




class InputData:
	def __init__(self,workload,electrical_power,thermal_power,gasinput):
		self.electrical_power = electrical_power
		self.thermal_power = thermal_power
 		self.gasinput = gasinput
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
 		return [self.workload,self.electrical_power,self.thermal_power,self.gasinput]

def cosine_interpolate(d1,d2,mu):
	mu /= 25.0
	mu2 = (1-math.cos(mu*math.pi)) / 2.0
	return (d1 * (1-mu2) + d2 * mu2)

