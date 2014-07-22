from base import BaseSystem


class ThermalConsumer(BaseSystem):
    """This class represents the thermal consume of the house.
    The demand is calculated by the necessary heating power and the required warm water.
    The house parameters are read from the database and can be set from the frontend.
    The following parameters are available:

    :param int apartments: number of apartments in the house
    :param int avg_rooms_per_apartment: average number of rooms
    :param int avg_windows_per_room: average number of windows
    :param int type_of_windows: isolation value between MISSING
    :param int total_living_area: in square meters
    :param int type_of_housing: isolation value between MISSING
    :param int residents:
    :param int type_of_residents: used to classify thermal demand MISSING RANGE
    :param int target_temperature: requested temperature of the rooms in degree Celsius
    :param int avg_thermal_consumption: in kWh
    """

    def __init__(self, system_id, env):
        super(ThermalConsumer, self).__init__(system_id, env)

        self.config = {
            'apartments' : 8,
            'avg_rooms_per_apartment': 4,
            'avg_windows_per_room': 3,
            'type_of_windows': 0,
            'total_heated_floor': 650,
            'type_of_housing': 0,
            'residents': 24,
            'type_of_residents': 0,
            'target_temperature': 20,
            'avg_thermal_consumption': 0,
        }

        self.heat_storage = None

        self.temperature_room = 18.0
        #: temperature of warm water 40 degrees Celsius by default
        self.temperature_warmwater = 40.0

        #: list of 24 values representing target_temperature per hour
        self.daily_demand = [19, 19, 19, 19, 19, 19, 19, 20, 21,
                             20, 20, 21, 20, 21, 21, 21, 21, 22, 22, 22, 22, 22, 21, 19]

        self.room_height = 2.5  #: constant room height
        self.heating_constant = 100
        # heat transfer coefficient normal glas window in W/(m^2 * K)
        # normal glas 5.9, isolated 1.1
        self.heat_transfer_window = 2.2
        self.heat_transfer_wall = 0.5

        self.consumed = 0
        self.current_power = 0

    def find_dependent_devices_in(self, system_list):
        for system in system_list:
            system.attach_to_thermal_consumer(self)

    def connected(self):
        """The device needs a `HeatStorage` to operate properly."""
        return self.heat_storage is not None

    def get_warmwater_consumption_power(self):
        raise NotImplementedError

    def get_outside_temperature(self, offset_days=0):
        raise NotImplementedError

    def get_consumption_power(self):
        # convert to kW
        return self.current_power / 1000.0

class ElectricalConsumer(BaseSystem):
    """This class represents the electrical consume of the house.
    The demand is calculated by the forecasting in :mod:server.forecasting.forecasting
    The house parameters are read from the database and can be set from the frontend.
    The following parameters are available:

    :param int apartments: number of apartments in the house
    :param int residents:
    :param int type_of_residents: used to classify thermal demand MISSING RANGE
    :param int avg_electrical_consumption: in kWh
    """

    def __init__(self, system_id, env):
        super(ElectricalConsumer, self).__init__(system_id, env)

        self.config = {
            'apartments' : 12,
            'residents': 22,
            'type_of_residents': 0,
            'avg_electrical_consumption': 0,
        }

        self.power_meter = None
        self.total_consumption = 0.0

    def find_dependent_devices_in(self, system_list):
        for system in system_list:
            system.attach_to_electrical_consumer(self)

    def connected(self):
        """The device needs a `PowerMeter` to operate properly."""
        return self.power_meter is not None

    def get_consumption_power(self):
        raise NotImplementedError