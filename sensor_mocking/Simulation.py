import Device
import BHKW
from PeakLoadBoiler import PLB
from HeatStorage import HeatStorage
from Heating import Heating
from ElectricConsumer import ElectricConsumer
import time
from  threading import Thread

class Simulation(Thread):
    def __init__(self,step_size=1,time_step=0.01,plotting=False,duration=None):
        Thread.__init__(self)
        self.bhkw = BHKW.BHKW(device_id=0)
        self.peakload_boiler = PLB(device_id=4)
        self.heat_storage = HeatStorage(device_id=1)
        self.heating = Heating(device_id=2)
        self.electric_consumer = ElectricConsumer(device_id=3)
        # update frequency
        self.time_step = time_step
        # simulation speed
        self.step_size = step_size
        self.daemon = True
        self.devices = {self.bhkw.device_id:self.bhkw,
                        self.heat_storage.device_id:self.heat_storage,
                        self.heating.device_id:self.heating,
                        self.electric_consumer.device_id:self.electric_consumer,
                        self.peakload_boiler.device_id:self.peakload_boiler}
        
        self.plotting = plotting
        self.plotting_data = {}
        self.duration = duration#
        
        for key,device in self.devices.items():
            for key,sensor in device.sensors.items():
                if sensor.graph_id != None:
                    if sensor.graph_id not in self.plotting_data:
                        self.plotting_data[sensor.graph_id] = {"unit":sensor.unit} 
                    self.plotting_data[sensor.graph_id][sensor.name] = []


    def run(self):
        self.mainloop_running = True
        self.mainloop()


    def mainloop(self):
        print "simulating..."
        self.start_time = time.time()
        count = 0
        time_loss = 0
        while self.mainloop_running:
            
            cur_time_millis = time.time() * 1000
            time.sleep(self.time_step - min(time_loss,self.time_step))

            t0 = time.time()
            time_delta = time.time() * 1000 - cur_time_millis
            time_delta_sim = float(time_delta * self.step_size)
            
            self.bhkw.update(time_delta_sim, self.heat_storage)
            self.peakload_boiler.update(time_delta_sim, self.heat_storage)
            self.electric_consumer.update(time_delta_sim, self.bhkw)
            self.heating.update(time_delta_sim, self.heat_storage)
            self.heat_storage.update(time_delta_sim)
            count += 1
            
            if self.plotting:
                self.plot()
            
            time_loss = time.time() - t0
                
            if self.duration != None and (time.time() - self.start_time) > self.duration:
                print "simulation finished"
                print count
                return

    def immediate_off(self):
        "for testcases"
        self.mainloop_running = False

    def set_heating(self, temperature):
        self.heating.target_temperature = temperature

    def set_electrical_consumption(self, energy):
        self.electric_consumer.sensors["energy_consumption"].value = energy
        
    
    def plot(self):
        for key,device in self.devices.items():
            for key,sensor in device.sensors.items():
                if sensor.graph_id != None:
                    self.plotting_data[sensor.graph_id][sensor.name].append(sensor.value)
                
