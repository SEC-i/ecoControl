import Device
import BHKW
from PeakLoadBoiler import PlBoiler
from HeatReservoir import HeatReservoir
import time
from  threading import Thread

class BHKW_Simulation(Thread):
	def __init__(self):
		Thread.__init__(self)

		self.bhkw = BHKW.BHKW(device_id=0)
		self.peakload_boiler = PlBoiler(device_id=1)
		self.heat_reservoir = HeatReservoir(device_id=2)
		self.devices = [self.bhkw,self.peakload_boiler,self.heat_reservoir]
		# the time_delta between current time and the last sucessful update call, per device (indexes correspond to self.devices)
		self.time_deltas  = [0,0,0]

		self.time_step = 0.03
		self.daemon = True


	def run(self):
		self.mainloop_running = True
		self.mainloop()

 	def set_workload(self,device_id,workload):
 		device = [dev for dev in self.devices if dev.device_id == device_id][0]
 		if isinstance(device, Device.GeneratorDevice):
 			device.set_current_workload(workload)
 			return "1"
 		else:
 			return "0"


	def mainloop(self):
		while self.mainloop_running:
			cur_time_millis = int(round(time.time() * 1000))
			time.sleep(self.time_step)

			time_delta = int(round(time.time() * 1000)) - cur_time_millis
			self.time_deltas = [old_delta + time_delta for old_delta in self.time_deltas]

			for i in range(len(self.devices)):
				was_updated = self.devices[i].update(self.time_deltas[i])
				if was_updated:
					self.time_deltas[i] = 0

	def immediate_off(self):
 		"for testcases"
 		self.mainloop_running = False
 		#if self.mainloopThread != None:
 		#	self.mainloopThread.join()


 	def get_workload(self,device_id):
 		device = [dev for dev in self.devices if dev.device_id == device_id][0]
 		if isinstance(device,Device.GeneratorDevice):
 			return self.devices[device_id].current_workload.value



