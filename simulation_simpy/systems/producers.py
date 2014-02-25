import random

from helpers import sign


class GasPoweredGenerator(object):

    def __init__(self, env):
        self.env = env
        self.gas_price_per_kwh = 0.0655  # Euro

        self.running = False

        self.workload = 0
        self.current_gas_consumption = 0  # kWh
        self.current_thermal_production = 0  # kWh
        self.total_gas_consumption = 0.0  # kWh
        self.total_thermal_production = 0.0  # kWh

        self.total_hours_of_operation = 0
        self.power_on_count = 0

    def start(self):
        self.running = True

    def stop(self):
        self.running = False

    def consume_gas(self):
        self.total_gas_consumption += self.current_gas_consumption / \
            self.env.accuracy
        self.total_thermal_production += self.current_thermal_production / \
            self.env.accuracy

    def get_operating_costs(self):
        return self.total_gas_consumption * self.gas_price_per_kwh


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

        self.current_electrical_production = 0.0  # kWh
        self.total_electrical_production = 0.0  # kWh
        self.mode = "thermal-led"


        self.overwrite_workload = None

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
        calculated_power =  self.heat_storage.get_target_energy() + \
            min_thermal_power - self.heat_storage.energy_stored()
        return calculated_power / max_thermal_power * 99.0

    def get_calculated_workload_electric(self):
        if self.heat_storage.get_temperature() >= self.heat_storage.max_temperature:
            return 0.0
        max_electric_power = self.electrical_efficiency / \
            100 * self.max_gas_input
        consumption_per_hour = self.power_meter.energy_consumed * \
            self.env.accuracy
        return consumption_per_hour / max_electric_power * 99.0

    def calculate_state(self):
        if self.overwrite_workload is not None:
            self.workload = self.overwrite_workload
        else:
            old_workload = self.workload

            if self.mode == "thermal-led":
                calculated_workload = self.get_calculated_workload_thermal()
            elif self.mode == "electric-led":
                calculated_workload = self.get_calculated_workload_electric()

            # ensure smoothly changing workload
            slope = sign(calculated_workload - old_workload)
            change_speed = 100 / 180  # percent per 3 minutes
            self.workload += change_speed * slope * self.env.step_size

            # make sure that minimal_workload <= workload <= 99.0 or workload =
            # 0
            if calculated_workload >= self.minimal_workload and self.off_time <= self.env.now:
                # detect if power has been turned on
                if old_workload == 0:
                    self.power_on_count += 1

                self.total_hours_of_operation += self.env.step_size / \
                    self.env.granularity
                self.workload = min(calculated_workload, 99.0)
            else:
                self.workload = 0.0
                if self.off_time <= self.env.now:
                    self.off_time = self.env.now + 10.0 * 60.0  # 5 min

        # calulate current consumption and production values
        self.current_gas_consumption = self.workload / \
            99.0 * self.max_gas_input

        self.current_electrical_production = self.current_gas_consumption * \
            self.electrical_efficiency * \
            self.get_efficiency_loss_factor()
        self.current_thermal_production = self.current_gas_consumption * \
            self.thermal_efficiency * self.get_efficiency_loss_factor()

    def consume_gas(self):
        super(CogenerationUnit, self).consume_gas()
        self.total_electrical_production += self.current_electrical_production / \
            self.env.accuracy

    def update(self):
        self.env.log('Starting cogeneration unit...')
        self.start()
        while True:
            if self.running:
                self.calculate_state()

                self.env.log(
                    'CU workload:', '%f %%' % self.workload, 'Total:', '%f kWh (%f Euro)' %
                    (self.total_gas_consumption, self.get_operating_costs()))

                self.power_meter.add_energy(
                    self.current_electrical_production)
                self.heat_storage.add_energy(self.current_thermal_production)
                self.consume_gas()
            else:
                self.workload = 0.0
                self.env.log('Cogeneration unit stopped')

            yield self.env.timeout(self.env.step_size)


class PeakLoadBoiler(GasPoweredGenerator):

    def __init__(self, env, heat_storage):
        GasPoweredGenerator.__init__(self, env)
        self.heat_storage = heat_storage

        self.max_gas_input = 50.0  # kW
        self.thermal_efficiency = 0.8  # %
        self.off_time = self.env.now

        self.overwrite_workload = None

    def calculate_state(self):
        if self.overwrite_workload is not None:
            self.workload = self.overwrite_workload
        else:
            # turn on if heat_storage is undersupplied
            if self.heat_storage.undersupplied() and self.off_time <= self.env.now:
                if self.workload == 0.0:
                    self.power_on_count += 1

                self.total_hours_of_operation += self.env.step_size / \
                    self.env.granularity
                self.workload = 99.0
            # turn off if heat storage's target energy is almost reached
            elif self.heat_storage.energy_stored() + self.current_thermal_production >= self.heat_storage.get_target_energy():
                self.workload = 0.0

                if self.off_time <= self.env.now:
                    self.off_time = self.env.now + 3 * 60.0  # 3 min

        # calulate current consumption and production values
        self.current_gas_consumption = self.workload / \
            99.0 * self.max_gas_input
        self.current_thermal_production = self.current_gas_consumption * \
            self.thermal_efficiency

    def update(self):
        self.env.log('Starting peak load boiler...')
        self.start()
        while True:
            if self.running:
                self.calculate_state()

                self.env.log(
                    'PLB workload:', '%f %%' % self.workload, 'Total:', '%f kWh (%f Euro)' %
                    (self.total_gas_consumption, self.get_operating_costs()))

                self.heat_storage.add_energy(self.current_thermal_production)
                self.consume_gas()
            else:
                self.workload = 0.0
                self.env.log('PLB stopped.')

            self.env.log('=' * 80)
            yield self.env.timeout(self.env.step_size)
