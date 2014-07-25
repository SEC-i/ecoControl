from server.devices.base import BaseDevice


class HeatStorage(BaseDevice):

    def __init__(self, device_id, env):
        super(HeatStorage, self).__init__(device_id, env)
        # default data from pamiru48
        self.config = {
            'capacity': 2500,  # liters
            'base_temperature': 20.0,  # assume no lower temperature
            'min_temperature': 55.0,  # degree Celsius
            'target_temperature': 85.0,  # degree Celsius
            'critical_temperature': 90.0,  # degree Celsius
            'specific_heat_capacity': 4.19 / 3600.0  # kWh/(kg*K)
        }


    def attach_to_cogeneration_unit(self, device):
        device.heat_storage = self

    def attach_to_peak_load_boiler(self, device):
        device.heat_storage = self

    def attach_to_thermal_consumer(self, device):
        device.heat_storage = self

    def energy_stored(self):
        return self.input_energy - self.output_energy

    def get_target_energy(self):
        return self.config['specific_heat_capacity'] * self.config['capacity'] * (self.config['target_temperature'] - self.config['base_temperature'])

    def get_require_energy(self):
        return self.get_target_energy() - self.energy_stored()

    def get_temperature(self):
        return self.config['base_temperature'] + self.energy_stored() / (self.config['capacity'] * self.config['specific_heat_capacity'])

    def get_energy_capacity(self):
        return self.config['capacity'] * \
            (self.critical_temperature - self.config['base_temperature']) * \
            self.config['specific_heat_capacity']

    def undersupplied(self):
        return self.get_temperature() < self.config['min_temperature']


class PowerMeter(BaseDevice):

    def __init__(self, device_id, env):
        super(PowerMeter, self).__init__(device_id, env)

        self.fed_in_electricity = 0.0  # kWh
        self.purchased = 0  # kWh
        self.total_fed_in_electricity = 0.0  # kWh
        self.total_purchased = 0  # kWh

        self.energy_produced = 0.0  # kWh
        self.energy_consumed = 0.0  # kWh

        # costs in Euro to purchase 1 kW/h from external supplier
        self.electrical_costs = 0.283
        # reward in Euro for feed in 1 kW/h
        self.feed_in_reward = 0.0917

    def attach_to_cogeneration_unit(self, device):
        device.power_meter = self

    def attach_to_electrical_consumer(self, device):
        device.power_meter = self

    def get_reward(self):
        return self.total_fed_in_electricity * self.feed_in_reward

    def get_costs(self):
        return self.total_purchased * self.electrical_costs
