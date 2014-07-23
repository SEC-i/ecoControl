from server.systems.producers import CogenerationUnit, PeakLoadBoiler


class SimulatedCogenerationUnit(CogenerationUnit):

    def __init__(self, system_id, env):

        super(SimulatedCogenerationUnit, self).__init__(system_id, env)

        self.off_time = self.env.now
        self.overwrite_workload = None
        # given efficiency is reached only on maximum workload
        # at minumum workload the efficiency is decreased by
        # max_efficiency_loss
        self.max_efficiency_loss = 0.15  # %

    def step(self):
        if self.running:
            presumable_workload = self.calculate_new_workload()
            self.set_workload(presumable_workload)
            self.consume_and_produce_energy()
            self.power_meter.add_energy(self.get_electrical_energy_production())
            self.heat_storage.add_energy(self.get_thermal_energy_production())
        else:
            self.workload = 0.0

    def calculate_new_workload(self):
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
        return self.current_electrical_production * (self.env.step_size / 3600.0)

    def get_thermal_energy_production(self):
        return self.current_thermal_production * (self.env.step_size / 3600.0)

    def get_efficiency_loss_factor(self):
        if self.workload == self.config['minimal_workload']:
            return 1.0 - self.max_efficiency_loss
        relative_workload = (self.workload - self.config['minimal_workload']) \
            / (1.0 - self.config['minimal_workload'])
        return 1.0 - self.max_efficiency_loss * (1.0 - relative_workload)

    def get_calculated_workload_thermal(self):
        max_thermal_power = self.config['thermal_efficiency'] * self.config['max_gas_input']
        min_thermal_power = max_thermal_power * self.config['minimal_workload'] \
                    * (1.0 - self.max_efficiency_loss)
        demand = self.heat_storage.get_require_energy()
        relative_demand = max(demand, min_thermal_power) / max_thermal_power
        return min(relative_demand, 1.0)

    def get_calculated_workload_electric(self):
        if self.heat_storage.get_temperature() >= self.heat_storage.target_temperature:
            return 0.0
        max_electric_power = self.config['electrical_efficiency'] * self.config['max_gas_input']
        min_electric_power = max_electric_power * self.config['minimal_workload'] \
                    * (1.0 - self.max_efficiency_loss)
        demand = self.power_meter.current_power_consum
        relative_demand = max(demand, min_electric_power) / max_electric_power
        return min(relative_demand, 1.0)

    def set_workload(self, calculated_workload):
        """Sets new workload, detects power-ons and tracks operating time"""
        old_workload = self.workload

        # make sure that config['minimal_workload'] <= workload <= 99.0 or workload = 0
        if calculated_workload >= self.config['minimal_workload']:
            # detect if power has been turned on
            if old_workload == 0:
                self.power_on_count += 1

            self.total_hours_of_operation += self.env.step_size / 3600.0
            # check range because of external overwrite_workload
            self.workload = max(min(calculated_workload, 1.0), 0.0)
        else:
            self.workload = 0.0
            if self.off_time <= self.env.now:
                self.off_time = self.env.now + self.config['minimal_off_time']

    def consume_and_produce_energy(self):
        # calulate current consumption and production values
        self.current_gas_consumption = self.workload * self.config['max_gas_input']
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

    def __init__(self, system_id, env):
        super(SimulatedPeakLoadBoiler, self).__init__(system_id, env)

        self.off_time = self.env.now
        self.overwrite_workload = None

    def step(self):
        if self.running:
            self.calculate_workload()
            self.consume_and_produce_energy()
            self.heat_storage.add_energy(self.get_thermal_energy_production())
        else:
            self.workload = 0.0

    def calculate_workload(self):
        if self.overwrite_workload is not None:
            self.workload = float(self.overwrite_workload)
            self.total_hours_of_operation += self.env.step_size / 3600.0
        else:
            # turn on if heat_storage is undersupplied
            if self.heat_storage.undersupplied() and self.off_time <= self.env.now:
                if self.workload == 0.0:
                    self.power_on_count += 1

                self.total_hours_of_operation += self.env.step_size / 3600.0
                self.workload = 1.0
            # turn off if heat storage's target energy is almost reached
            elif self.current_thermal_production >= self.heat_storage.get_require_energy():
                self.workload = 0.0

                if self.off_time <= self.env.now:
                    self.off_time = self.env.now + 3 * 60.0  # 3 min

    def consume_and_produce_energy(self):
        # calulate current consumption and production values
        self.current_gas_consumption = self.workload * self.config['max_gas_input']
        self.current_thermal_production = self.current_gas_consumption * \
                self.config['thermal_efficiency']

        self.total_gas_consumption += self.current_gas_consumption * \
            (self.env.step_size / 3600.0)
        self.total_thermal_production += self.current_thermal_production * \
            (self.env.step_size / 3600.0)

    def get_thermal_energy_production(self):
        return self.current_thermal_production * (self.env.step_size / 3600.0)