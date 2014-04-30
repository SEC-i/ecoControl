import time

from systems import BaseSystem
from systems.helpers import interpolate_year
from systems.data import weekly_electrical_demand_winter, weekly_electrical_demand_summer, warm_water_demand_workday, warm_water_demand_weekend
from forecasting.weather import WeatherForecast


class ThermalConsumer(BaseSystem):

    """
    physically based heating, using formulas from 
    http://www.model.in.tum.de/um/research/groups/ai/fki-berichte/postscript/fki-227-98.pdf and
    http://www.inference.phy.cam.ac.uk/is/papers/DanThermalModellingBuildings.pdf 
    house data from pamiru48 (12 apartments with 22 persons)

    total_heated_floor - area of simulated house in square meter (650)
    residents - number of residents (22)
    apartments - number of apartments (12)
    avg_rooms_per_appartment - average room number (4)
    average_window_per_room, each window 2 m^2(3)
    heating_constant - heating demand per square meter in W (rule of thumb for new housing: 100)
    """

    def __init__(self, env, heat_storage):

        super(ThermalConsumer, self).__init__(env)

        self.heat_storage = heat_storage

        self.total_consumption = 0.0
        # initial temperature
        self.temperature_room = 12.0
        self.temperature_warmwater = 40.0

        # list of 24 values representing target_temperature per hour
        self.daily_demand = [19, 19, 19, 19, 19, 19, 19, 20, 21,
                             20, 20, 21, 20, 21, 21, 21, 21, 22, 22, 22, 22, 22, 21, 19]
        self.target_temperature = self.daily_demand[0]

        self.total_heated_floor = 650
        self.room_height = 2.5 # constant
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
        self.weather_forecast = WeatherForecast(self.env)

        self.calculate()

    def calculate(self):

        self.total_heated_volume = self.total_heated_floor * self.room_height
        self.avg_room_volume = self.total_heated_volume / \
            (self.apartments * self.avg_rooms_per_apartment)
        # Assume 3 walls per room to not count multiple
        avg_wall_size = self.avg_room_volume / self.room_height * 3
        # Assume each appartment have an average of 0.8 outer walls per apartment
        self.outer_wall_surface = avg_wall_size * self.apartments * 0.8
        self.max_power = self.total_heated_floor * \
            float(self.heating_constant)

        self.current_power = 0
        # Assume a window size of 2 square meters
        self.window_surface = 2 * self.avg_windows_per_room * \
            self.avg_rooms_per_apartment * self.apartments

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

    def heat_room(self):
        # Convert from J/(m^3 * K) to kWh/(m^3 * K)
        specific_heat_capacity_air = 1000.0 / 3600.0
        room_power = self.get_consumption_power() - self.heat_loss_power()
        room_energy = room_power * (self.env.step_size / self.env.measurement_interval)
        temp_delta = room_energy / (self.avg_room_volume *  specific_heat_capacity_air)
        self.temperature_room += temp_delta

    def get_consumption_power(self):
        # convert to kW
        return self.current_power / 1000.0

    def get_consumption_energy(self):
        # convert to kWh
        return self.get_consumption_power() * (self.env.step_size / self.env.measurement_interval)

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
        return self.get_warmwater_consumption_power() * (self.env.step_size / self.env.measurement_interval)

    def simulate_consumption(self):
        # Calculate variation using daily demand
        self.target_temperature = self.daily_demand[
            time.gmtime(self.env.now).tm_hour]

        self.heat_room()

        # The heating powers to full capacity in 60 min
        slope = self.max_power * (self.env.step_size / (60 * 60.0))
        if self.temperature_room > self.target_temperature:
            self.current_power -= slope
        else:
            self.current_power += slope

        # Clamp to maximum power
        self.current_power = max(min(self.current_power, self.max_power), 0.0)

    def heat_loss_power(self):
        temp_delta = self.temperature_room - self.get_outside_temperature()
        heat_flow_window = self.window_surface * \
            self.heat_transfer_window * temp_delta
        heat_flow_wall = self.outer_wall_surface * \
            self.heat_transfer_wall * temp_delta
        return (heat_flow_wall + heat_flow_window) / 1000.0 # kW

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

    def __init__(self, env, power_meter, residents=22):
        super(SimpleElectricalConsumer, self).__init__(env)

        self.power_meter = power_meter
        self.residents = residents
        self.total_consumption = 0.0  # kWh

        # list of 24 values representing relative demand per hour
        self.demand_variation = [1 for i in range(24)]

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
        return self.get_consumption_power() * (self.env.step_size / self.env.measurement_interval)
