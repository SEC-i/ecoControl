from server.forecasting.forecasting.systems.producers as producers


class RealCogenerationUnit(producers.CogenerationUnit):

    def __init__(self, system_id, env, max_gas_input=19.0, electrical_efficiency=24.7, thermal_efficiency=65, maintenance_interval=4000, minimal_workload=40.0):

        GasPoweredGenerator.__init__(self, system_id, env)
        self.power_meter = None

        # vaillant ecopower 4.7
        self.max_gas_input = max_gas_input  # kW
        # % (max 4.7 kW)
        self.electrical_efficiency = electrical_efficiency
        self.thermal_efficiency = thermal_efficiency  # % (max 12.5 kW)
        self.max_efficiency_loss = 0.15  # %
        self.maintenance_interval = maintenance_interval  # hours

        self.minimal_workload = minimal_workload  # %

        self.minimal_off_time = 10.0 * 60.0
        self.off_time = self.env.now

        self.current_electrical_production = 0.0  # kW
        self.total_electrical_production = 0.0  # kWh
        self.thermal_driven = True
        self.electrical_driven_minimal_production = 1.0  # kWh (electrical)

        self.overwrite_workload = None

    def find_dependent_devices_in(self, system_list):
        raise NotImplementedError

    def connected(self):
        raise NotImplementedError

    def step(self):
        raise NotImplementedError

    def calculate_new_workload(self):
        raise NotImplementedError

    def get_electrical_energy_production(self):
        return self.current_electrical_production * (self.env.step_size / 3600.0)

    def get_thermal_energy_production(self):
        return self.current_thermal_production * (self.env.step_size / 3600.0)

    def get_operating_costs(self):
        raise NotImplementedError

    def get_efficiency_loss_factor(self):
        raise NotImplementedError

    def get_calculated_workload_thermal(self):
        raise NotImplementedError

    def get_calculated_workload_electric(self):
        raise NotImplementedError

    def update_parameters(self, calculated_workload):
        raise NotImplementedError

    def consume_gas(self):
        raise NotImplementedError


class RealPeakLoadBoiler(producers.PeakLoadBoiler):

    def __init__(self, system_id, env, max_gas_input=45.0, thermal_efficiency=80.0):
        GasPoweredGenerator.__init__(self, system_id, env)

        self.max_gas_input = max_gas_input  # kW
        self.thermal_efficiency = thermal_efficiency  # %
        self.off_time = self.env.now

        self.overwrite_workload = None

    def find_dependent_devices_in(self, system_list):
        raise NotImplementedError

    def connected(self):
        raise NotImplementedError

    def step(self):
        raise NotImplementedError

    def get_thermal_energy_production(self):
        return self.current_thermal_production * (self.env.step_size / 3600.0)

    def calculate_state(self):
        raise NotImplementedError
