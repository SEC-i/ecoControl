
class Device(object):

	def __init__(self,device_id):
		self.device_id = device_id
		self.givenData = []

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



class Sensor(object):

	def __init__(self,name,id,value,unit):
		self.id = id
		self.value = value
		self.name = name
		self.unit = unit
