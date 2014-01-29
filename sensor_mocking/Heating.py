import Device
from Device import Sensor

milliseconds_per_hour = 1000 * 60 * 60
heat_capacity_air = 1.005


class Heating(Device.Device):
    def __init__(self, device_id):
        self.device_id = device_id
        self.name = "Heating"
        self.sensors = {"temperature":Sensor(name="temperature", id=0, value=18, unit=r"C")}
        self.target_temperature = 22
        # Type 22, 1.4m X 0.5m
        # W/m to 22 C = 90 W
        # room: 2x5x2.1m
        self.room_volume = 2 * 5 * 2.1
        self.power = 2.150 #kW

    def update(self, time_delta, heat_storage):
        self.heat_loss(time_delta)
        print "heating: " + str(self.sensors["temperature"].value)
        if self.sensors["temperature"].value < self.target_temperature:
            heat_storage.consume_power(self.power)
            self.heat_room(time_delta)
        

    def heat_loss(self, time_delta):
        time_delta_hour = time_delta / milliseconds_per_hour
        # assume cooling of power/2
        energy = (self.power/2) * time_delta_hour
        temperature_delta = energy / (self.room_volume * heat_capacity_air)

        self.sensors["temperature"].value -= temperature_delta

    def heat_room(self, time_delta):
        time_delta_hour = time_delta / milliseconds_per_hour
        energy = self.power * time_delta_hour
        temperature_delta = energy / (self.room_volume * heat_capacity_air)

        self.sensors["temperature"].value += temperature_delta
