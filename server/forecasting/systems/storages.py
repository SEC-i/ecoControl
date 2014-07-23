from server.systems.storages import HeatStorage, PowerMeter


class SimulatedHeatStorage(HeatStorage):
    """The simulation of a heat storage"""

    def __init__(self, system_id, env):
        super(SimulatedHeatStorage, self).__init__(system_id, env)

        self.input_energy = 0.0
        self.output_energy = 0.0
        #: count the steps when mimium temperature is undershot
        self.empty_count = 0
        #: termperature loss per hour by default 3 degress Celsius
        self.temperature_loss = 3.0 / 24.0

    def add_energy(self, energy):
        """Store energy in the heat storage.

        :param float energy: in kWh
        """
        self.input_energy += energy

    def consume_energy(self, energy):
        """Use energy from the heat storage

        :param float energy: in kWh
        """
        if self.energy_stored() - energy >= 0:
            self.output_energy += energy
        else:
            self.empty_count += 1
            self.output_energy += self.energy_stored()

    def energy_stored(self):
        """Currently available energy in kWh"""
        return self.input_energy - self.output_energy

    def get_target_energy(self):
        """Returns the overall energy needed for reaching the target temperature
        when the water is cold (base temperature)
        """
        return self.specific_heat_capacity * self.config['capacity'] * \
         (self.config['target_temperature'] - self.base_temperature)

    def get_require_energy(self):
        """Necessary energy in kWh to reach the target temperature."""
        return self.get_target_energy() - self.energy_stored()

    def get_temperature(self):
        """Returns the average temperature of the heat storage"""
        return self.base_temperature + self.energy_stored() / \
        (self.config['capacity'] * self.specific_heat_capacity)

    def set_temperature(self, temperature):
        """When the simulation is initialized to a real system the temperature of the real heat storage must be set"""
        self.output_energy = 0
        self.input_energy = (float(temperature) - self.base_temperature) * \
            (self.config['capacity'] * self.specific_heat_capacity)

    def get_energy_capacity(self):
        """Returns the maximal storable amount of energy in kWh"""
        temp_delta = self.config['critical_temperature'] - self.base_temperature
        return self.config['capacity'] * \
            temp_delta * self.specific_heat_capacity

    def undersupplied(self):
        """Returns `True` if the minimal temperature is undershot."""
        return self.get_temperature() < self.config['min_temperature']

    def step(self):
        """Loose some energy according to isolation"""
        hourly_energy_loss = (self.config['capacity'] * self.specific_heat_capacity) * \
            self.temperature_loss
        self.output_energy += hourly_energy_loss * \
            (self.env.step_size / 3600.0)


class SimulatedPowerMeter(PowerMeter):
    """The simulation of a power meter"""

    def __init__(self, system_id, env):
        super(SimulatedPowerMeter, self).__init__(system_id, env)

    def add_energy(self, energy):
        """Devices should use this method to supply electrical energy.

        :param float energy: in kWh
        """
        self.energy_produced += energy

    def consume_energy(self, energy):
        """Devices should use this method to consume electrical energy.

        :param float energy: in kWh
        """
        self.energy_consumed += energy

    def step(self):
        """Purchase electrical energy if more energy needed than produced.
        Otherwise the remaining energy is fed in."""
        balance = (self.energy_produced - self.energy_consumed)
        if balance < 0:
            self.purchased = -balance
            self.total_purchased -= balance
        else:
            self.fed_in_electricity = balance
            self.total_fed_in_electricity += balance
        self.energy_produced = 0
        self.energy_consumed = 0