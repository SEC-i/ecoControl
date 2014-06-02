from server.systems.base import BaseSystem


class CogenerationUnit(BaseSystem):

    def __init__(self, system_id, env):

        super(CogenerationUnit, self).__init__(system_id, env)
        # vaillant ecopower 4.7
        self.max_gas_input = 19.0  # kW
        # % (max 4.7 kW)
        self.electrical_efficiency = 24.7
        self.thermal_efficiency = 65.0  # % (max 12.5 kW)
        self.max_efficiency_loss = 0.15  # %
        self.maintenance_interval = 4000  # hours

        self.minimal_workload = 40.0  # %

        self.minimal_off_time = 10.0 * 60.0
        self.off_time = 0  # self.env.now

        self.heat_storage = None
        self.running = True

        self.workload = 0
        self.current_gas_consumption = 0.0  # kW
        self.current_thermal_production = 0.0  # kWh
        self.total_gas_consumption = 0  # kWh
        self.total_thermal_production = 0.0  # kWh

        self.gas_costs = 0.0655  # Euro

        self.power_meter = None

        self.current_electrical_production = 0.0  # kW
        self.total_electrical_production = 0.0  # kWh
        self.thermal_driven = True
        self.electrical_driven_minimal_production = 1.0  # kWh (electrical)

    def find_dependent_devices_in(self, system_list):
        for system in system_list:
            system.attach_to_cogeneration_unit(self)

    def connected(self):
        return self.power_meter is not None and self.heat_storage is not None

    def start(self):
        self.running = True

    def stop(self):
        self.running = False

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

    def get_operating_costs(self):
        return self.total_gas_consumption * self.gas_costs

    def update_parameters(self, calculated_workload):
        raise NotImplementedError


class PeakLoadBoiler(BaseSystem):

    def __init__(self, system_id, env):
        super(PeakLoadBoiler, self).__init__(system_id, env)

        self.max_gas_input = 45.0  # kW
        self.thermal_efficiency = 80.0  # %
        self.off_time = 0  # self.env.now

        self.heat_storage = None
        self.running = True

        self.workload = 0
        self.current_gas_consumption = 0.0  # kW
        self.current_thermal_production = 0.0  # kWh
        self.total_gas_consumption = 0  # kWh
        self.total_thermal_production = 0.0  # kWh

        self.total_hours_of_operation = 0
        self.power_on_count = 0

        self.gas_costs = 0.0655  # Euro

        self.overwrite_workload = None

    def find_dependent_devices_in(self, system_list):
        for system in system_list:
            system.attach_to_peak_load_boiler(self)

    def connected(self):
        return self.heat_storage is not None

    def start(self):
        self.running = True

    def stop(self):
        self.running = False

    def get_thermal_energy_production(self):
        return self.current_thermal_production * (self.env.step_size / 3600.0)

    def get_operating_costs(self):
        return self.total_gas_consumption * self.gas_costs
