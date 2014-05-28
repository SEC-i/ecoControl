from server.forecasting.forecasting.systems.consumers as consumers


class RealThermalConsumer(consumers.ThermalConsumer):

    def __init__(self, system_id, env):

        super(ThermalConsumer, self).__init__(system_id, env)

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

        global weather_forecast
        if weather_forecast == None:
            weather_forecast = WeatherForecast(self.env)
        self.weather_forecast = weather_forecast
        self.current_power = 0

        # only build once, to save lots of time
        #self.warmwater_forecast = Forecast(self.env, input_data, samples_per_hour=1)

        self.calculate()

    def find_dependent_devices_in(self, system_list):
        raise NotImplementedError

    def connected(self):
        raise NotImplementedError

    def calculate(self):
        raise NotImplementedError

    def step(self):
        raise NotImplementedError

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

    def linear_interpolation(self, a, b, x):
        raise NotImplementedError


class RealElectricalConsumer(consumers.ElectricalConsumer):

    def __init__(self, system_id, env, residents=22):
        super(ElectricalConsumer, self).__init__(system_id, env)

        self.power_meter = None
        self.residents = residents
        self.total_consumption = 0.0  # kWh

        # list of 24 values representing relative demand per hour
        self.demand_variation = [1 for i in range(24)]

        self.new_data_interval = 24 * 60 * 60  # append data each day
        self.last_forecast_update = self.env.now

    def find_dependent_devices_in(self, system_list):
        raise NotImplementedError

    def connected(self):
        raise NotImplementedError

    def step(self):
        raise NotImplementedError

    def update_forecast_data(self):
        raise NotImplementedError

    def get_consumption_power(self):
        raise NotImplementedError

    def get_consumption_energy(self):
        return self.get_consumption_power() * (self.env.step_size / 3600.0)

    def get_data_until(self, timestamp, start_timestamp=None):
        raise NotImplementedError
