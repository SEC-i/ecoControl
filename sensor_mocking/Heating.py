import Device
from Device import Sensor

milliseconds_per_hour = 1000 * 60 * 60
#J /( m^3 * K)
heat_capacity_air = 1290

#formulas from http://www.model.in.tum.de/um/research/groups/ai/fki-berichte/postscript/fki-227-98.pdf
#and http://www.inference.phy.cam.ac.uk/is/papers/DanThermalModellingBuildings.pdf


class Heating(Device.Device):
    def __init__(self, device_id):
        self.device_id = device_id
        self.name = "Heating"
        self.sensors = {"temperature":Sensor(name="temperature",id=0,value=20, unit=r"C"),
                        "temperature_outside":Sensor(name="temperature_outside",id=1,value=5,unit=r"C")}
        self.target_temperature = 30
        # Type 22, 1.4m X 0.5m
        # W/m to 22 C = 90 W
        # room: 2x5x2.1m
        self.room_volume = 2 * 5 * 2.1
        self.power = 2150 #W
        self.window_surface = 5 #m^2
        #heat transfer coefficient normal glas window, W/(m^2 * K)
        self.k = 5.9
        #self.energy = 

        # J / K, approximation for 5m^3 wall, spec heat capacity brick = 0.84 J/(g * K)
        heat_cap_brick =  9 * 10**5

        self.heat_capacity = heat_capacity_air * self.room_volume + heat_cap_brick



    def update(self, time_delta, heat_storage):
        time_delta_hour = time_delta / milliseconds_per_hour
        self.heat_loss(time_delta)
        #print "room temperature: " + str(self.sensors["temperature"].value)
        if self.sensors["temperature"].value < self.target_temperature:
            heat_storage.consume_energy(self.power / 1000 * time_delta_hour)
            self.heat_room(time_delta)
        

    def heat_loss(self, time_delta):
        time_delta_seconds = time_delta / 1000
        # assume cooling of power/2
        d = self.sensors["temperature"].value - self.sensors["temperature_outside"].value
        #in Watt
        cooling_rate  =(self.window_surface * self.k / self.heat_capacity)

        self.sensors["temperature"].value -=  d * cooling_rate * time_delta_seconds


    def heat_room(self, time_delta):
        time_delta_seconds = time_delta / 1000
        # 0.8 denotes heating power to thermal energy efficiency
        heating_efficiency = 0.8 / (self.heat_capacity)
        
        temperature_delta = self.power *   heating_efficiency * time_delta_seconds

        self.sensors["temperature"].value += temperature_delta



    # def heat_loss(self, time_delta):
    #     time_delta_hour = time_delta / milliseconds_per_hour
    #     # assume cooling of power/10
    #     energy = (self.power/10) * time_delta_hour
    #     temperature_delta = energy / (self.room_volume * heat_capacity_air)

    #     self.sensors["temperature"].value -= temperature_delta
