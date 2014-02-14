import random
import math


class PowerGenerator(object):

    def __init__(self):
        self.running = False

    def start(self):
        self.running = True

    def stop(self):
        self.running = False

    def get_workload(self):
        pass


class BHKW(PowerGenerator):

    def __init__(self, heat_storage):
        # XRGI 15kW
        self.max_gas_input = 49.0  # kW
        self.electrical_efficiency = 0.3  # max 14.7 kW
        self.thermal_efficiency = 0.62  # max 30.38 kW
        self.maintenance_interval = 8500  # hours

        self.heat_storage = heat_storage

        self.minimal_workload = 40.0
        self.total_gas_consumption = 0.0  # kWh
        self.total_electrical_production = 0.0  # kWh
        self.total_thermal_production = 0.0  # kWh

    def get_workload(self):
        if self.running:
            calculated_workload = self.heat_storage.target_level + \
                self.minimal_workload - self.heat_storage.level()
            # add noise
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


class PeakLoadBoiler(PowerGenerator):

    def __init__(self, heat_storage):
        self.max_gas_input = 100.0  # kW
        self.thermal_efficiency = 0.8

        self.heat_storage = heat_storage

        self.producing = False
        self.total_gas_consumption = 0.0  # kWh
        self.total_thermal_production = 0.0  # kWh

    def analyze_demand(self):
        if self.heat_storage.undersupplied():
            self.producing = True
        elif self.heat_storage.level() + self.get_thermal_power() >= self.heat_storage.target_level:
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


class HeatStorage():

    def __init__(self):
        self.capacity = 700.0  # kWh
        self.target_level = 500.0  # kWh
        self.input_energy = 0.0  # kWh
        self.output_energy = 0.0  # kWh

        self.undersupplied_threshold = self.target_level / 2

    def level(self):
        return self.input_energy - self.output_energy

    def add_energy(self, energy):
        if self.level() + energy <= self.capacity:
            self.input_energy += energy

    def consume_energy(self, energy):
        if self.level() - energy >= 0:
            self.output_energy += energy
        else:
            print('Heat Storage empty')

    def undersupplied(self):
        return self.level() < self.undersupplied_threshold


class ThermalConsumer():

    def __init__(self, env):
        self.env = env
        self.average_demand = 20.0  # kW
        self.varying_demand = 10.0  # kW

        self.total_consumption = 0.0 # kWh

    def get_consumption(self, consider_consumed=False):
        variation = self.varying_demand * \
            math.fabs(math.sin((self.env.now % 100.0) / 100.0 * 2 * math.pi))
        current_consumption = self.average_demand + variation
        if consider_consumed:
            self.total_consumption += current_consumption
        return current_consumption
