from data import electrical_feed_in_reward_per_kwh, electrical_costs_per_kwh
from helpers import BaseSystem


class HeatStorage(BaseSystem):

    def __init__(self, env):
        BaseSystem.__init__(self, env)

        # data from pamiru48
        self.capacity = 25000 # liters  (=kilos)
        self.base_temperature = 20.0  # degree Celsius
        self.min_temperature = 55.0  # degree Celsius
        self.target_temperature = 70.0  # degree Celsius
        self.critical_temperature = 90.0  # degree Celsius

        self.specific_heat_capacity = 4.19 * 1 / 3600.0  # kWh/(kg*K)

        self.input_energy = 0.0  # kWh
        self.output_energy = 0.0  # kWh
        self.empty_count = 0
        self.temperature_loss = 3.0 / 24.0  # loss per hour

    def add_energy(self, energy):
        self.input_energy += energy

    def consume_energy(self, energy):
        if self.energy_stored() - energy >= 0:
            self.output_energy += energy
        else:
            self.empty_count += 1
            self.output_energy += self.energy_stored()

    def energy_stored(self):
        return self.input_energy - self.output_energy

    def get_target_energy(self):
        return self.specific_heat_capacity * self.capacity * (self.target_temperature - self.base_temperature)

    def get_require_energy(self):
        return self.get_target_energy() - self.energy_stored()

    def get_temperature(self):
        return self.base_temperature + self.energy_stored() / (self.capacity * self.specific_heat_capacity)

    def get_energy_capacity(self):
        return self.capacity * \
            (self.critical_temperature - self.base_temperature) * \
            self.specific_heat_capacity

    def undersupplied(self):
        return self.get_temperature() < self.min_temperature

    def start(self):
        self.running = True

    def stop(self):
        self.running = False

    def step(self):
        energy_loss = (self.capacity * self.specific_heat_capacity) * \
            self.temperature_loss #per hour
        self.output_energy += energy_loss * (self.env.step_size / 3600.0)


class PowerMeter(BaseSystem):

    def __init__(self, env):
        BaseSystem.__init__(self, env)

        self.total_fed_in_electricity = 0.0  # kWh
        self.total_purchased = 0  # kWh

        self.energy_produced = 0.0  # kWh
        self.energy_consumed = 0.0  # kWh
        self.current_power_consum = 0.0

    def add_energy(self, energy):
        self.energy_produced += energy

    def consume_energy(self, energy):
        self.energy_consumed += energy

    def get_reward(self):
        return self.total_fed_in_electricity * electrical_feed_in_reward_per_kwh

    def get_costs(self):
        return self.total_purchased * electrical_costs_per_kwh

    def step(self):
        balance = (self.energy_produced - self.energy_consumed)
        # purchase electrical energy if more energy needed than produced
        if balance < 0:
            self.total_purchased -= balance
        else:
            self.total_fed_in_electricity += balance
        self.energy_produced = 0
        self.energy_consumed = 0
        

