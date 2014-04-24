import time

from helpers import BaseSystem, interpolate_year
from data import weekly_electrical_demand_winter, weekly_electrical_demand_summer, warm_water_demand_workday, warm_water_demand_weekend
from server.forecasting.forecasting.weather import WeatherForecast


class ThermalConsumer(BaseSystem):

    """
    physically based heating, using formulas from 
    http://www.model.in.tum.de/um/research/groups/ai/fki-berichte/postscript/fki-227-98.pdf and
    http://www.inference.phy.cam.ac.uk/is/papers/DanThermalModellingBuildings.pdf 
    house data from pamiru48 (12 apartments with 22 persons)

    env - simpy simulation environment
    heat_storage - HeatStorge for energy supply
    total_heated_floor - area of simulated house in square meter (650)
    residents - number of residents (22)
    apartments - number of apartments (12)
    avg_rooms_per_appartment - average room number (4)
    average_window_per_room (4)
    heating_constant - heating demand per square meter in W (rule of thumb for new housing: 100)
    """

    def __init__(self, env):

        super(ThermalConsumer, self).__init__(env)

        self.heat_storage = None

        self.target_temperature = 20.0  # is overwritten by daily_demand
        self.total_consumption = 0.0
        # initial temperature
        self.temperature_room = 12.0
        self.temperature_warmwater = 40.0

        # list of 24 values representing  target_temperature per hour
        self.daily_demand = [19, 19, 19, 19, 19, 19, 19, 20, 21,
                             20, 20, 21, 20, 21, 21, 21, 21, 22, 22, 22, 22, 22, 21, 19]

        self.total_heated_floor = 650
        self.residents = 22
        self.apartments = 12
        self.avg_rooms_per_apartment = 4
        self.avg_windows_per_room = 4
        self.heating_constant = 100

        self.consumed = 0
        self.weather_forecast = WeatherForecast(self.env)

        self.calculate()

    def connected(self):
        return self.heat_storage is not None

    def calculate(self):

        # 2.5m high walls
        self.total_heated_volume = self.total_heated_floor * 2.5
        avg_room_volume = self.total_heated_volume / \
            (self.apartments * self.avg_rooms_per_apartment)
        # avg surface of a cube side, so multiply with 6 to get the whole
        # surface
        avg_wall_size = avg_room_volume ** (2.0 / 3.0)  # m^2
        # lets have each appartment have an average of 1.5 outer walls
        self.outer_wall_surface = avg_wall_size * self.apartments * 1.5
        self.max_power = self.total_heated_floor * \
            float(self.heating_constant)  # W

        self.current_power = 0
        # m^2
        self.window_surface = self.avg_windows_per_room * \
            self.avg_rooms_per_apartment * self.apartments

        specific_heat_capacity_brick = 1360 * 10 ** 6  # J/(m^3 * K)
        # J / K, approximation for 5 walls including ceiling, 0.36m wall
        # thickness,
        heat_cap_brick_per_room = specific_heat_capacity_brick * \
            (avg_wall_size * 5 * 0.36)
        self.heat_cap_brick = heat_cap_brick_per_room * \
            self.avg_rooms_per_apartment * self.apartments

        #J /( m^3 * K)
        self.specific_heat_capacity_air = 1290.0
        self.heat_capacity_air = self.specific_heat_capacity_air * \
            self.total_heated_volume

        # object factor--> we have some objects, which slow down heating and cooling
        #--> used to make heating and cooling look realistic ;)
        stuff_weight = self.total_heated_volume * \
            50.0  # assume 50.0 kilo per m^3 of heatable objects (wood)
        heat_capacity_stuff = stuff_weight * 600.0  # 600 = spec heat cap wood

        self.heat_capacity = self.heat_capacity_air + heat_capacity_stuff

        self.room_power = self.heat_capacity_air * self.temperature_room

    @classmethod
    def copyconstruct(cls, env, other_thermal_consumer, heat_storage):
        thermal_consumer = ThermalConsumer(env, heat_storage)
        thermal_consumer.__dict__ = other_thermal_consumer.__dict__.copy()
        thermal_consumer.heat_storage = heat_storage
        thermal_consumer.env = env
        return thermal_consumer

    def step(self):
        self.simulate_consumption()
        consumption = self.get_consumption_energy(
        ) + self.get_warmwater_consumption_energy()
        self.consumed += consumption
        self.total_consumption += consumption
        self.heat_storage.consume_energy(consumption)

    def calculate_room_temperature(self):
        gas_constant = 287.0  # J/(kg*K)
        temperature_kelvin = self.temperature_room + 273
        normal_pressure = 101325.0  # pascal

        nominator = gas_constant * temperature_kelvin
        denominator = normal_pressure * self.heat_capacity
        temp_delta = nominator / denominator * \
            self.room_power * self.env.step_size
        self.temperature_room += temp_delta

    def get_consumption_power(self):
        # convert to kW
        return self.current_power / 1000.0

    def get_consumption_energy(self):
        # convert to kWh
        return self.get_consumption_power() * (self.env.step_size / 3600.0)

    def get_warmwater_consumption_power(self):
        specific_heat_capacity_water = 0.001163708  # kWh/(kg*K)
        time_tuple = time.gmtime(self.env.now)

        hour = time_tuple.tm_hour
        wday = time_tuple.tm_wday
        weight = time_tuple.tm_min / 60.0
        if wday in [5, 6]:  # weekend
            demand_liters_per_hour = self.linear_interpolation(
                warm_water_demand_weekend[hour],
                warm_water_demand_weekend[(hour + 1) % 24], weight)
        else:
            demand_liters_per_hour = self.linear_interpolation(
                warm_water_demand_workday[hour],
                warm_water_demand_workday[(hour + 1) % 24], weight)

        power_demand = demand_liters_per_hour * \
            (self.temperature_warmwater - self.heat_storage.base_temperature) * \
            specific_heat_capacity_water
        return power_demand * self.residents

    def get_warmwater_consumption_energy(self):
        return self.get_warmwater_consumption_power() * (self.env.step_size / 3600.0)

    def simulate_consumption(self):
        # calculate variation using daily demand
        self.target_temperature = self.daily_demand[
            time.gmtime(self.env.now).tm_hour]

        self.room_power = self.current_power - self.heat_loss()
        self.calculate_room_temperature()

        # the heating powers to full capacity in 10 min
        slope = self.max_power * (self.env.step_size / (60 * 10.0))
        if self.temperature_room > self.target_temperature:
            self.current_power -= slope
        else:
            self.current_power += slope

        # clamp to maximum power
        self.current_power = max(min(self.current_power, self.max_power), 0.0)

    def heat_loss(self):
        heat_loss = 0
        d = self.temperature_room - self.get_outside_temperature()
        # heat transfer coefficient normal glas window, W/(m^2 * K)
        k_window = 5.9
        # in Watt
        heat_flow_window = self.window_surface * k_window * d
        heat_loss += heat_flow_window

        # semi good isolated wall
        k_wall = 0.5
        layers = 10
        layer_depth = 0.1
        capacity = (layer_depth / k_wall) * layers
        heat_flow_wall = self.outer_wall_surface / capacity * d
        heat_loss += heat_flow_wall

        return heat_loss

    def get_outside_temperature(self, offset_days=0):
        return self.weather_forecast.get_temperature_estimate(self.env.now)

    def linear_interpolation(self, a, b, x):
        return a * (1 - x) + b * x


class SimpleElectricalConsumer(BaseSystem):

    """
    Demand based on pamiru's data (22 residents in a 12 apartment house)

    env - simpy simulation environment
    power_meter - PowerMeter
    residents - house residents
    """

    def __init__(self, env, residents=22):
        super(SimpleElectricalConsumer, self).__init__(env)

        self.power_meter = power_meter
        self.residents = residents
        self.total_consumption = 0.0  # kWh

        # list of 24 values representing relative demand per hour
        self.demand_variation = [1 for i in range(24)]

    def connected(self):
        return self.power_meter is not None

    @classmethod
    def copyconstruct(cls, env, other_electrical_consumer, power_meter):
        electrical_consumer = SimpleElectricalConsumer(env, power_meter)
        # just a shallow copy, so no dict copy
        electrical_consumer.__dict__ = other_electrical_consumer.__dict__.copy(
        )
        electrical_consumer.power_meter = power_meter
        electrical_consumer.env = env
        return electrical_consumer

    def step(self):
        consumption = self.get_consumption_energy()
        self.total_consumption += consumption
        self.power_meter.consume_energy(consumption)
        self.power_meter.current_power_consum = self.get_consumption_power()

    def get_consumption_power(self):
        time_tuple = time.gmtime(self.env.now)
        quarter = int(time_tuple.tm_min / 15.0)
        quarters = (time_tuple.tm_hour * 4 + quarter) % (4 * 24)
        # week days 0-6 converted to 1-7
        wday = time_tuple.tm_wday + 1
        interpolation = interpolate_year(time_tuple.tm_yday)
        summer_part =  (1 - interpolation) * \
            weekly_electrical_demand_summer[quarters * wday]
        winter_part = interpolation * \
            weekly_electrical_demand_winter[quarters * wday]
        demand = summer_part + winter_part
        # data based on 22 residents
        demand = demand / 22 * self.residents
        # calculate variation using demand and variation
        return demand * self.demand_variation[time_tuple.tm_hour]

    def get_consumption_energy(self):
        return self.get_consumption_power() * (self.env.step_size / 3600.0)
