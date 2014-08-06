from server.devices.base import BaseDevice


class HeatStorage(BaseDevice):
    """Represents a heat storage necessary to supply heating and warm water demand.
    The temperatures of the storage are as average and measured in degree Celsius.
    The configuration is read from the database and can be set from the frontend.
    The following parameters are available:

    :param int capacity: in liters
    :param float min_temperature: below this temperature the PeakLoadBoiler will turn on
    :param float target_temperature: the HS schould always have this temperature
    :param float critical_temperature: above this temperature all production devices are turned off
    """
    acronym = "hs"

    def __init__(self, device_id, env):
        super(HeatStorage, self).__init__(device_id, env)
        self.config = {
            'capacity': 2500,
            'min_temperature': 55.0,
            'target_temperature': 85.0,
            'critical_temperature': 90.0,
        }

        #: specific heat capacity of water 4.19 J/(g*K)
        self.specific_heat_capacity = 4.19 / 3600.0 # convert to kWh/(kg*K)
        self.base_temperature = 20.0 #: assume no lower temperature


    def attach_to_cogeneration_unit(self, device):
        device.heat_storage = self

    def attach_to_peak_load_boiler(self, device):
        device.heat_storage = self

    def attach_to_thermal_consumer(self, device):
        device.heat_storage = self

    def get_temperature(self):
        raise NotImplementedError

    def undersupplied(self):
        raise NotImplementedError


class PowerMeter(BaseDevice):
    """Represents the power meter of the whole building.
    Measures the purchased and fed in electricity in kWh
    """
    acronym = "pm"

    def __init__(self, device_id, env):
        super(PowerMeter, self).__init__(device_id, env)

        self.fed_in_electricity = 0.0 #: since last step
        self.purchased = 0 #: since last step
        self.total_fed_in_electricity = 0.0
        self.total_purchased = 0

        #: set by producer devices with `add_energy`
        self.energy_produced = 0.0
        #: set by consumer devices with `consume_energy`
        self.energy_consumed = 0.0

        #: costs in Euro to purchase 1 kW/h from external supplier (default 0.283)
        self.electrical_costs = 0.283
        #: reward in Euro for feed in 1 kW/h to public grid (default 0.0917)
        self.feed_in_reward = 0.0917

    def attach_to_cogeneration_unit(self, device):
        device.power_meter = self

    def attach_to_electrical_consumer(self, device):
        device.power_meter = self

    def add_energy(self, energy):
        """This counts up the produced energy.

        :param float energy: in kWh
        """
        raise NotImplementedError

    def consume_energy(self, energy):
        """This counts up the consumed energy.

        :param float energy: in kWh
        """
        raise NotImplementedError

    def get_reward(self):
        """Calculated by overall fed in electricity and the default reward of 0.0917 Euro per kWh.
        Sale to tenants is not considered here."""
        return self.total_fed_in_electricity * self.feed_in_reward

    def get_costs(self):
        """Calculated by overall purchased electricity and default costs of 0.283 Euro per kWh"""
        return self.total_purchased * self.electrical_costs