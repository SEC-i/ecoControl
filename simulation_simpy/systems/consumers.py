import math
import random


class SimpleThermalConsumer():

    def __init__(self, env, heat_storage):
        self.env = env
        self.heat_storage = heat_storage

        self.base_demand = 20.0  # kW
        self.varying_demand = 25.0  # kW
        self.noise = False

        self.total_consumption = 0.0  # kWh

        # list of 24 values representing relative demand per hour
        self.daily_demand = [50 / 350.0, 25 / 350.0, 10 / 350.0, 10 / 350.0, 5 / 350.0, 20 / 350.0, 250 / 350.0, 1, 320 / 350.0, 290 / 350.0, 280 / 350.0, 310 /
                             350.0, 250 / 350.0, 230 / 350.0, 225 / 350.0, 160 / 350.0, 125 / 350.0, 160 / 350.0, 200 / 350.0, 220 / 350.0, 260 / 350.0, 130 / 350.0, 140 / 350.0, 120 / 350.0]

    def get_consumption(self, consider_consumed=False):
        time_of_day = (self.env.now % (3600 * 24)) / 3600
        # calculate variation using daily demand
        variation = self.daily_demand[time_of_day] * self.varying_demand
        current_consumption = self.base_demand + variation

        if self.noise:
            current_consumption += self.varying_demand / 4.0 * \
                (random.random() - 0.5)

        if consider_consumed:
            self.total_consumption += current_consumption

        return current_consumption

    def update(self):
        while True:
            consumption = self.get_consumption()
            self.heat_storage.consume_energy(consumption)

            self.env.log('Thermal demand:', '%f kW' % consumption)
            self.env.log('HS level:', '%f kWh' %
                         self.heat_storage.energy_stored())

            yield self.env.timeout(3600)


class ThermalConsumer():

    """ physically based heating, using formulas from 
    http://www.model.in.tum.de/um/research/groups/ai/fki-berichte/postscript/fki-227-98.pdf and
    http://www.inference.phy.cam.ac.uk/is/papers/DanThermalModellingBuildings.pdf """

    def __init__(self, env, heat_storage):
        self.env = env
        self.heat_storage = heat_storage

        self.name = "Heating"

        self.target_temperature = 25
        self.total_consumption = 0
        self.temperature_room = 20
        self.temperature_outside = 1

        # list of 24 values representing relative target_temperature per hour
        self.daily_demand = [50 / 350.0, 25 / 350.0, 10 / 350.0, 10 / 350.0, 5 / 350.0, 20 / 350.0, 250 / 350.0, 1, 320 / 350.0, 290 / 350.0, 280 / 350.0, 310 /
                             350.0, 250 / 350.0, 230 / 350.0, 225 / 350.0, 160 / 350.0, 125 / 350.0, 160 / 350.0, 200 / 350.0, 220 / 350.0, 260 / 350.0, 130 / 350.0, 140 / 350.0, 120 / 350.0]


        # let's use 30 heating systems
        amount_of_heating_systems = 30

        # Type 22, 1.4m X 0.5m
        # W/m to 22 C = 90 W
        # room: 3x5x3m
        self.room_volume = 3 * 5 * 3 * amount_of_heating_systems
        self.max_power = 4000 * amount_of_heating_systems  # W
        self.current_power = 0
        self.window_surface = 5 * amount_of_heating_systems  # m^2

        specific_heat_capacity_brick = 1360 * 10 ** 2  # J/(m^3 * K)
        # J / K, approximation for 15m^2walls, 0.2m thickness, walls, ceiling,
        heat_cap_brick = specific_heat_capacity_brick * (4 * 3 * 5 * 0.2)

        #J /( m^3 * K)
        specific_heat_capacity_air = 1290

        self.heat_capacity = specific_heat_capacity_air * \
            self.room_volume + heat_cap_brick

    def get_consumption(self):
        time_of_day = (self.env.now % (3600 * 24)) / 3600
        # calculate variation using daily demand
        self.target_temperature = self.daily_demand[time_of_day] 


        self.heat_loss(self.env.step_size)

        # slow rise and  fall of heating
        change_speed = 1
        slope = change_speed * \
            sign(self.target_temperature - self.temperature_room)
        power_delta = slope * self.env.step_size

        self.current_power += power_delta
        # clamp to maximum power
        self.current_power = max(min(self.current_power, self.max_power), 0)
        self.heat_room(time_delta)
        return self.current_power

    def update(self):
        while True:
            consumption_kW = self.get_consumption() / 1000.0
            self.heat_storage.consume_energy(consumption_kW)

            self.env.log('Thermal demand:', '%f kW' % consumption)
            self.env.log('HS level:', '%f kWh' %
                         self.heat_storage.energy_stored())

            yield self.env.timeout(3600)

    def heat_loss(self):
        # assume cooling of power/2
        d = self.temperature_room - \
            self.temperature_outside
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


def sign(x):
    return 1 if x >= 0 else -1


class SimpleElectricalConsumer():

    def __init__(self, env, electrical_infeed):
        self.env = env
        self.electrical_infeed = electrical_infeed

        self.base_demand = 5.0  # kW
        self.varying_demand = 7.5  # kW
        self.noise = False

        self.total_consumption = 0.0  # kWh

        # list of 24 values representing relative demand per hour
        self.daily_demand = [50 / 350.0, 25 / 350.0, 10 / 350.0, 10 / 350.0, 5 / 350.0, 20 / 350.0, 250 / 350.0, 1, 320 / 350.0, 290 / 350.0, 280 / 350.0, 310 /
                             350.0, 250 / 350.0, 230 / 350.0, 225 / 350.0, 160 / 350.0, 125 / 350.0, 160 / 350.0, 200 / 350.0, 220 / 350.0, 260 / 350.0, 130 / 350.0, 140 / 350.0, 120 / 350.0]

    def get_consumption(self, consider_consumed=False):
        time_of_day = (self.env.now % (3600 * 24)) / 3600
        # calculate variation using daily demand
        variation = self.daily_demand[time_of_day] * self.varying_demand
        current_consumption = self.base_demand + variation

        if self.noise:
            current_consumption += self.varying_demand / 4.0 * \
                (random.random() - 0.5)

        if consider_consumed:
            self.total_consumption += current_consumption

        return current_consumption

    def update(self):
        while True:
            consumption = self.get_consumption()
            self.electrical_infeed.consume_energy(consumption)

            self.env.log('Electrical demand:', '%f kW' % consumption)
            self.env.log('Infeed Reward:', '%f Euro' %
                         self.electrical_infeed.get_reward())

            yield self.env.timeout(3600)
