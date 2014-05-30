from server.systems import BaseSystem
from server.forecasting.forecasting.weather import WeatherForecast

electrical_forecast = None
weather_forecast = None


class ThermalConsumer(BaseSystem):

    def __init__(self, system_id):

        super(ThermalConsumer, self).__init__(system_id)

        self.heat_storage = None

        # initial temperature
        self.temperature_room = 12.0
        self.temperature_warmwater = 40.0

        # list of 24 values representing target_temperature per hour
        self.daily_demand = [19, 19, 19, 19, 19, 19, 19, 20, 21,
                             20, 20, 21, 20, 21, 21, 21, 21, 22, 22, 22, 22, 22, 21, 19]
        self.target_temperature = self.daily_demand[0]

        self.total_heated_floor = 650
        self.room_height = 2.5  # constant
        self.residents = 22
        self.apartments = 12
        self.avg_rooms_per_apartment = 4
        self.avg_windows_per_room = 3
        self.heating_constant = 100
        # heat transfer coefficient normal glas window in W/(m^2 * K)
        # normal glas 5.9, isolated 1.1
        self.heat_transfer_window = 2.2
        self.heat_transfer_wall = 0.5

        self.consumed = 0

        # global weather_forecast
        # if weather_forecast == None:
        #     weather_forecast = WeatherForecast(self.env)
        # self.weather_forecast = weather_forecast
        self.current_power = 0

        self.calculate()

    def heat_room(self):
        raise NotImplementedError

    def get_consumption_power(self):
        # convert to kW
        return self.current_power / 1000.0

    def get_consumption_energy(self):
        # convert to kWh
        return self.get_consumption_power() * (self.env.step_size / 3600.0)

    def get_warmwater_consumption_power(self):
        raise NotImplementedError

    def get_warmwater_consumption_energy(self):
        return self.get_warmwater_consumption_power() * (self.env.step_size / 3600.0)

    def simulate_consumption(self):
        raise NotImplementedError

    def heat_loss_power(self):
        raise NotImplementedError

    def get_outside_temperature(self, offset_days=0):
        raise NotImplementedError


class ElectricalConsumer(BaseSystem):

    def __init__(self, system_id):
        super(ElectricalConsumer, self).__init__(system_id)

        self.power_meter = None
        self.residents = 22
        self.total_consumption = 0.0  # kWh

        # list of 24 values representing relative demand per hour
        self.demand_variation = [1 for i in range(24)]

        self.new_data_interval = 24 * 60 * 60  # append data each day
        self.last_forecast_update = 0  # self.env.now

    def update_forecast_data(self):
        raise NotImplementedError

    def get_consumption_power(self):
        raise NotImplementedError

    def get_consumption_energy(self):
        return self.get_consumption_power() * (self.env.step_size / 3600.0)

    def get_data_until(self, timestamp, start_timestamp=None):
        raise NotImplementedError
