import math
import random


class ThermalConsumer():

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


class ElectricalConsumer():

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
