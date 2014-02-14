from helpers import log


class HeatStorage():

    def __init__(self, env):
        self.env = env
        self.capacity = 700.0  # kWh
        self.target_energy = 500.0  # kWh
        
        self.input_energy = 0.0  # kWh
        self.output_energy = 0.0  # kWh

        self.undersupplied_threshold = self.target_energy / 2

    def energy_stored(self):
        return self.input_energy - self.output_energy

    def level(self):
        return self.energy_stored()/self.capacity * 99.0

    def add_energy(self, energy):
        if self.energy_stored() + energy <= self.capacity:
            self.input_energy += energy

    def consume_energy(self, energy):
        if self.energy_stored() - energy >= 0:
            self.output_energy += energy
        else:
            log(self.env, 'Heat Storage empty')

    def undersupplied(self):
        return self.energy_stored() < self.undersupplied_threshold
