from server.systems.base import BaseSystem


class HeatStorage(BaseSystem):

    def __init__(self, system_id, env):
        super(HeatStorage, self).__init__(system_id, env)
        self.config = {
            'capacity': 2500,
            'min_temperature': 55.0,  # degree Celsius
            'target_temperature': 85.0,  # degree Celsius
            'critical_temperature': 90.0,  # degree Celsius
        }

        #: specific heat capacity of water in kWh/(kg*K)
        self.specific_heat_capacity = 4.19 / 3600.0
        self.base_temperature = 20.0 #: assume no lower temperature


    def attach_to_cogeneration_unit(self, system):
        system.heat_storage = self

    def attach_to_peak_load_boiler(self, system):
        system.heat_storage = self

    def attach_to_thermal_consumer(self, system):
        system.heat_storage = self

    def get_temperature(self):
        raise NotImplementedError

    def undersupplied(self):
        raise NotImplementedError


class PowerMeter(BaseSystem):

    def __init__(self, system_id, env):
        super(PowerMeter, self).__init__(system_id, env)

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

    def attach_to_cogeneration_unit(self, system):
        system.power_meter = self

    def attach_to_electrical_consumer(self, system):
        system.power_meter = self

    def add_energy(self, energy):
        raise NotImplementedError

    def consume_energy(self, energy):
        raise NotImplementedError

    def get_reward(self):
        return self.total_fed_in_electricity * self.feed_in_reward

    def get_costs(self):
        return self.total_purchased * self.electrical_costs