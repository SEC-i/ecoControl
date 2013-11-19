import Device
import BHKW
from PeakLoadBoiler import PlBoiler
from HeatReservoir import HeatReservoir
import time
from  threading import Thread

class BHKW_Simulation:
	def __init__(self):

		self.BHKW = BHKW.BHKW(device_id=0)
		self.PlBoiler = PlBoiler(device_id=1)
		self.HeatReservoir = HeatReservoir(device_id=2)
		self.devices = [self.BHKW,self.PlBoiler,self.HeatReservoir]
		# the time_delta between current time and the last sucessful update call, per device (indexes correspond to self.devices)
		self.timeDeltas  = [0,0,0]

		self.timeStep = 0.03

		self.mainloopRunning = True
		self.start()

	def start(self):
		self.mainloopThread = Thread(target=self.mainloop,args=())
 		self.mainloopThread.start()

 	def setWorkload(self,device_id,workload):
 		device = [dev for dev in self.devices if dev.device_id == device_id][0]
 		if isinstance(device,Device.GeneratorDevice):
 			device.setcurrentWorkload(workload)
 			return "1"
 		else:
 			return "0"


	def mainloop(self):
		while self.mainloopRunning:
			curTimeMillis = int(round(time.time() * 1000))
			time.sleep(self.timeStep)

			timeDelta = int(round(time.time() * 1000)) - curTimeMillis
			self.timeDeltas = [oldDelta + timeDelta for oldDelta in self.timeDeltas]

			for i in range(len(self.devices)):
				wasUpdated = self.devices[i].update(self.timeDeltas[i])
				if wasUpdated:
					self.timeDeltas[i] = 0

	def immediateOff(self):
 		"for testcases"
 		self.mainloopRunning = False
 		if self.mainloopThread != None:
 			self.mainloopThread.join()


 	def getWorkload(self,device_id):
 		device = [dev for dev in self.devices if dev.device_id == device_id][0]
 		if isinstance(device,Device.GeneratorDevice):
 			return self.devices[device_id].currentWorkload.value



