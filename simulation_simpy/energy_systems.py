import random

class BHKW():

    def __init__(self, heat_storage):
        # XRGI 15kW
        self.max_gas_input = 49.0  # kW
        self.electrical_efficiency = 0.3
        self.thermal_efficiency = 0.62
        self.maintenance_interval = 8500  # hours

        self.heat_storage = heat_storage

        self.minimal_workload = 40.0

    def producing(self):
        return self.get_workload() >= self.minimal_workload

    def start(self):
        self.running = True

    def stop(self):
        self.running = False

    def get_workload(self):
        if(self.running):
            calculated_workload = 99.0 * (self.heat_storage.target_level - self.heat_storage.level()) / self.heat_storage.target_level
            # add noise
            calculated_workload += random.random() - 0.5
            if(calculated_workload >= self.minimal_workload):
                return min(calculated_workload, 99.0)
            else:
                return 0.0
        else:
            return 0.0

    def get_gas_consumption(self):
        return self.get_workload() / 99.0 * self.max_gas_input

    def get_electrical_power(self):
        return self.get_gas_consumption() * self.electrical_efficiency

    def get_thermal_power(self):
        return self.get_gas_consumption() * self.thermal_efficiency


class HeatStorage():

    def __init__(self):
        self.capacity = 100.0  # kW
        self.target_level = 80.0  # kW
        self.input_energy = 0.0  # kW
        self.output_energy = 0.0  # kW

    def level(self):
        return self.input_energy - self.output_energy

    def add_energy(self, energy):
        if(self.level() + energy <= self.capacity):
            self.input_energy += energy
        else:
            print('Heat Storage overloaded')

    def consume_energy(self, energy):
        if(self.level() - energy >= 0):
            self.output_energy += energy
        else:
            print('Heat Storage empty')
