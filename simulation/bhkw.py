from device import Sensor, GeneratorDevice
import math
import time
from  threading import Thread
import random
import unittest
import sys

seconds_per_hour = 60 * 60.0

"""@doc please read the technical datasheet of vitobloc_200_EM,
which contains all the data which we are mocking here"""
class BHKW(GeneratorDevice):
    def __init__(self,device_id):
        GeneratorDevice.__init__(self,device_id)

        self.name = "BHKW"
        # workload is modulated starting from this value
        # ecoPower from 1,3 kw el or 4 kw th -> about 30% workload
        self.modulation = 30 


        self.sensors = {"workload":Sensor(name="workload", id=0, value=0, unit=r"%",graph_id=1),
                        "electrical_power":Sensor(name="electrical_power", id=1, value=0, unit="kW",graph_id=1),
                        "thermal_power":Sensor(name="thermal_power", id=2, value=0, unit="kW",graph_id=1),
                        "gasinput":Sensor(name="gas_input", id=3, value=0, unit="kW",graph_id=1) }


        self.given_data = []
        # workload in percent, other data in kW
        #self.given_data.append({"workload":0, "electrical_power":0, "thermal_power":0, "gasinput":0})
        #self.given_data.append({"workload":25, "electrical_power":12.5, "thermal_power":20, "gasinput":43})
        #self.given_data.append({"workload":50, "electrical_power":25, "thermal_power":46, "gasinput":86})
        #self.given_data.append({"workload":75, "electrical_power":38, "thermal_power":64, "gasinput":118})
        #self.given_data.append({"workload":99, "electrical_power":50, "thermal_power":81, "gasinput":145})

        # use smaller bhkw of pamiru48: Vaillant ecoPower 4.7
        # gas input based on maximum 90% efficiency scaling down like vitobloc
        # electric/thermal power scaled down almost linear
        self.given_data.append({"workload":31, "electrical_power":1.5, "thermal_power":4.7, "gasinput":5.75})
        self.given_data.append({"workload":50, "electrical_power":2.35, "thermal_power":7, "gasinput":11.27})
        self.given_data.append({"workload":75, "electrical_power":3.53, "thermal_power":10, "gasinput":15.73})
        self.given_data.append({"workload":99, "electrical_power":4.7, "thermal_power":12.5, "gasinput":19.1})
        
        #0 = follow thermal, 1 = follow electric
        self.mode = 0


    def find_bounding_datasets(self,value,type):
        # get the two datasets in between which the workload resides
        for i in range(len(self.given_data)-1):
            if value < self.given_data[i+1][type]:
                data_set1 = self.given_data[i]
                data_set2 = self.given_data[i+1]
                break
        else:
            data_set1 = self.given_data[-2] #last and second to last
            data_set2 = self.given_data[-1]
        return (data_set1,data_set2)



    def calculate_parameters(self,value,type):
        #return 0 initialized dict if value is under threshold
        if value < self.given_data[0][type]:
            return {key: 0 for (key, value) in self.given_data[0].items()}
        
        ret_dict = {}
        data_set1,data_set2 = self.find_bounding_datasets(value,type)
        mu = value-data_set1[type]
        

        #return interpolated values from datasheet
        for key in self.sensors:
            if (key!= type):
                interp_value = cosine_interpolate(data_set1[key], data_set2[key], mu)
                ret_dict[key] = interp_value
            else:
                ret_dict[key]= value
        return ret_dict

    def modulating(self):
        if self.target_workload > self.modulation:
            return
       # elif self.target_workload > (self.modulation * 0.8):
       #     self.target_workload = self.modulation
        else:
            self.target_workload = 0

    def update(self,time_delta,heat_storage,electric_consumer):
        time_delta_hour = time_delta / seconds_per_hour

        if self.mode == 0:
            needed_thermal_energy = heat_storage.get_energy_demand()
            self.target_workload = self.calculate_parameters(needed_thermal_energy / time_delta_hour,"thermal_power")["workload"]
        else:
            self.target_workload = self.calculate_parameters(electric_consumer.get_power_demand(),"electrical_power")["workload"]
            #ensure heatstorage is not overheated
            if heat_storage.get_temperature() > heat_storage.target_temperature:
                self.target_workload = 0
        self.modulating()
        self.smooth_set_step(time_delta)            
        new_values = self.calculate_parameters(self.sensors["workload"].value,"workload")
        #set values for current simulation step
        for key in new_values:
            if (key != "workload"):
                self.sensors[key].value = new_values[key]
        
        if self.mode == 0:
            heat_storage.add_energy(self.sensors["thermal_power"].value * time_delta_hour)
        else:
            heat_storage.add_energy(self.sensors["electrical_power"].value * time_delta_hour)

    def get_electrical_power(self):
        return self.sensors["electrical_power"].value


def cosine_interpolate(d1,d2,mu):
    if mu>d2:
        return d2
    if mu< d1:
        return d1
    mu /= 25.0
    mu2 = (1-math.cos(mu*math.pi)) / 2.0
    return (d1 * (1-mu2) + d2 * mu2)
