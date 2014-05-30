from server.systems import BaseSystem


class CogenerationUnit(BaseSystem):

    def __init__(self, system_id):

        super(CogenerationUnit, self).__init__(system_id)
        self.power_meter = None

        # vaillant ecopower 4.7
        self.max_gas_input = 19.0  # kW
        # % (max 4.7 kW)
        self.electrical_efficiency = 24.7
        self.thermal_efficiency = 65  # % (max 12.5 kW)
        self.max_efficiency_loss = 0.15  # %
        self.maintenance_interval = 4000  # hours

        self.minimal_workload = 40.0  # %

        self.minimal_off_time = 10.0 * 60.0
        self.off_time = 0 # self.env.now

        self.current_electrical_production = 0.0  # kW
        self.total_electrical_production = 0.0  # kWh
        self.thermal_driven = True
        self.electrical_driven_minimal_production = 1.0  # kWh (electrical)

        self.overwrite_workload = None

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


class PeakLoadBoiler(BaseSystem):

    def __init__(self, system_id):
        super(PeakLoadBoiler, self).__init__(system_id)

        self.max_gas_input = 45.0  # kW
        self.thermal_efficiency = 80.0  # %
        self.off_time = 0 # self.env.now

        self.overwrite_workload = None

    def get_thermal_energy_production(self):
        return self.current_thermal_production * (self.env.step_size / 3600.0)

    def calculate_state(self):
        raise NotImplementedError
