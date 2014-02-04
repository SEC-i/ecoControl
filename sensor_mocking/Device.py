from  threading import Thread
import random
import time

class Device(object):

    def __init__(self, device_id):
        self.device_id = device_id
        self.name = "Abstract Device"
        self.sensors = {}
    
    def update(self, time_delta):
        pass




class GeneratorDevice(Device):

    def __init__(self, device_id):
        Device.__init__(self, device_id)

        self.name = "Abstract GeneratorDevice"

        #internalState
        self.changing_workload = False
        self.changing_workload_thread = None
        self.target_workload  = 0
        self.last_delta = 0

    def smooth_set_step(self, time_delta):      
        if self.sensors["workload"].value != self.target_workload:
            change_speed = 0.001
            rand = change_speed * (random.random() * 2.0 - 1.0)
            slope = change_speed * sign(self.target_workload - self.sensors["workload"].value)
            workload_delta = (rand + slope ) * time_delta
            self.sensors["workload"].value += workload_delta
            # clamp to 0-99
            self.sensors["workload"].value = max(min(self.sensors["workload"].value, 99),0)
        return True


    def get_mapped_sensor(self, sID):
        max_value = max([sensor_set.toList()[sID] for sensor_set in self.given_data])
        min_value = min([sensor_set.toList()[sID] for sensor_set in self.given_data])
        
        for key,sensor in self.sensors.items():
            if sensor.id == sID:
                new_value = sensor.value / ((max_value - min_value) / 100.0)
                return Sensor(name=sensor.name, id=sID, value=new_value, unit=sensor.unit)

    def immediateOff(self):
        "for testcases"
        self.changing_workload = False
        if self.changing_workload_thread != None:
            self.changing_workload_thread.join()
        self.set_current_workload(0.0)

    def update(self,time_delta,heat_storage):
        if self.changing_workload:
            self.smooth_set_step(time_delta)
        return True




class Sensor(object):

    def __init__(self,name,id,value,unit,max_value=None,graph_id=None):
        self.id = id
        self.value = value
        self.name = name
        self.unit = unit
        self.max_value = max_value
        self.graph_id = graph_id


def sign(x): 
    return 1 if x >= 0 else -1
