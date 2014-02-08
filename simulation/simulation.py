from datetime import datetime
from time import time, sleep,clock
from threading import Thread

from bhkw import BHKW
from peak_load_boiler import PLB
from heat_storage import HeatStorage
from heating import Heating
from electric_consumer import ElectricConsumer

class Simulation(Thread):
    def __init__(self,step_size=1,time_step=0.01,plotting=False,duration=None):
        Thread.__init__(self)
        self.bhkw = BHKW(device_id=0)
        self.peakload_boiler = PLB(device_id=4, power=45) # PLB of pamiru48
        self.heat_storage = HeatStorage(device_id=1)
        self.electric_consumer = ElectricConsumer(device_id=3)

        self.heating = []
        self.heating.append(Heating(device_id=2))
        
        for i in range(5,11):
            self.heating.append(Heating(device_id=i))
        
        # update frequency
        self.time_step = time_step
        # simulation speed
        self.step_size = step_size
        self.remaining_time = 0 #ms
        self.forwarded_time = 0
        self.fast_motion_values = {}
                
        self.daemon = True
        self.devices = {self.bhkw.device_id:self.bhkw,
                        self.heat_storage.device_id:self.heat_storage,
                        self.electric_consumer.device_id:self.electric_consumer,
                        self.peakload_boiler.device_id:self.peakload_boiler}
        
        for heating in self.heating:
            self.devices[heating.device_id] = heating
        
        self.init_fast_motion()
        
        self.plotting = plotting
        self.duration = duration #seconds
        self.ff_remaining_sim_time = 0
        self.stat_info = {}
        if self.plotting:
            self.init_plotting()

    def run(self):
        self.mainloop_running = True
        self.mainloop()

    def mainloop(self):
        print "simulating..."
        self.start_time = time()
        step_start_time = time()
        sleep(0.002)
        step_end_time = time()
        time_since_plot = 0
        while self.mainloop_running:
            
            time_delta = step_end_time - step_start_time
            step_start_time =clock()
            time_since_plot += time_delta
            #sleep(self.time_step - min(time_loss,self.time_step))

            if self.ff_remaining_sim_time != 0:
                self.fast_forward_loop()
                step_start_time = clock()
            
            sim_step_time = float(time_delta * self.step_size) #in secs
            self.update_devices(sim_step_time)
            

            if self.plotting and time_since_plot >= self.time_step:
                self.plot()
                time_since_plot = 0
            
            # terminate plotting
            if self.duration != None and time()-self.start_time > self.duration:

                print "simulation finished"
                return
            step_end_time = clock()

    def update_devices(self, time_delta):
        self.bhkw.update(time_delta, self.heat_storage,self.electric_consumer)
        self.peakload_boiler.update(time_delta, self.heat_storage)
        self.electric_consumer.update(time_delta, self.bhkw)
        for heating in self.heating:
            heating.update(time_delta, self.heat_storage)
        self.heat_storage.update(time_delta)

    def immediate_off(self):
        "for testcases"
        self.mainloop_running = False

    def fast_forward(self, seconds,num_values):
        #simulation duration in real-time
        self.init_fast_motion()
        self.ff_remaining_sim_time = seconds
        self.ff_step = self.ff_remaining_sim_time / num_values
        while self.ff_remaining_sim_time > 0:
            sleep(0.1)
        return self.fast_motion_values
    
    def fast_forward_loop(self):
        internal_step = self.ff_step * 0.1
        internal_steps = 0
        t0 = clock()
        while self.ff_remaining_sim_time > 0:
            self.ff_remaining_sim_time -= internal_step
            self.update_devices(internal_step)
            internal_steps += internal_step
            if internal_steps >= self.ff_step:
                if self.plotting:
                    self.plot()
                else:
                    self.add_sensor_data()
                internal_steps = 0
        
        self.stat_info["fast_forward_duration"] = clock() - t0
        

    def set_heating(self, temperature):
        for heating in self.heating:
            heating.target_temperature = temperature
    
    def set_outside_temperature(self, temperature):
        for heating in self.heating:
            heating.sensors["temperature_outside"] = temperature    

    def set_electric_consumption(self, power):
        self.electric_consumer.sensors["electric_consumption"].value = power
        
        
        
    def get_sensor(self,device_id,sensor_id=None,sensor_name=None):
        dev = self.devices[device_id]
        if sensor_id!=None:
            for key,sens in dev.sensors.items():
                if sensor_id == sens.id:
                    return sens
        elif sensor_name != None:
            for key,sens in dev.sensors.items():
                if sensor_name == sens.name:
                    return sens
        return None  
                
                
    
    
    def init_plotting(self):
        self.plotting_data = {}
        
        
        for key,device in self.devices.items():
            for key,sensor in device.sensors.items():
                if sensor.graph_id != None:
                    if sensor.graph_id not in self.plotting_data:
                        self.plotting_data[sensor.graph_id] = {"unit":sensor.unit}
                    key_name = sensor.name + "." +  str(device.device_id)
                    self.plotting_data[sensor.graph_id][key_name] = []        
    
    def plot(self):
        for key,device in self.devices.items():
            for key,sensor in device.sensors.items():
                if sensor.graph_id != None:
                    key_name = sensor.name + "." + str(device.device_id)
                    self.plotting_data[sensor.graph_id][key_name].append(sensor.value)

    def init_fast_motion(self):
        for key,device in self.devices.items():
            for key,sensor in device.sensors.items():
                if device.device_id not in self.fast_motion_values:
                    self.fast_motion_values[device.device_id] = {}
                self.fast_motion_values[device.device_id][sensor.name] = []

    def add_sensor_data(self):
        for key,device in self.devices.items():
            for key,sensor in device.sensors.items():
                self.fast_motion_values[device.device_id][sensor.name].append(sensor.value)
