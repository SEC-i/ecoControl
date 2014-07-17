from server.systems.base import BaseSystem


class CogenerationUnit(BaseSystem):

    def __init__(self, system_id, env):
        super(CogenerationUnit, self).__init__(system_id, env)

        # Vaillant ecoPOWER 4.7
        self.config = {
            'max_gas_input': 19.0,  # kW
            'thermal_efficiency': 0.65,  # % (max 12.5 kW)
            'electrical_efficiency': 0.247,  # % (max 4.7 kW)
            'minimal_workload': 0.40,  # %
            'minimal_off_time': 600.0,  # seconds
            'purchase_price': 15000.0,  # Euro
            'purchase_date': '01.01.2013',
            'maintenance_interval_hours': 8000.0,  # hours
            'maintenance_interval_powerons': 2000.0,
        }

        self.heat_storage = None
        self.power_meter = None
        self.running = True
        self.thermal_driven = True

        self.workload = 0
        self.current_gas_consumption = 0.0  # kW
        self.current_thermal_production = 0.0  # kWh
        self.total_gas_consumption = 0  # kWh
        self.total_thermal_production = 0.0  # kWh

        self.current_electrical_production = 0.0  # kW
        self.total_electrical_production = 0.0  # kWh

        self.total_hours_of_operation = 0
        self.power_on_count = 0

        self.gas_costs = 0.0655  # Euro

    def workload_percent(self, workload=None):
        if workload is not None:
            self.workload = workload / 100.0
        return self.workload * 100.0

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
        raise NotImplementedError

    def get_thermal_energy_production(self):
        raise NotImplementedError

    def get_operating_costs(self):
        gas_costs = self.total_gas_consumption * self.gas_costs
        maintenance_costs = self.total_electrical_production * \
            0.05
        return maintenance_costs + gas_costs


class PeakLoadBoiler(BaseSystem):

    def __init__(self, system_id, env):
        super(PeakLoadBoiler, self).__init__(system_id, env)

        self.config = {
            'max_gas_input': 0.45,  # kW
            'thermal_efficiency': 0.91,  # %
        }

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

    def workload_percent(self, workload=None):
        if workload is not None:
            self.workload = workload / 100.0
        return self.workload * 100.0

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
        raise NotImplementedError

    def get_operating_costs(self):
        return self.total_gas_consumption * self.gas_costs