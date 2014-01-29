import Device
from Device import Sensor
from Device import GeneratorDevice
import math
import time
from  threading import Thread
import random
import unittest
import sys



"""@doc please read the technical datasheet of vitobloc_200_EM,
which contains all the data which we are mocking here"""
class BHKW(GeneratorDevice):
    def __init__(self,device_id):
        GeneratorDevice.__init__(self,device_id)

        self.name = "BHKW"

        # self.current_electrical_power =  Sensor(name="electrical_power", id=1, value=0, unit="kW")
        # self.current_thermal_power    =  Sensor(name="thermal_power", id=2, value=0, unit="kW")
        # self.current_gasinput         =  Sensor(name="gas_input", id=3, value=0, unit="kW")

        #index corresponds to sensor id

        self.sensors = {"workload":Sensor(name="workload", id=0, value=0, unit=r"%"),
                        "electrical_power":Sensor(name="electrical_power", id=1, value=0, unit="kW"),
                        "thermal_power":Sensor(name="thermal_power", id=2, value=0, unit="kW"),
                        "gasinput":Sensor(name="gas_input", id=3, value=0, unit="kW") }
        
        self.current_workload  = self.sensors["workload"]

        self.given_data = []
        #workload in percent, other data in kW
        self.given_data.append({"workload":0, "electrical_power":0, "thermal_power":0, "gasinput":0})
        self.given_data.append({"workload":25, "electrical_power":12.5, "thermal_power":20, "gasinput":43})
        self.given_data.append({"workload":50, "electrical_power":25, "thermal_power":46, "gasinput":86})
        self.given_data.append({"workload":75, "electrical_power":38, "thermal_power":64, "gasinput":118})
        self.given_data.append({"workload":99, "electrical_power":50, "thermal_power":81, "gasinput":145})


    def find_bounding_datasets(self,value,type):
        #get the two datasets in between which the workload resides
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
        data_set1,data_set2 = self.find_bounding_datasets(value,type)
        
        mu = self.sensors[type].value-data_set1[type]
        print "calc " + type + " "+ str(data_set1) + " " + str(data_set2) + " " + str(mu)
        ret_dict = {}

        #return interpolated values from datasheet
        for key in self.sensors:
            if (key!= type):
                interp_value = cosine_interpolate(data_set1[key], data_set2[key], mu)
                ret_dict[key] = interp_value
        return ret_dict


    def update(self,time_delta,heat_storage):
        needed_thermal_power = heat_storage.get_power_demand(time_delta)
        self.target_workload = self.calculate_parameters(needed_thermal_power,"thermal_power")["workload"]
        print "target workload: " + str(self.target_workload)
        self.smooth_set_step(time_delta)
        new_values = self.calculate_parameters(self.current_workload,"workload")
        
        #set values for current simulation step
        for key in new_values:
            if (key != "workload"):
                self.sensors[key].value = new_values[key] 

        heat_storage.set_power(self.sensors["thermal_power"].value)
        print "bhkw_temp: " + str(self.sensors["thermal_power"].value)
        print "bhkw_workload: " + str(self.sensors["workload"].value)



def cosine_interpolate(d1,d2,mu):
    mu /= 25.0
    mu2 = (1-math.cos(mu*math.pi)) / 2.0
    return (d1 * (1-mu2) + d2 * mu2)
