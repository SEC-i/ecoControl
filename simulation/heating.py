from device import Device, Sensor
import random

seconds_per_hour = 60 * 60
#J /( m^3 * K)
heat_capacity_air = 1290

# let's use 15 heating systems
amount_of_heating_systems = 22

#formulas from http://www.model.in.tum.de/um/research/groups/ai/fki-berichte/postscript/fki-227-98.pdf
#and http://www.inference.phy.cam.ac.uk/is/papers/DanThermalModellingBuildings.pdf


class Heating(Device):
    def __init__(self, device_id):
        self.device_id = device_id
        self.name = "Heating"
        self.sensors = {"temperature":Sensor(name="temperature",id=0,value=20, unit=r"C",graph_id=2),
                        "temperature_outside":Sensor(name="temperature_outside",id=1,value=5,unit=r"C",graph_id=2)}
        self.target_temperature = 25
        # Type 22, 1.4m X 0.5m
        # W/m to 22 C = 90 W
        # room: 2x5x2.1m
        self.room_volume = 3 * 5 * 3 * amount_of_heating_systems
        self.max_power = 4000 * amount_of_heating_systems #W
        self.current_power = 0
        self.window_surface = 5 * amount_of_heating_systems#m^2
        #heat transfer coefficient normal glas window, W/(m^2 * K)
        self.k = 5.9
        # J / K, approximation for 15m^2walls, 0.2m thickness, walls, ceiling, spec heat capacity brick = 1360 KJ/(m^3 * K)
        heat_cap_brick =  1360 * 100 * (4*3*5 * 0.2)

        self.heat_capacity = heat_capacity_air * self.room_volume + heat_cap_brick



    def update(self, time_delta, heat_storage):
        time_delta_hour = time_delta / seconds_per_hour
        self.heat_loss(time_delta)
        
        #slow rise and  fall of heating
        change_speed = 1
        rand = change_speed * (random.random() * 2.0 - 1.0)
        slope = change_speed * sign(self.target_temperature - self.sensors["temperature"].value)
        power_delta = (rand + slope ) * time_delta

        self.current_power += power_delta
        self.current_power =  max(min(self.current_power, self.max_power),0)
        
        heat_storage.consume_energy(self.current_power / 1000 * time_delta_hour)
        self.heat_room(time_delta)
        

    def heat_loss(self, time_delta):
        # assume cooling of power/2
        d = self.sensors["temperature"].value - self.sensors["temperature_outside"].value
        #in Watt
        cooling_rate  =(self.window_surface * self.k / self.heat_capacity)
        self.sensors["temperature"].value -=  d * cooling_rate * time_delta


    def heat_room(self, time_delta):
        # 0.8 denotes heating power to thermal energy efficiency
        heating_efficiency = 0.8 / (self.heat_capacity)       
        temperature_delta = self.current_power *   heating_efficiency * time_delta
        self.sensors["temperature"].value += temperature_delta

def sign(x): 
    return 1 if x >= 0 else -1

