import Device
from Device import Sensor

milliseconds_per_hour = 1000 * 60 * 60
heat_capacity_air = 1.005

#formulas from http://www.model.in.tum.de/um/research/groups/ai/fki-berichte/postscript/fki-227-98.pdf


class Heating(Device.Device):
    def __init__(self, device_id):
        self.device_id = device_id
        self.name = "Heating"
        self.sensors = {"temperature":Sensor(name="temperature",id=0,value=20, unit=r"C"),
                        "temperature_outside":Sensor(name="temperature_outside",id=1,value=5,unit=r"C")}
        self.target_temperature = 22
        # Type 22, 1.4m X 0.5m
        # W/m to 22 C = 90 W
        # room: 2x5x2.1m
        self.room_volume = 2 * 5 * 2.1
        self.power = 2.150 #kW
        self.window_surface = 5 #m^2
        #heat transfer coefficient normal glas window, W/(m^2 * K)
        self.k = 5.9


    def update(self, time_delta, heat_storage):
        time_delta_hour = time_delta / milliseconds_per_hour
        self.heat_loss(time_delta)
        print "room temperature: " + str(self.sensors["temperature"].value)
        if self.sensors["temperature"].value < self.target_temperature:
            heat_storage.consume_energy(self.power * time_delta_hour)
            self.heat_room(time_delta)
        

    # def heat_loss(self, time_delta):
    #     time_delta_hour = time_delta / milliseconds_per_hour
    #     # assume cooling of power/2
    #     d = self.sensors["temperature"].value - self.sensors["temperature_outside"].value
    #     #in Watt
    #     energy_loss  = d * self.window_surface * self.k * time_delta_hour
    #     energy_room = self.power * 1000  * time_delta_hour - energy_loss
    #     print "energy_room: " + str(energy_room)


    #     air_pressure = 1.2041
    #     gas_constant = 287 # J/(kg * K)


    #     temperature = self.sensors["temperature"].value
    #     normalized_room_temp = (gas_constant * temperature)/(air_pressure * self.room_volume * heat_capacity_air)
    #     self.sensors["temperature"].value =  normalized_room_temp * energy_room * time_delta_hour


    def heat_room(self, time_delta):
        time_delta_hour = time_delta / milliseconds_per_hour
        energy = self.power * time_delta_hour
        temperature_delta = energy / (self.room_volume * heat_capacity_air)

        self.sensors["temperature"].value += temperature_delta



    def heat_loss(self, time_delta):
        time_delta_hour = time_delta / milliseconds_per_hour
        # assume cooling of power/2
        energy = (self.power/10) * time_delta_hour
        temperature_delta = energy / (self.room_volume * heat_capacity_air)

        self.sensors["temperature"].value -= temperature_delta

