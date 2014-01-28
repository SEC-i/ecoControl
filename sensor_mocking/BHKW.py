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

	

 	def __init__(self,device_id):
 		GeneratorDevice.__init__(self,device_id)

 		self.name = "BHKW"

 		# self.current_electrical_power =  Sensor(name="electrical_power", id=1, value=0, unit="kW")
 		# self.current_thermal_power 	=  Sensor(name="thermal_power", id=2, value=0, unit="kW")
 		# self.current_gasinput 		=  Sensor(name="gas_input", id=3, value=0, unit="kW")

 		#index corresponds to sensor id

 		self.sensors = {"workload":Sensor(name="workload", id=0, value=0, unit=r"%"),
 						"electrical_power":Sensor(name="electrical_power", id=1, value=0, unit="kW"),
 						"thermal_power":Sensor(name="thermal_power", id=2, value=0, unit="kW"),
 						"gasinput":Sensor(name="gas_input", id=3, value=0, unit="kW") }
 		
 		self.current_workload  = self.sensors["workload"]

 		self.given_data = []
 		#workload in percent, other data in kW
 		self.given_data.append({"workload":0, "electrical_power":0, "thermal_power":0, "gasinput":0})
 		self.given_data.append({"workload":25, "electrical_power":12.5, "thermal_power":20, "gasinput":43})
 		self.given_data.append({"workload":50, "electrical_power":25, "thermal_power":46, "gasinput":86})
 		self.given_data.append({"workload":75, "electrical_power":38, "thermal_power":64, "gasinput":118})
 		self.given_data.append({"workload":100, "electrical_power":50, "thermal_power":81, "gasinput":145})




 	def turn_on(self): 		
 		print "turning on BHKW, please wait.."
 		self.set_current_workload(75.0)

 	def turn_off(self):
 		print "turning off BHKW, please wait.."
 		self.set_current_workload(0.0)



 	def find_bounding_datasets(self,value,type):
 		#get the two datasets in between which the workload resides
 		for i in range(len(self.given_data)-1):
 			if value < self.given_data[i+1][type]:
 				data_set1 = self.given_data[i]
 				data_set2 = self.given_data[i+1]
 				break
 		else:
 			data_set1 = self.given_data[-2] #last and second to last
 			data_set2 = self.given_data[-1]
 		return (data_set1,data_set2)



	def calculate_parameters(self,value,type):
		data_set1,data_set2 = find_bounding_datasets(value,type)

		mu = self.sensors[type]-data_set1[type]
		ret_dict = {}

		#return interpolated values from datasheet
		for key,sensor in self.sensors:
			if (key!= type):
				interp_value = cosine_interpolate(data_set1[type], data_set2[type], mu)
				ret_dict[type] = interp_value
		return ret_dict


	def update(self,time_delta,heat_storage):
		needed_thermal_power = heat_storage.get_power_demand()
		self.target_workload = calculate_parameters(needed_thermal_power,"thermal_power")["workload"]
		self.smooth_set_step(time_delta)
		new_values = calculate_parameters(self.current_workload,"workload")
		
		#set values for current simulation step
		for key,sensor_value in new_values:
			if (key != "workload"):
				self.sensors[key].value = sensor_value 

		heat_storage.set_power(self.sensors["thermal_power"].value)



def cosine_interpolate(d1,d2,mu):
	mu /= 25.0
	mu2 = (1-math.cos(mu*math.pi)) / 2.0
	return (d1 * (1-mu2) + d2 * mu2)

