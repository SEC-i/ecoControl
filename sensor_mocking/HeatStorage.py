import Device
from Device import Sensor
from Device import GeneratorDevice


class HeatStorage(Device.Device):

    def __init__(self, device_id):
        Device.Device.__init__(self, device_id)

        self.name = "HeatStorage"

        self.storage_capacity = 500 #l

        self.sensors = {"temperature":Sensor(name="temperature", id=0, value=40, unit=r"C", max_value=100)}
        self.target_temperature = 90
        self.input_energy = 0
        self.output_energy = 0
        #specific heat capacity
        self.c = 0.00116 # kwh/l * K

    def add_energy(self,energy):
        self.input_energy = energy

    def consume_energy(self,energy):
        self.output_energy = energy

    def update(self,time_delta):
        energy_delta =  self.input_energy - self.output_energy
        #compute water temperature from energy
        self.sensors["temperature"].value +=  energy_delta / (self.storage_capacity * self.c)

    def get_energy_demand(self):
        temperature_delta = self.target_temperature - self.sensors["temperature"].value
        energy = temperature_delta * self.c * self.storage_capacity
        return energy
