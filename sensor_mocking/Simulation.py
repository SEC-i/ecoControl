import Device
import BHKW
from PeakLoadBoiler import PlBoiler
from HeatStorage import HeatStorage
from Heating import Heating
from ElectricConsumer import ElectricConsumer
import time
from  threading import Thread

class Simulation(Thread):
    def __init__(self,step_size):
        Thread.__init__(self)
        self.bhkw = BHKW.BHKW(device_id=0)
        #self.peakload_boiler = PlBoiler(device_id=1)
        self.heat_storage = HeatStorage(device_id=1)
        self.heating = Heating(device_id=2)
        self.electric_consumer = ElectricConsumer(device_id=3)
        # update frequency
        self.time_step = 0.5
        # simulation speed
        self.step_size = step_size
        self.daemon = True
        self.devices = [self.bhkw, self.heat_storage, self.heating, self.electric_consumer]


    def run(self):
        self.mainloop_running = True
        self.mainloop()


    def mainloop(self):
        while self.mainloop_running:
            
            cur_time_millis = int(round(time.time() * 1000))
            time.sleep(self.time_step)

            time_delta = int(round(time.time() * 1000)) - cur_time_millis
            time_delta_sim = float(time_delta * self.step_size)
            
            self.bhkw.update(time_delta_sim, self.heat_storage)
            self.electric_consumer.update(time_delta_sim, self.bhkw)
            self.heating.update(time_delta_sim, self.heat_storage)
            self.heat_storage.update(time_delta_sim)

    def immediate_off(self):
        "for testcases"
        self.mainloop_running = False

    def set_heating(self, temperature):
        self.heating.target_temperature = temperature

    def set_electrical_consumption(self, energy):
        self.electric_consumer.sensors["energy_consumption"].value = energy
