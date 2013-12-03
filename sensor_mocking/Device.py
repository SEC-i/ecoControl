from  threading import Thread
import random
import time

class Device(object):

	def __init__(self, device_id, time_step):
		self.device_id = device_id
		self.name = "Abstract Device"
		self.given_data = []
		self.sensors = []

		self.time_step = time_step
	
	def update(self, time_delta):
		if time_delta < self.time_step:
			# didnt update
 			return False
 		else:
 			return True




	



class GeneratorDevice(Device):

	def __init__(self, device_id, time_step):
		Device.__init__(self, device_id, time_step)

		self.name = "Abstract GeneratorDevice"

		#internalState
 		self.changing_workload = False
 		self.changing_workload_thread = None
 		self.target_workload  = 0
 		self.last_delta = 0
 		self.workload_delta = 0


	def set_current_workload(self,workload):
 		
 		# if (self.changing_workload == True):
 		# 	self.changing_workload = False
 		# 	self.changing_workload_thread.join()

 		# self.changing_workload_thread = Thread(target=self.smooth_set_to_workload,args=(workload,))
 		# self.changing_workload_thread.start()
 		self.last_delta = 0
 		self.workload_delta = 0

 		self.changing_workload = True
 		self.target_workload = workload
 		pass

 	def calculate_parameters(self, workload):
 		pass


 	def smooth_set_to_workload(self,workload):
 		self.changing_workload = True
 		last_delta = 0
 		delta = 0
 		while self.current_workload.value != workload and self.changing_workload == True:
 			last_delta = delta
 			delta = self.time_step * ((random.random() * 2.0 - 1.0) + 10.0 *  sign(workload - self.current_workload.value))
 			#use two last deltas to determine if value oscilating around certain point
 			#print "delta: ", delta, " added: ", abs(delta + last_delta), " workload: ", self.current_workload
 			if abs(delta + last_delta) <  self.time_step:
 				self.current_workload.value = workload
 				self.calculate_parameters(workload)
 				break
 			else:
 				self.current_workload.value += delta
 				self.calculate_parameters(self.current_workload.value)
			time.sleep(self.time_step)
 		self.changing_workload = False

 	def smooth_set_step(self, time_delta): 		
 		if self.current_workload.value != self.target_workload:
 			self.last_delta = self.workload_delta
 			self.workload_delta = self.time_step * ((random.random() * 2.0 - 1.0) + 10.0 *  sign(self.target_workload - self.current_workload.value))
 			#use two last deltas to determine if value oscilating around certain point
 			if abs(self.workload_delta + self.last_delta) <  self.time_step:
 				self.current_workload.value = self.target_workload
 				self.calculate_parameters(self.target_workload)
 				self.changing_workload = False
 				print "finished"
 			else:
 				self.current_workload.value += self.workload_delta
 				self.calculate_parameters(self.current_workload.value)
 		return True


 	def get_mapped_sensor(self, sID):
 		max_value = max([sensor_set.toList()[sID] for sensor_set in self.given_data])
 		min_value = min([sensor_set.toList()[sID] for sensor_set in self.given_data])
 		
 		for sensor in self.sensors:
 			if sensor.id == sID:
 				new_value = sensor.value / ((max_value - min_value) / 100.0)
 				return Sensor(name=sensor.name, id=sID, value=new_value, unit=sensor.unit)

 	def immediateOff(self):
 		"for testcases"
 		self.changing_workload = False
 		if self.changing_workload_thread != None:
 			self.changing_workload_thread.join()
 		self.set_current_workload(0.0)

 	def update(self,time_delta):
 		if not super(GeneratorDevice, self).update(time_delta):
 			return False
 		if self.changing_workload:
 			self.smooth_set_step(time_delta)
 		return True




class Sensor(object):

	def __init__(self,name,id,value,unit,max_value=None):
		self.id = id
		self.value = value
		self.name = name
		self.unit = unit
		self.max_value = max_value


def sign(x): 
    return 1 if x >= 0 else -1

