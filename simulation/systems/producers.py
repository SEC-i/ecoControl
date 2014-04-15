from helpers import sign
from systems import BaseSystem


class GasPoweredGenerator(BaseSystem):

    def __init__(self, env):
        super(GasPoweredGenerator, self).__init__(env)

        self.running = True

        self.workload = 0
        self.current_gas_consumption = 0  # kWh
        self.current_thermal_production = 0  # kWh
        self.total_gas_consumption = 0.0  # kWh
        self.total_thermal_production = 0.0  # kWh

        self.total_hours_of_operation = 0
        self.power_on_count = 0

        self.gas_costs = 0.0655  # Euro

    def start(self):
        self.running = True

    def stop(self):
        self.running = False

    def consume_gas(self):
        self.total_gas_consumption += self.current_gas_consumption / \
            self.env.steps_per_measurement
        self.total_thermal_production += self.current_thermal_production / \
            self.env.steps_per_measurement

    def get_operating_costs(self):
        return self.total_gas_consumption * self.gas_costs


class CogenerationUnit(GasPoweredGenerator):

    def __init__(self, env, heat_storage, power_meter):
        GasPoweredGenerator.__init__(self, env)
        self.heat_storage = heat_storage

        # vaillant ecopower 4.7
        self.max_gas_input = 19.0  # kW
        self.electrical_efficiency = 0.247  # % (max 4.7 kW)
        self.thermal_efficiency = 0.65  # % (max 12.5 kW)
        self.max_efficiency_loss = 0.15  # %
        self.maintenance_interval = 4000  # hours

        self.power_meter = power_meter

        self.minimal_workload = 40.0  # %

        self.minimal_off_time = 5.0 * 60.0
        self.off_time = self.env.now

        self.current_electrical_production = 0.0  # kW
        self.total_electrical_production = 0.0  # kWh
        self.thermal_driven = True
        self.electrical_driven_minimal_production = 1.0  # kWh (electrical)

        self.overwrite_workload = None

    @classmethod
    def copyconstruct(cls, env, other_cu, heat_storage, power_meter):
        cu = CogenerationUnit(env, heat_storage, power_meter)
        cu.__dict__ = other_cu.__dict__.copy()
        # copy will also copy references for heatstorage and powermeter, so we
        # have to change refences manually
        cu.heat_storage = heat_storage
        cu.power_meter = power_meter
        cu.env = env
        return cu

    def step(self):
        if self.running:
            self.calculate_state()
            self.power_meter.add_energy(
                self.get_electrical_energy_production())
            self.heat_storage.add_energy(self.get_thermal_energy_production())
            self.consume_gas()
        else:
            self.workload = 0.0

    def get_electrical_energy_production(self):
        return self.current_electrical_production / self.env.steps_per_measurement

    def get_thermal_energy_production(self):
        return self.current_thermal_production / self.env.steps_per_measurement

    def get_operating_costs(self):
        gas_costs = GasPoweredGenerator.get_operating_costs(self)
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
        max_thermal_power = self.thermal_efficiency * self.max_gas_input
        min_thermal_power = max_thermal_power * (self.minimal_workload / 100.0)
        calculated_power = self.heat_storage.get_require_energy(
        ) + min_thermal_power
        return min(calculated_power / max_thermal_power, 1) * 99.0

    def get_calculated_workload_electric(self):
        if self.heat_storage.get_temperature() >= self.heat_storage.target_temperature:
            return 0.0
        max_electric_power = self.electrical_efficiency * self.max_gas_input
        return min(max(self.power_meter.current_power_consum, self.electrical_driven_minimal_production) / max_electric_power, 1) * 99.0

    def calculate_state(self):
        if self.overwrite_workload is not None:
            calculated_workload = self.overwrite_workload
        else:
            old_workload = self.workload

            if self.thermal_driven:
                calculated_workload = self.get_calculated_workload_thermal()
            else:
                calculated_workload = self.get_calculated_workload_electric()

        self.update_parameters(calculated_workload)

    def update_parameters(self, calculated_workload):
        old_workload = self.workload
        # ensure smoothly changing workload
        slope = sign(calculated_workload - old_workload)
        # percent per second --> 3 minutes for full startup
        change_speed = 1.0 / 180.0 * self.env.step_size
        self.workload += change_speed * slope

        # make sure that minimal_workload <= workload <= 99.0 or workload =
        # 0
        if calculated_workload >= self.minimal_workload and self.off_time <= self.env.now:
            # detect if power has been turned on
            if old_workload == 0:
                self.power_on_count += 1

            self.total_hours_of_operation += self.env.step_size / \
                self.env.measurement_interval
            self.workload = min(calculated_workload, 99.0)
        else:
            self.workload = 0.0
            if self.off_time <= self.env.now:
                self.off_time = self.env.now + 10.0 * 60.0  # 5 min

        # calulate current consumption and production values
        self.current_gas_consumption = self.workload / \
            99.0 * self.max_gas_input

        self.current_electrical_production = self.current_gas_consumption * \
            self.electrical_efficiency * self.get_efficiency_loss_factor()
        self.current_thermal_production = self.current_gas_consumption * \
            self.thermal_efficiency * self.get_efficiency_loss_factor()

    def consume_gas(self):
        GasPoweredGenerator.consume_gas(self)
        self.total_electrical_production += self.current_electrical_production * \
            (self.env.step_size / 3600.0)


class PeakLoadBoiler(GasPoweredGenerator):

    def __init__(self, env, heat_storage):
        GasPoweredGenerator.__init__(self, env)
        self.heat_storage = heat_storage

        self.max_gas_input = 50.0  # kW
        self.thermal_efficiency = 0.8  # %
        self.off_time = self.env.now

        self.overwrite_workload = None

    @classmethod
    def copyconstruct(cls, env, other_plb, heat_storage):
        plb = PeakLoadBoiler(env, heat_storage)
        plb.__dict__ = other_plb.__dict__.copy()
        plb.heat_storage = heat_storage
        plb.env = env
        return plb

    def step(self):
        if self.running:
            self.calculate_state()
            self.heat_storage.add_energy(self.get_thermal_energy_production())
            self.consume_gas()
        else:
            self.workload = 0.0

    def get_thermal_energy_production(self):
        return self.current_thermal_production / self.env.steps_per_measurement

    def calculate_state(self):
        if self.overwrite_workload is not None:
            self.workload = self.overwrite_workload
        else:
            # turn on if heat_storage is undersupplied
            if self.heat_storage.undersupplied() and self.off_time <= self.env.now:
                if self.workload == 0.0:
                    self.power_on_count += 1

                self.total_hours_of_operation += self.env.step_size / \
                    self.env.measurement_interval
                self.workload = 99.0
            # turn off if heat storage's target energy is almost reached
            elif self.current_thermal_production >= self.heat_storage.get_require_energy():
                self.workload = 0.0

                if self.off_time <= self.env.now:
                    self.off_time = self.env.now + 3 * 60.0  # 3 min

        # calulate current consumption and production values
        self.current_gas_consumption = self.workload / \
            99.0 * self.max_gas_input
        self.current_thermal_production = self.current_gas_consumption * \
            self.thermal_efficiency
