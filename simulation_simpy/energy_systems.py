import random


class BHKW():

    def __init__(self, heat_storage):
        # XRGI 15kW
        self.max_gas_input = 49.0  # kW
        self.electrical_efficiency = 0.3  # max 14.7 kW
        self.thermal_efficiency = 0.62  # max 30.38 kW
        self.maintenance_interval = 8500  # hours

        self.heat_storage = heat_storage

        self.minimal_workload = 40.0
        self.running = False
        self.total_gas_consumption = 0.0 # kWh

    def producing(self):
        return self.get_workload() >= self.minimal_workload

    def start(self):
        self.running = True

    def stop(self):
        self.running = False

    def get_workload(self):
        if self.running:
            calculated_workload = self.heat_storage.target_level + self.minimal_workload - self.heat_storage.level()
            # add noise
            calculated_workload += random.random() - 0.5
            if calculated_workload >= self.minimal_workload:
                return min(calculated_workload, 99.0)
        return 0.0

    def get_gas_consumption(self, consider_consumed = False):
        current_gas_demand = self.get_workload() / 99.0 * self.max_gas_input
        if consider_consumed:
            self.total_gas_consumption += current_gas_demand
        return current_gas_demand

    def get_electrical_power(self, consider_consumed = False):
        return self.get_gas_consumption(consider_consumed) * self.electrical_efficiency

    def get_thermal_power(self, consider_consumed = False):
        return self.get_gas_consumption(consider_consumed) * self.thermal_efficiency


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


class PeakLoadBoiler():

    def __init__(self, heat_storage):
        self.max_gas_input = 100.0  # kW
        self.thermal_efficiency = 0.8

        self.heat_storage = heat_storage

        self.running = False
        self.producing = False
        self.total_gas_consumption = 0.0 # kWh

    def start(self):
        self.running = True

    def stop(self):
        self.running = False

    def analyze_demand(self):
        if self.heat_storage.undersupplied():
            self.producing = True
        elif self.heat_storage.level() + self.get_thermal_power() >= self.heat_storage.target_level:
            self.producing = False

    def get_workload(self):
        if self.running and self.producing:
            return 99.0
        return 0.0

    def get_gas_consumption(self, consider_consumed = False):
        current_gas_demand = self.get_workload() / 99.0 * self.max_gas_input
        if consider_consumed:
            self.total_gas_consumption += current_gas_demand
        return current_gas_demand

    def get_thermal_power(self, consider_consumed = False):
        return self.get_gas_consumption(consider_consumed) * self.thermal_efficiency
