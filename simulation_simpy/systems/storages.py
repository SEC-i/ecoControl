class HeatStorage():

    def __init__(self, env):
        self.env = env

        self.capacity = 700.0 * 10  # kilos ~ liters
        self.base_temperature = 20.0  # degree Celsius
        self.min_temperature = 70.0  # degree Celsius
        self.max_temperature = 78.0  # degree Celsius

        self.specific_heat_capacity = 4.19 * 1 / 3600.0  # kWh/(kg*K)

        self.input_energy = 0.0  # kWh
        self.output_energy = 0.0  # kWh
        self.empty_count = 0

    def energy_stored(self):
        return self.input_energy - self.output_energy

    def get_target_energy(self):
        return self.specific_heat_capacity * self.capacity * (self.max_temperature - self.base_temperature)

    def add_energy(self, energy):
        energy /= self.env.accuracy
        if self.energy_stored() + energy <= self.capacity:
            self.input_energy += energy

    def consume_energy(self, energy):
        energy /= self.env.accuracy
        if self.energy_stored() - energy >= 0:
            self.output_energy += energy
        else:
            self.empty_count += 1
            self.env.log('Heat Storage empty')

    def get_temperature(self):
        return self.base_temperature + self.energy_stored() / (self.capacity * self.specific_heat_capacity)

    def undersupplied(self):
        return self.get_temperature() < self.min_temperature


class ElectricalInfeed():

    def __init__(self, env):
        self.env = env
        self.electrical_reward_per_kwh = 0.0541  # Euro
        self.electrical_costs_per_kwh = 0.264  # Euro

        self.total = 0.0  # kWh
        self.total_purchased = 0  # kWh

        self.energy_produced = 0.0  # kWh

    def add_energy(self, energy):
        energy /= self.env.accuracy
        self.energy_produced = energy

    def consume_energy(self, energy):
        energy /= self.env.accuracy

        balance = self.energy_produced - energy
        # purchase electrical energy if more energy needed than produced
        if balance < 0:
            self.total_purchased -= balance
        else:
            self.total += balance
        self.energy_produced = 0

    def get_reward(self):
        return self.total * self.electrical_reward_per_kwh

    def get_costs(self):
        return self.total_purchased * self.electrical_costs_per_kwh