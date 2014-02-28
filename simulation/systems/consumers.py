import time
import math

from data import outside_temperatures_2013, daily_electrical_demand
from helpers import BaseSystem, sign


class ThermalConsumer(BaseSystem):

    """ physically based heating, using formulas from 
    http://www.model.in.tum.de/um/research/groups/ai/fki-berichte/postscript/fki-227-98.pdf and
    http://www.inference.phy.cam.ac.uk/is/papers/DanThermalModellingBuildings.pdf """

    def __init__(self, env, heat_storage):
        BaseSystem.__init__(self, env)
        self.heat_storage = heat_storage

        self.target_temperature = 25
        self.total_consumption = 0
        self.temperature_room = 20

        # list of 24 values representing  target_temperature per hour
        self.daily_demand = [15, 15, 16, 15, 15, 15, 19, 20, 21,
                             20, 20, 21, 20, 22, 22, 21, 22, 22, 22, 22, 22, 22, 21, 17]

        # data from pamiru48
        # has 12 apartments with 22 persons
        self.total_heated_volume = 650  # m^3
        appartments  = 12
        avg_rooms_per_appartment = 4
        avg_room_volume = self.total_heated_volume / (appartments * avg_rooms_per_appartment)
        #avg surface of a cube side, so multiply with 6 to get the whole surface
        avg_wall_size = avg_room_volume ** (2/3.0) #m^2
        # assume 100W heating demand per m^2, rule of thumb for new housings
        self.max_power = self.total_heated_volume * 100  # W
        self.current_power = 0
        # m^2
        self.window_surface = (avg_wall_size/2.0) * avg_rooms_per_appartment * appartments

        specific_heat_capacity_brick = 1360 * 10 ** 6  # J/(m^3 * K)
        # J / K, approximation for 5 walls including ceiling, 0.2m wall thickness, 
        heat_cap_brick_per_room = specific_heat_capacity_brick *  (avg_wall_size * 5 * 0.2)
        # avg rooms per appartent,number of appartments
        heat_cap_brick = heat_cap_brick_per_room * 4 * 12

        #J /( m^3 * K)
        specific_heat_capacity_air = 1290
        heat_capacity_air = specific_heat_capacity_air * self.total_heated_volume

        self.heat_capacity =  heat_capacity_air + heat_cap_brick

    def step(self):
        self.simulate_consumption()
        consumption = self.get_consumption_energy()
        self.total_consumption += consumption
        self.heat_storage.consume_energy(consumption)

    def get_consumption_power(self):
        return self.current_power / 1000.0

    def get_consumption_energy(self):
        return self.get_consumption_power() / self.env.steps_per_measurement

    def simulate_consumption(self):
        # calculate variation using daily demand
        self.target_temperature = self.daily_demand[
            time.gmtime(self.env.now).tm_hour]

        self.heat_loss()

        # slow rise and fall of heating
        slope = sign(self.target_temperature - self.temperature_room)
        power_delta = slope * self.env.step_size
        self.current_power += power_delta

        # clamp to maximum power
        self.current_power = max(min(self.current_power, self.max_power), 0)
        self.heat_room()

    def heat_loss(self):
        # assume cooling of power/2
        d = self.temperature_room - \
            self.get_outside_temperature()
        # heat transfer coefficient normal glas window, W/(m^2 * K)
        k = 5.9
        # in Watt
        cooling_rate = (self.window_surface * k / self.heat_capacity)
        self.temperature_room -= d * cooling_rate * self.env.step_size

    def heat_room(self):
        # 0.8 denotes heating power to thermal energy efficiency
        heating_efficiency = 0.8 / (self.heat_capacity)
        temperature_delta = self.current_power * \
            heating_efficiency * self.env.step_size
        self.temperature_room += temperature_delta

    def get_outside_temperature(self, offset_days=0):
        day = (time.gmtime(self.env.now).tm_yday + offset_days) % 365
        return outside_temperatures_2013[day]


class SimpleElectricalConsumer(BaseSystem):

    def __init__(self, env, power_meter):
        BaseSystem.__init__(self, env)
        self.power_meter = power_meter

        self.total_consumption = 0.0  # kWh

        # list of 24 values representing relative demand per hour
        self.demand_variation = [1 for i in range(24)]

    def step(self):
        consumption = self.get_consumption_energy()
        self.total_consumption += consumption
        self.power_meter.consume_energy(consumption)

    def get_consumption_power(self):
        time_tuple = time.gmtime(self.env.now)
        quarter = int(time_tuple.tm_min / 15.0)
        quarters = (time_tuple.tm_hour * 4 + quarter) % (4 * 24)
        # calculate variation using daily demand and variation
        return daily_electrical_demand[quarters] * self.demand_variation[time_tuple.tm_hour]

    def get_consumption_energy(self):
        return self.get_consumption_power() / self.env.steps_per_measurement
