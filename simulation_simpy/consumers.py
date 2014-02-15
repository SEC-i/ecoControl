import math
import random

from helpers import log


class ThermalConsumer():

    def __init__(self, env, heat_storage):
        self.env = env
        self.heat_storage = heat_storage

        self.average_demand = 20.0  # kW
        self.varying_demand = 10.0  # kW
        self.noise = True

        self.total_consumption = 0.0  # kWh

    def get_consumption(self, consider_consumed=False):
        time_of_day = (self.env.now % (60.0 * 60 * 24)) / (60.0 * 60 * 24)
        # calculate variation using sine function
        variation = self.varying_demand * \
            math.fabs(math.sin(time_of_day * math.pi))
        current_consumption = self.average_demand + variation

        if self.noise:
            current_consumption += self.varying_demand * (random.random() - 0.5)

        if consider_consumed:
            self.total_consumption += current_consumption
        return current_consumption

    def update(self):
        while True:
            consumption = self.get_consumption()
            self.heat_storage.consume_energy(consumption)
            log(self.env, 'Thermal demand:', '%f kW' % consumption)
            log(self.env, 'HS energy stored:', '%f kWh' %
                self.heat_storage.energy_stored())
            yield self.env.timeout(3600)
