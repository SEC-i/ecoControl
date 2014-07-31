from server.devices.base import BaseDevice


class CogenerationUnit(BaseDevice):
    """Represents a basic interface to a cogeneration unit.
    The configuration is read from the database and can be set from the frontend.
    The following parameters are available:

    :param float max_gas_input: in kW
    :param float thermal_efficiency: in percent between 0 and 1 calculated by the maximal thermal power and gas input
    :param float electrical_efficiency: in percent between 0 and 1 calculated by the maximal electrical power and gas input
    :param float minimal_workload: in percent between 0 and 1 used for modulation
    :param float minimal_off_time: minimal time between to power-ons in seconds
    :param float purchase_price: in Euro
    :param date purchase_date: to calculate armotization
    :param int maintenance_interval_hours: operating hours until maintenance is necessary
    :param int maintenance_interval_powerons: maximal power-ons until maintenance is necessary
    """

    def __init__(self, device_id, env):
        super(CogenerationUnit, self).__init__(device_id, env)

        # Vaillant ecoPOWER 4.7
        self.config = {
            'max_gas_input': 19.0,
            'thermal_efficiency': 0.65,
            'electrical_efficiency': 0.247,
            'minimal_workload': 0.40,
            'minimal_off_time': 600.0,
            'purchase_price': 15000.0,
            'purchase_date': '01.01.2013',
            'maintenance_interval_hours': 8000.0,
            'maintenance_interval_powerons': 2000.0,
        }

        self.heat_storage = None
        self.power_meter = None
        self.running = True
        self.thermal_driven = True

        self.workload = 0
        self.current_gas_consumption = 0.0  #: kW
        self.current_thermal_production = 0.0  #: kWh
        self.total_gas_consumption = 0  #: kWh
        self.total_thermal_production = 0.0  #: kWh

        self.current_electrical_production = 0.0  #: kW
        self.total_electrical_production = 0.0  #: kWh

        self.total_hours_of_operation = 0
        self.power_on_count = 0

        self.gas_costs = 0.0655  #: default 0.0655 Euro per kWh

    def workload_percent(self, workload=None):
        """Getter and setter for the workload.

        :param float workload: between 0-100, if None nothing is set

        :returns: current workload in percent [0,100]
        """
        if workload is not None:
            self.workload = workload / 100.0
        return self.workload * 100.0

    def find_dependent_devices_in(self, device_list):
        for device in device_list:
            device.attach_to_cogeneration_unit(self)

    def connected(self):
        """The device needs a `PowerMeter` and a `HeatStorage` to operate properly."""
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
        """Calculated by the consumed gas and maintenance costs (0.05 Euro per electric produced kWh). """
        gas_costs = self.total_gas_consumption * self.gas_costs
        maintenance_costs = self.total_electrical_production * \
            0.05
        return maintenance_costs + gas_costs


class PeakLoadBoiler(BaseDevice):
    """Represents a basic interface to a cogeneration unit.
    The configuration is read from the database and can be set from the frontend.
    The following parameters are available:

    :param float max_gas_input: in kW
    :param float thermal_efficiency: in percent between 0 and 1 calculated by the maximal thermal power and gas input
    """

    def __init__(self, device_id, env):
        super(PeakLoadBoiler, self).__init__(device_id, env)

        self.config = {
            'max_gas_input': 0.45,
            'thermal_efficiency': 0.91,
        }

        self.heat_storage = None
        self.running = True

        self.workload = 0
        self.current_gas_consumption = 0.0  #: kW
        self.current_thermal_production = 0.0  #: kWh
        self.total_gas_consumption = 0  #: kWh
        self.total_thermal_production = 0.0  #: kWh

        self.total_hours_of_operation = 0
        self.power_on_count = 0

        self.gas_costs = 0.0655  #: default 0.0655 Euro

    def workload_percent(self, workload=None):
        """Getter and setter for the workload.

        :param float workload: between 0-100, if None nothing is set

        :returns: current workload in [0,100]
        """
        if workload is not None:
            self.workload = workload / 100.0
        return self.workload * 100.0

    def find_dependent_devices_in(self, device_list):
        for device in device_list:
            device.attach_to_peak_load_boiler(self)

    def connected(self):
        """The device needs a `HeatStorage` to operate properly."""
        return self.heat_storage is not None

    def start(self):
        self.running = True

    def stop(self):
        self.running = False

    def get_thermal_energy_production(self):
        raise NotImplementedError

    def get_operating_costs(self):
        """Calculated by the consumed gas. """
        return self.total_gas_consumption * self.gas_costs