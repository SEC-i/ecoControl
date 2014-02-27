import math
import random
import datetime

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
        self.daily_demand = [18, 18, 19, 18, 19, 18, 19, 20, 21,
                             24, 24, 25, 24, 25, 25, 25, 26, 25, 25, 24, 23, 22, 21, 20]

        # data from pamiru48
        # has 12 apartments with 22 persons
        self.room_volume = 650  # m^3
        # assume 100W heating demand per m^2, rule of thumb for new housings
        self.max_power = self.room_volume * 100  # W
        self.current_power = 0
        # m^2, avg per room, avg rooms per appartments, appartments
        self.window_surface = 4 * 4 * 12

        specific_heat_capacity_brick = 1360 * 10 ** 3  # J/(m^3 * K)
        # J / K, approximation for 15m^2walls, 0.2m thickness, walls, ceiling,
        # acg rooms p appartent, appartments
        heat_cap_brick = specific_heat_capacity_brick * \
            (4 * 3 * 5 * 0.2) * 4 * 12

        #J /( m^3 * K)
        specific_heat_capacity_air = 1290

        self.heat_capacity = specific_heat_capacity_air * \
            self.room_volume + heat_cap_brick

    def step(self):
        self.simulate_consumption()
        consumption = self.get_consumption_energy()
        self.total_consumption += consumption
        self.heat_storage.consume_energy(consumption)

        self.env.log('Thermal demand:', '%f kW' % self.get_consumption_power())
        self.env.log('HS level:', '%f kWh' %
                     self.heat_storage.energy_stored())

    def get_consumption_power(self):
        return self.current_power / 1000.0

    def get_consumption_energy(self):
        return self.get_consumption_power() / self.env.steps_per_measurement

    def simulate_consumption(self):
        # calculate variation using daily demand
        self.target_temperature = self.daily_demand[self.env.get_hour_of_day()]

        self.heat_loss()

        # slow rise and fall of heating
        change_speed = 0.3
        slope = change_speed * \
            sign(self.target_temperature - self.temperature_room)
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
        day = (self.env.get_day_of_year() + offset_days) % 365
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

        self.env.log('Electrical demand:', '%f kW' %
                     self.get_consumption_power())
        self.env.log('Infeed Reward:', '%f Euro' %
                     self.power_meter.get_reward())

    def get_consumption_power(self):
        # calculate variation using daily demand and variation
        return self.get_electrical_demand() * self.demand_variation[self.env.get_hour_of_day()]

    def get_consumption_energy(self):
        return self.get_consumption_power() / self.env.steps_per_measurement

    def get_electrical_demand(self):
        hour = self.env.get_hour_of_day()
        quarter = int(self.env.get_min_of_hour() / 15.0)
        quarters = (hour * 4 + quarter) % (4 * 24)
        return daily_electrical_demand[quarters]
