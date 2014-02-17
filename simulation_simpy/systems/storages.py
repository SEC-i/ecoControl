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
        return self.energy_stored() / self.capacity * 99.0

    def add_energy(self, energy):
        if self.energy_stored() + energy <= self.capacity:
            self.input_energy += energy

    def consume_energy(self, energy):
        if self.energy_stored() - energy >= 0:
            self.output_energy += energy
        else:
            self.env.log('Heat Storage empty')

    def undersupplied(self):
        return self.energy_stored() < self.undersupplied_threshold


class ElectricalInfeed():

    def __init__(self):
        self.electrical_reward_per_kwh = 0.0541  # Euro
        self.electrical_costs_per_kwh = 0.264  # Euro

        self.total = 0.0  # kWh
        self.total_purchased = 0  # kWh

        self.energy_produced = 0.0  # kWh

    def add_energy(self, energy):
        self.energy_produced = energy

    def consume_energy(self, energy):
        balance = self.energy_produced - energy
        # purchase external electrical energy if more energy needed than
        # produced
        if balance < 0:
            self.total_purchased -= balance
        else:
            self.total += balance
        self.energy_produced = 0

    def get_reward(self):
        return self.total * self.electrical_reward_per_kwh

    def get_costs(self):
        return self.total_purchased * self.electrical_costs_per_kwh
