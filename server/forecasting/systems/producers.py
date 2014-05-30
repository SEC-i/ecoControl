from server.systems.producers import CogenerationUnit, PeakLoadBoiler


class SimulatedCogenerationUnit(CogenerationUnit):

    def __init__(self, system_id, env):

        super(SimulatedCogenerationUnit, self).__init__(system_id)
        self.env = env

        self.off_time = self.env.now

        self.workload = 0
        self.current_gas_consumption = 0.0  # kW
        self.current_thermal_production = 0.0  # kWh
        self.total_gas_consumption = 0  # kWh
        self.total_thermal_production = 0.0  # kWh

        self.total_hours_of_operation = 0
        self.power_on_count = 0

        self.power_meter = None

        self.current_electrical_production = 0.0  # kW
        self.total_electrical_production = 0.0  # kWh
        self.electrical_driven_minimal_production = 1.0  # kWh (electrical)

        self.overwrite_workload = None

    def step(self):
        if self.running:
            presumable_workload = self.calculate_new_workload()
            self.update_parameters(presumable_workload)
            self.power_meter.add_energy(
                self.get_electrical_energy_production())
            self.heat_storage.add_energy(self.get_thermal_energy_production())
            self.consume_gas()
        else:
            self.workload = 0.0

    def calculate_new_workload(self):
        if self.overwrite_workload is not None:
            calculated_workload = self.overwrite_workload
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

    def get_operating_costs(self):
        gas_costs = self.total_gas_consumption * self.gas_costs
        maintenance_costs = self.total_electrical_production * \
            0.05  # 5 ct maintenance costs
        return maintenance_costs + gas_costs

    def get_efficiency_loss_factor(self):
        # given efficiency is reached only on maximum workload
        # at minumum workload the efficiency is decreased with
        # max_efficiency_loss
        relative_loss = 1.0 - (self.workload - self.minimal_workload) \
            / (99.0 - self.minimal_workload)
        return 1.0 - self.max_efficiency_loss / 100.0 * relative_loss

    def get_calculated_workload_thermal(self):
        max_thermal_power = self.thermal_efficiency / \
            100.0 * self.max_gas_input
        min_thermal_power = max_thermal_power * (self.minimal_workload / 100.0)
        calculated_power = self.heat_storage.get_require_energy()
        return min(calculated_power / max_thermal_power, 1) * 99.0

    def get_calculated_workload_electric(self):
        if self.heat_storage.get_temperature() >= \
            self.heat_storage.target_temperature:
            return 0.0
        max_electric_power = self.electrical_efficiency / \
            100.0 * self.max_gas_input
        return min(max(self.power_meter.current_power_consum,
                       self.electrical_driven_minimal_production)
                   / max_electric_power, 1) * 99.0

    def update_parameters(self, calculated_workload):
        old_workload = self.workload

        # make sure that minimal_workload <= workload <= 99.0 or workload =
        # 0
        if calculated_workload >= self.minimal_workload:
            # detect if power has been turned on
            if old_workload == 0:
                self.power_on_count += 1

            self.total_hours_of_operation += self.env.step_size / 3600.0
            self.workload = min(calculated_workload, 99.0)
        else:
            self.workload = 0.0
            if self.off_time <= self.env.now:
                self.off_time = self.env.now + self.minimal_off_time

        # calulate current consumption and production values
        self.current_gas_consumption = self.workload / \
            99.0 * self.max_gas_input

        self.current_electrical_production = self.current_gas_consumption * \
            self.electrical_efficiency / 100.0 * \
            self.get_efficiency_loss_factor()
        self.current_thermal_production = self.current_gas_consumption * \
            self.thermal_efficiency / 100.0 * self.get_efficiency_loss_factor()

    def consume_gas(self):
        self.total_gas_consumption += self.current_gas_consumption * \
            (self.env.step_size / 3600.0)
        self.total_thermal_production += self.current_thermal_production * \
            (self.env.step_size / 3600.0)
        self.total_electrical_production += self.current_electrical_production * \
            (self.env.step_size / 3600.0)


class SimulatedPeakLoadBoiler(PeakLoadBoiler):

    def __init__(self, system_id, env):
        super(SimulatedPeakLoadBoiler, self).__init__(system_id)
        self.env = env

        self.off_time = self.env.now

        self.workload = 0
        self.current_gas_consumption = 0.0  # kW
        self.current_thermal_production = 0.0  # kWh
        self.total_gas_consumption = 0  # kWh
        self.total_thermal_production = 0.0  # kWh

        self.total_hours_of_operation = 0
        self.power_on_count = 0

        self.gas_costs = 0.0655  # Euro

        self.overwrite_workload = None

    def step(self):
        if self.running:
            self.calculate_state()
            self.heat_storage.add_energy(self.get_thermal_energy_production())
            self.consume_gas()
        else:
            self.workload = 0.0

    def get_thermal_energy_production(self):
        return self.current_thermal_production * (self.env.step_size / 3600.0)

    def get_operating_costs(self):
        return self.total_gas_consumption * self.gas_costs

    def calculate_state(self):
        if self.overwrite_workload is not None:
            self.workload = self.overwrite_workload
        else:
            # turn on if heat_storage is undersupplied
            if self.heat_storage.undersupplied() and self.off_time <= self.env.now:
                if self.workload == 0.0:
                    self.power_on_count += 1

                self.total_hours_of_operation += self.env.step_size / 3600.0
                self.workload = 99.0
            # turn off if heat storage's target energy is almost reached
            elif self.current_thermal_production >= \
                self.heat_storage.get_require_energy():
                self.workload = 0.0

                if self.off_time <= self.env.now:
                    self.off_time = self.env.now + 3 * 60.0  # 3 min

        # calulate current consumption and production values
        self.current_gas_consumption = float(self.workload) / \
            99.0 * self.max_gas_input
        self.current_thermal_production = self.current_gas_consumption * \
            self.thermal_efficiency / 100.0

    def consume_gas(self):
        self.total_gas_consumption += self.current_gas_consumption * \
            (self.env.step_size / 3600.0)
        self.total_thermal_production += self.current_thermal_production * \
            (self.env.step_size / 3600.0)
