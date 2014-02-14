import math

from helpers import log


class ThermalConsumer():

    def __init__(self, env, heat_storage):
        self.env = env
        self.heat_storage = heat_storage

        self.average_demand = 20.0  # kW
        self.varying_demand = 10.0  # kW

        self.total_consumption = 0.0  # kWh

    def get_consumption(self, consider_consumed=False):
        # calculate variation using sine function
        variation = self.varying_demand * \
            math.fabs(math.sin((self.env.now % 100.0) / 100.0 * 2 * math.pi))
        
        current_consumption = self.average_demand + variation
        if consider_consumed:
            self.total_consumption += current_consumption
        return current_consumption

    def update(self):
        while True:
            consumption = self.get_consumption()
            self.heat_storage.consume_energy(consumption)
            log(self.env, 'Thermal demand:', '%f kW' % consumption)
            log(self.env, 'HS energy stored:', '%f kWh' % self.heat_storage.energy_stored())
            yield self.env.timeout(1)
