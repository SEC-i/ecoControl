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

    def __init__(self, env, heat_storage, electrical_infeed):
        GasPoweredGenerator.__init__(self, env)
        self.heat_storage = heat_storage

        # XRGI 15kW
        self.max_gas_input = 49.0  # kW
        self.electrical_efficiency = 0.3  # max 14.7 kW
        self.thermal_efficiency = 0.62  # max 30.38 kW
        self.max_efficiency_loss = 0.1  # %
        self.maintenance_interval = 8500  # hours

        self.electrical_infeed = electrical_infeed

        self.minimal_workload = 40.0  # %

        self.current_electrical_production = 0.0  # kWh
        self.total_electrical_production = 0.0  # kWh

        self.overwrite_workload = None

    def get_efficiency_loss_factor(self):
        # given efficiency is reached only on maximum workload
        # at minumum workload the efficiency is decreased with
        # max_efficiency_loss
        relative_loss = 1.0 - (self.workload - self.minimal_workload) \
            / (99.0 - self.minimal_workload)
        return 1.0 - self.max_efficiency_loss * relative_loss

    def calculate_state(self):
        if self.overwrite_workload:
            self.workload = self.overwrite_workload
        else:
            old_workload = self.workload
            calculated_workload = self.heat_storage.get_target_energy() + \
                self.minimal_workload - self.heat_storage.energy_stored()

            # ensure smoothly changing workload
            slope = sign(calculated_workload - old_workload)
            change_speed = 100 / 180  # percent per 3 minutes
            self.workload += change_speed * slope * self.env.step_size

            # make sure that minimal_workload <= workload <= 99.0 or workload =
            # 0
            if calculated_workload >= self.minimal_workload:
                # detect if power has been turned on
                if old_workload == 0:
                    self.power_on_count += 1

                self.total_hours_of_operation += self.env.step_size / self.env.granularity
                self.workload = min(calculated_workload, 99.0)
            else:
                self.workload = 0.0

        # calulate current consumption and production values
        self.current_gas_consumption = self.workload / \
            99.0 * self.max_gas_input

        self.current_electrical_production = self.current_gas_consumption * \
            self.electrical_efficiency * self.get_efficiency_loss_factor()
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

                self.electrical_infeed.add_energy(
                    self.current_electrical_production)
                self.heat_storage.add_energy(self.current_thermal_production)
                self.consume_gas()
            else:
                self.env.log('Cogeneration unit stopped')

            yield self.env.timeout(self.env.step_size)


class PeakLoadBoiler(GasPoweredGenerator):

    def __init__(self, env, heat_storage):
        GasPoweredGenerator.__init__(self, env)
        self.heat_storage = heat_storage

        self.max_gas_input = 100.0  # kW
        self.thermal_efficiency = 0.8

        self.overwrite_workload = None

    def calculate_state(self):
        if self.overwrite_workload:
            self.workload = self.overwrite_workload
        else:
            # turn on if heat_storage is undersupplied
            if self.heat_storage.undersupplied():
                if self.workload == 0.0:
                    self.power_on_count += 1

                self.total_hours_of_operation += self.env.step_size / self.env.granularity
                self.workload = 99.0
            # turn off if heat storage's target energy is almost reached
            elif self.heat_storage.energy_stored() + self.current_thermal_production >= self.heat_storage.get_target_energy():
                self.workload = 0.0

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
                self.env.log('PLB stopped.')

            self.env.log('=' * 80)
            yield self.env.timeout(self.env.step_size)
