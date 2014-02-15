import random

from helpers import log

gas_price_per_kwh = 0.0655


class PowerGenerator(object):

    def __init__(self, env):
        self.env = env
        self.running = False

    def start(self):
        self.running = True

    def stop(self):
        self.running = False


class BHKW(PowerGenerator):

    def __init__(self, env, heat_storage):
        PowerGenerator.__init__(self, env)
        # XRGI 15kW
        self.max_gas_input = 49.0  # kW
        self.electrical_efficiency = 0.3  # max 14.7 kW
        self.thermal_efficiency = 0.62  # max 30.38 kW
        self.maintenance_interval = 8500  # hours

        self.heat_storage = heat_storage

        self.minimal_workload = 40.0
        self.noise = True

        self.total_gas_consumption = 0.0  # kWh
        self.total_electrical_production = 0.0  # kWh
        self.total_thermal_production = 0.0  # kWh

    def get_workload(self):
        if self.running:
            calculated_workload = self.heat_storage.target_energy + \
                self.minimal_workload - self.heat_storage.energy_stored()
                
            if self.noise:
                calculated_workload += random.random() - 0.5

            if calculated_workload >= self.minimal_workload:
                return min(calculated_workload, 99.0)
        return 0.0

    def get_gas_consumption(self, consider_consumed=False):
        current_gas_demand = self.get_workload() / 99.0 * self.max_gas_input
        if consider_consumed:
            self.total_gas_consumption += current_gas_demand
        return current_gas_demand

    def get_electrical_power(self, consider_consumed=False):
        current_electrical_production = self.get_gas_consumption(
            consider_consumed) * self.electrical_efficiency
        if consider_consumed:
            self.total_electrical_production += current_electrical_production
        return current_electrical_production

    def get_thermal_power(self, consider_consumed=False):
        current_thermal_production = self.get_gas_consumption(
            consider_consumed) * self.thermal_efficiency
        if consider_consumed:
            self.total_thermal_production += current_thermal_production
        return current_thermal_production

    def update(self):
        log(self.env, 'Starting BHKW...')
        self.start()
        while True:
            if self.running:
                log(self.env, 'BHKW workload:', '%f %%' % self.get_workload(), 'Total:', '%f kWh (%f Euro)' %
                    (self.total_gas_consumption, self.total_gas_consumption * gas_price_per_kwh))
                if self.get_workload() > 0:
                    self.heat_storage.add_energy(self.get_thermal_power(True))
            else:
                log(self.env, 'BHKW stopped.')
            yield self.env.timeout(3600)


class PeakLoadBoiler(PowerGenerator):

    def __init__(self, env, heat_storage):
        PowerGenerator.__init__(self, env)
        self.max_gas_input = 100.0  # kW
        self.thermal_efficiency = 0.8

        self.heat_storage = heat_storage

        self.producing = False
        self.total_gas_consumption = 0.0  # kWh
        self.total_thermal_production = 0.0  # kWh

    def analyze_demand(self):
        if self.heat_storage.undersupplied():
            self.producing = True
        elif self.heat_storage.energy_stored() + self.get_thermal_power() >= self.heat_storage.target_energy:
            self.producing = False

    def get_workload(self):
        if self.running and self.producing:
            return 99.0
        return 0.0

    def get_gas_consumption(self, consider_consumed=False):
        current_gas_demand = self.get_workload() / 99.0 * self.max_gas_input
        if consider_consumed:
            self.total_gas_consumption += current_gas_demand
        return current_gas_demand

    def get_thermal_power(self, consider_consumed=False):
        current_thermal_production = self.get_gas_consumption(
            consider_consumed) * self.thermal_efficiency
        if consider_consumed:
            self.total_thermal_production += current_thermal_production
        return current_thermal_production

    def update(self):
        log(self.env, 'Starting PLB...')
        self.start()
        while True:
            self.analyze_demand()
            if self.running:
                log(self.env, 'PLB workload:', '%f %%' % self.get_workload(), 'Total:', '%f kWh (%f Euro)' %
                   (self.total_gas_consumption, self.total_gas_consumption * gas_price_per_kwh))
                if self.get_workload() > 0:
                    self.heat_storage.add_energy(self.get_thermal_power(True))
            else:
                log(self.env, 'PLB stopped.')

            log(self.env, '=' * 80)
            yield self.env.timeout(3600)
