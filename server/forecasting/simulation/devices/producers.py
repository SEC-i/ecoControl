from server.devices.producers import CogenerationUnit, PeakLoadBoiler, SolarPowerUnit


class SimulatedCogenerationUnit(CogenerationUnit):
    """The simulation of a cogeneration unit"""

    def __init__(self, device_id, env):

        super(SimulatedCogenerationUnit, self).__init__(device_id, env)
        #: Saves the last powered off time to ensure minimal_off_time
        self.off_time = self.env.now
        #: Device can have fixed workload without internal control. Be aware of overheating!
        self.overwrite_workload = None
        """Efficiency is reached only on maximum workload
        at minumum workload the efficiency is decreased by 15 %"""
        self.max_efficiency_loss = 0.15

    def step(self):
        """Calculates new workload, produce and consume energy for the last time-step"""
        if self.running:
            presumable_workload = self.calculate_new_workload()
            self.set_workload(presumable_workload)
            self.consume_and_produce_energy()
            self.power_meter.add_energy(self.get_electrical_energy_production())
            self.heat_storage.add_energy(self.get_thermal_energy_production())
        else:
            self._workload = 0.0

    def calculate_new_workload(self):
        """Selects right operating mode for workload calculation"""
        if self.overwrite_workload is not None:
            calculated_workload = float(self.overwrite_workload)
        elif self.off_time > self.env.now:
            calculated_workload = 0.0
        elif self.thermal_driven:
            calculated_workload = self.get_calculated_workload_thermal()
        else:
            calculated_workload = self.get_calculated_workload_electric()
        return calculated_workload

    def get_electrical_energy_production(self):
        """Returns produced electrical energy in kWh during current time-step"""
        return self.current_electrical_production * (self.env.step_size / 3600.0)

    def get_thermal_energy_production(self):
        """Returns produced thermal energy in kWh during current time-step"""
        return self.current_thermal_production * (self.env.step_size / 3600.0)

    def get_efficiency_loss_factor(self):
        """Computes efficiency loss on modulation and returns left efficiency in percent [0,1]"""
        if self._workload == self.config['minimal_workload']:
            return 1.0 - self.max_efficiency_loss
        relative_workload = (self._workload - self.config['minimal_workload']) \
            / (1.0 - self.config['minimal_workload'])
        return 1.0 - self.max_efficiency_loss * (1.0 - relative_workload)

    def get_calculated_workload_thermal(self):
        """Returns workload for thermal driven mode"""
        max_thermal_power = self.config['thermal_efficiency'] * self.config['max_gas_input']
        min_thermal_power = max_thermal_power * self.config['minimal_workload'] \
                    * (1.0 - self.max_efficiency_loss)
        demand = self.heat_storage.get_required_energy()
        relative_demand = max(demand, min_thermal_power) / max_thermal_power
        return min(relative_demand, 1.0)

    def get_calculated_workload_electric(self):
        """Returns workload for electrical driven mode"""
        if self.heat_storage.get_temperature() >= self.heat_storage.target_temperature:
            return 0.0
        max_electric_power = self.config['electrical_efficiency'] * self.config['max_gas_input']
        min_electric_power = max_electric_power * self.config['minimal_workload'] \
                    * (1.0 - self.max_efficiency_loss)
        demand = self.power_meter.current_power_consum
        relative_demand = max(demand, min_electric_power) / max_electric_power
        return min(relative_demand, 1.0)

    def set_workload(self, calculated_workload):
        """Sets given workload, detects power-ons and tracks operating time

        :param float calculated_workload: new workload for the next time-step
        """
        old_workload = self._workload

        # make sure that config['minimal_workload'] <= workload <= 99.0 or workload = 0
        if calculated_workload >= self.config['minimal_workload']:
            # detect if power has been turned on
            if old_workload == 0:
                self.power_on_count += 1

            self.total_hours_of_operation += self.env.step_size / 3600.0
            # check range because of external overwrite_workload
            self._workload = max(min(calculated_workload, 1.0), 0.0)
        else:
            self._workload = 0.0
            if self.off_time <= self.env.now:
                self.off_time = self.env.now + self.config['minimal_off_time']

    def consume_and_produce_energy(self):
        """Updates currently consumed and produced energy"""
        self.current_gas_consumption = self._workload * self.config['max_gas_input']
        self.current_electrical_production = self.current_gas_consumption * \
            self.config['electrical_efficiency'] * self.get_efficiency_loss_factor()
        self.current_thermal_production = self.current_gas_consumption * \
            self.config['thermal_efficiency'] * self.get_efficiency_loss_factor()

        self.total_gas_consumption += self.current_gas_consumption * \
            (self.env.step_size / 3600.0)
        self.total_thermal_production += self.current_thermal_production * \
            (self.env.step_size / 3600.0)
        self.total_electrical_production += self.current_electrical_production * \
            (self.env.step_size / 3600.0)


class SimulatedPeakLoadBoiler(PeakLoadBoiler):
    """The simulation of a peak load boiler"""

    def __init__(self, device_id, env):
        super(SimulatedPeakLoadBoiler, self).__init__(device_id, env)

        #: Saves the last power off time to ensure 3 min off-time
        self.off_time = self.env.now
        #: Device can have fixed workload without internal control. Be aware of overheating!
        self.overwrite_workload = None

    def step(self):
        """Calculates new workload, produce and consume energy for the last time-step"""
        if self.running:
            self.calculate_workload()
            self.consume_and_produce_energy()
            self.heat_storage.add_energy(self.get_thermal_energy_production())
        else:
            self._workload = 0.0

    def calculate_workload(self):
        """Switches on when the heat storage is undersupplied and off if target temperature is reached.
        Also detects power-ons and tracks operating time."""
        if self.overwrite_workload is not None:
            self._workload = float(self.overwrite_workload)
            self.total_hours_of_operation += self.env.step_size / 3600.0
        else:
            # turn on if heat_storage is undersupplied
            if self.heat_storage.undersupplied() and self.off_time <= self.env.now:
                if self._workload == 0.0:
                    self.power_on_count += 1

                self.total_hours_of_operation += self.env.step_size / 3600.0
                self._workload = 1.0
            # turn off if heat storage's target energy is reached
            elif self.current_thermal_production >= self.heat_storage.get_required_energy():
                self._workload = 0.0

                if self.off_time <= self.env.now:
                    self.off_time = self.env.now + 3 * 60.0

    def consume_and_produce_energy(self):
        """Updates currently consumed and produced energy"""
        self.current_gas_consumption = self._workload * self.config['max_gas_input']
        self.current_thermal_production = self.current_gas_consumption * \
                self.config['thermal_efficiency']

        self.total_gas_consumption += self.current_gas_consumption * \
            (self.env.step_size / 3600.0)
        self.total_thermal_production += self.current_thermal_production * \
            (self.env.step_size / 3600.0)

    def get_thermal_energy_production(self):
        """Returns produced thermal energy in kWh during current time-step"""
        return self.current_thermal_production * (self.env.step_size / 3600.0)


class SimulatedSolarPowerUnit(SolarPowerUnit):

    def __init__(self, device_id, env):
        super(SimulatedSolarPowerUnit, self).__init__(device_id, env)


    def step(self):
        #convert sun hours to electrical power
        self.current_electrical_production = 1.23 #!: TODO
        self.total_electrical_production += self.current_electrical_production * \
            (self.env.step_size / 3600.0)
        self.power_meter.add_energy(self.get_electrical_energy_production())

    def get_electrical_energy_production(self):
        """Returns produced electrical energy in kWh during current time-step"""
        return self.current_electrical_production * (self.env.step_size / 3600.0)
