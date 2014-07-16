from base import BaseSystem
# from server.forecasting.forecasting.weather import WeatherForecast

electrical_forecast = None
weather_forecast = None


class ThermalConsumer(BaseSystem):

    def __init__(self, system_id, env):
        super(ThermalConsumer, self).__init__(system_id, env)

        self.config = {
            'apartments' : 12,
            'avg_rooms_per_apartment': 4,
            'residents': 22,
            'avg_thermal_consumption': 0,
            'type_of_housing': 0,
            'avg_windows_per_room': 3,
            'total_heated_floor': 650,
            'type_of_residents': 0,
            'type_of_windows': 0,
            'target_temperature': 20,
        }

        self.heat_storage = None

        # initial temperature
        self.temperature_room = 18.0
        self.temperature_warmwater = 40.0

        # list of 24 values representing target_temperature per hour
        self.daily_demand = [19, 19, 19, 19, 19, 19, 19, 20, 21,
                             20, 20, 21, 20, 21, 21, 21, 21, 22, 22, 22, 22, 22, 21, 19]

        self.total_heated_floor = 650
        self.room_height = 2.5  # constant
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
        return self.heat_storage is not None

    def get_warmwater_consumption_power(self):
        raise NotImplementedError

    def get_outside_temperature(self, offset_days=0):
        raise NotImplementedError

    def get_consumption_power(self):
        # convert to kW
        return self.current_power / 1000.0

class ElectricalConsumer(BaseSystem):

    def __init__(self, system_id, env):
        super(ElectricalConsumer, self).__init__(system_id, env)

        self.config = {
            'apartments' : 12,
            'residents': 22,
            'avg_electrical_consumption': 0,
            'type_of_residents': 0,
        }

        self.power_meter = None
        self.total_consumption = 0.0  # kWh

    def find_dependent_devices_in(self, system_list):
        for system in system_list:
            system.attach_to_electrical_consumer(self)

    def connected(self):
        return self.power_meter is not None

    def get_consumption_power(self):
        raise NotImplementedError