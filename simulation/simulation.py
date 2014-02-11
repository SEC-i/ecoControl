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
        self.peakload_boiler = PLB(device_id=4, power=4.5) # PLB of pamiru48
        self.heat_storage = HeatStorage(device_id=1)
        self.electric_consumer = ElectricConsumer(device_id=3)

        self.heating = Heating(device_id=2)
        
        # update frequency
        self.time_step = time_step
        # simulation speed
        self.step_size = step_size
        self.remaining_time = 0 #ms
        self.forwarded_seconds = 0
        self.total_forwarded_seconds = 0
        self.fast_motion_values = {}
                
        self.daemon = True
        self.devices = {self.bhkw.device_id:self.bhkw,
                        self.heat_storage.device_id:self.heat_storage,
                        self.electric_consumer.device_id:self.electric_consumer,
                        self.peakload_boiler.device_id:self.peakload_boiler,
                        self.heating.device_id:self.heating}
        
        self.init_fast_motion()
        
        self.plotting = plotting
        self.duration = duration #seconds
        self.fast_forwarding = False
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
        time_since_plot = 0
        #fill the parameters with starting values
        step_start_time = 0
        step_end_time = 0.00002
        while self.mainloop_running:
            
            time_delta = step_end_time - step_start_time
            if time_delta <= 0.0000001:
                # minimal time passed
                time_delta = 0.0001
            step_start_time =clock()
            time_since_plot += time_delta


            # update target temperature
            self.set_heating(self.get_current_target_temperature())

            sim_step_time = float(time_delta * self.step_size) #in secs
            self.update_devices(sim_step_time)
            

            if self.plotting and time_since_plot >= self.time_step:
                self.plot()
                time_since_plot = 0
            
            # terminate plotting
            if self.duration != None and time()-self.start_time > self.duration:

                print "simulation finished"
                return

            # terminate plotting
            if self.duration != None and time()-self.start_time > self.duration:

                print "simulation finished"
                return
            step_end_time = clock()

    def update_devices(self, time_delta):
        self.bhkw.update(time_delta, self.heat_storage,self.electric_consumer)
        self.peakload_boiler.update(time_delta, self.heat_storage)
        self.electric_consumer.update(time_delta, self.bhkw)
        self.heating.update(time_delta, self.heat_storage)
        self.heat_storage.update(time_delta)

    def immediate_off(self):
        "for testcases"
        self.mainloop_running = False

    def fast_forward(self, seconds, num_values):
        #simulation duration in real-time
        self.init_fast_motion()
        self.ff_remaining_sim_time = self.forwarded_seconds = seconds
        self.ff_step = self.ff_remaining_sim_time / num_values
        self.ff_start = time()
        # start ff loop (in simulation thread)
        self.fast_forwarding = True
        self.fast_forward_loop()
        self.fast_forwarding = False
        # update total_forwarded_seconds
        self.total_forwarded_seconds += seconds
        return self.fast_motion_values
    
    def fast_forward_loop(self):
        internal_step = self.ff_step * 0.1
        internal_steps = 0
        t0 = clock()
        while self.ff_remaining_sim_time > 0:
            self.ff_remaining_sim_time -= internal_step
            self.set_heating(self.get_current_target_temperature(ff = True))
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
        self.heating.target_temperature = temperature
    
    def set_outside_temperature(self, temperature):
        self.heating.sensors["temperature_outside"] = temperature    

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

    def get_current_target_temperature(self, ff = False):
        if(ff):
            time_fast_forward_start = (self.ff_start-self.start_time)
            time_already_fast_forwarded = (self.forwarded_seconds-self.ff_remaining_sim_time)
            current_day_seconds = ( time_fast_forward_start + time_already_fast_forwarded + self.total_forwarded_seconds) % (60*60*24)
            current_hour = current_day_seconds / (60*60)
        else:
            current_day_seconds = (time()-self.start_time + self.total_forwarded_seconds) % (60*60*24)
            current_hour = current_day_seconds / (60*60)

        if(current_hour<6):
            return 16.0
        elif(current_hour<8):
            return 18.0
        elif(current_hour<10):
            return 18.5
        elif(current_hour<12):
            return 19.0
        elif(current_hour<14):
            return 20.0
        elif(current_hour<16):
            return 21.0
        elif(current_hour<18):
            return 25.0
        elif(current_hour<20):
            return 24.0
        elif(current_hour<22):
            return 20.0
        else:
            return 18.0
