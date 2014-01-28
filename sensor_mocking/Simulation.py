import Device
import BHKW
from PeakLoadBoiler import PlBoiler
from HeatStorage import HeatStorage
from Heating import Heating
import time
from  threading import Thread

class BHKW_Simulation(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.bhkw = BHKW.BHKW(device_id=0)
        #self.peakload_boiler = PlBoiler(device_id=1)
        self.heat_storage = HeatStorage(device_id=2)
        self.heating = Heating(device_id=3)
        self.time_step = 0.03
        self.daemon = True


    def run(self):
        self.mainloop_running = True
        self.mainloop()


    def mainloop(self):
        while self.mainloop_running:
            cur_time_millis = int(round(time.time() * 1000))
            time.sleep(self.time_step)

            time_delta = int(round(time.time() * 1000)) - cur_time_millis
            self.bhkw.update(time_delta, self.heat_storage )
            self.heating.update(time_delta, self.heat_storage)
            self.heat_storage.update(time_delta)

    def immediate_off(self):
        "for testcases"
        self.mainloop_running = False


