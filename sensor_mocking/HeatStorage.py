import Device
from Device import Sensor
from Device import GeneratorDevice

milliseconds_per_hour = 1000 * 60 * 60

class HeatStorage(Device.Device):

    def __init__(self, device_id):
        Device.Device.__init__(self, device_id)

        self.name = "HeatStorage"

        self.storage_capacity = 500 #l

        self.sensors = {"temperature":Sensor(name="temperature", id=0, value=0, unit=r"C", max_value=100)}
        self.target_temperature = 90
        self.input_power = 0
        self.output_power = 0
        #specific heat capacity
        self.c = 0.00116#kwh/l * K

    def set_power(self,power):
        self.input_power = power

    def consume_power(self,power):
        self.output_power = power

    def update(self,time_delta):
        time_delta_hour = time_delta / milliseconds_per_hour
        power_delta =  self.input_power - self.output_power
        #compute water temperature from power
        self.sensors["temperature"].value +=  power_delta * time_delta_hour / (self.storage_capacity * self.c)

    def get_power_demand(self):
        temperature_delta = self.target_temperature - self.sensors["temperature"].value
        power = temperature_delta * self.c * self.storage_capacity
        return power

        

