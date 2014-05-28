from server.forecasting.forecasting.systems.storages as storages


class RealHeatStorage(storages.HeatStorage):

    def __init__(self, system_id, env, capacity=2500, min_temperature=55.0, target_temperature=70.0, critical_temperature=90.0):
        super(HeatStorage, self).__init__(system_id, env)

        # default data from pamiru48
        self.capacity = capacity  # liters
        self.base_temperature = 20.0  # assume no lower temperature
        self.min_temperature = min_temperature  # degree Celsius
        self.target_temperature = target_temperature  # degree Celsius
        self.critical_temperature = critical_temperature  # degree Celsius

        self.specific_heat_capacity = 4.19 / 3600.0  # kWh/(kg*K)

        self.input_energy = 0.0  # kWh
        self.output_energy = 0.0  # kWh
        self.empty_count = 0
        self.temperature_loss = 3.0 / 24.0  # loss per hour

    def add_energy(self, energy):
        raise NotImplementedError

    def consume_energy(self, energy):
        raise NotImplementedError

    def energy_stored(self):
        return self.input_energy - self.output_energy

    def get_target_energy(self):
        return self.specific_heat_capacity * self.capacity * (self.target_temperature - self.base_temperature)

    def get_require_energy(self):
        return self.get_target_energy() - self.energy_stored()

    def get_temperature(self):
        return self.base_temperature + self.energy_stored() / (self.capacity * self.specific_heat_capacity)

    def set_temperature(self, value):
        raise NotImplementedError

    def get_energy_capacity(self):
        return self.capacity * \
            (self.critical_temperature - self.base_temperature) * \
            self.specific_heat_capacity

    def undersupplied(self):
        return self.get_temperature() < self.min_temperature

    def start(self):
        raise NotImplementedError

    def stop(self):
        raise NotImplementedError

    def step(self):
        raise NotImplementedError

    def attach_to_cogeneration_unit(self, system):
        raise NotImplementedError

    def attach_to_peak_load_boiler(self, system):
        raise NotImplementedError

    def attach_to_thermal_consumer(self, system):
        raise NotImplementedError


class RealPowerMeter(storages.PowerMeter):

    def __init__(self, system_id, env, electrical_costs=0.283, feed_in_reward=0.0917):
        super(PowerMeter, self).__init__(system_id, env)

        self.fed_in_electricity = 0.0  # kWh
        self.purchased = 0  # kWh
        self.total_fed_in_electricity = 0.0  # kWh
        self.total_purchased = 0  # kWh

        self.energy_produced = 0.0  # kWh
        self.energy_consumed = 0.0  # kWh

        # costs in Euro to purchase 1 kW/h from external supplier
        self.electrical_costs = electrical_costs
        # reward in Euro for feed in 1 kW/h
        self.feed_in_reward = feed_in_reward

    def add_energy(self, energy):
        raise NotImplementedError

    def consume_energy(self, energy):
        raise NotImplementedError

    def get_reward(self):
        return self.total_fed_in_electricity * self.feed_in_reward

    def get_costs(self):
        return self.total_purchased * self.electrical_costs

    def step(self):
        raise NotImplementedError

    def attach_to_cogeneration_unit(self, system):
        raise NotImplementedError

    def attach_to_electrical_consumer(self, system):
        raise NotImplementedError
