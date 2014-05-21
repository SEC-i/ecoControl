import time
from datetime import datetime
import os
from django.utils.timezone import utc

from helpers import BaseSystem, interpolate_year
from data import weekly_electrical_demand_winter, weekly_electrical_demand_summer, warm_water_demand_workday, warm_water_demand_weekend
from server.forecasting.forecasting.weather import WeatherForecast
from server.forecasting.forecasting import Forecast
from server.forecasting.forecasting.dataloader import DataLoader
from server.forecasting.forecasting.helpers import approximate_index


electrical_forecast = None
weather_forecast = None


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

    def __init__(self, system_id, env):

        super(ThermalConsumer, self).__init__(system_id, env)

        self.heat_storage = None

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
        
        global weather_forecast
        if weather_forecast == None:
            weather_forecast = WeatherForecast(self.env)
        self.weather_forecast = weather_forecast



        input_data = warm_water_demand_workday + warm_water_demand_weekend
        #only build once, to save lots of time
        #self.warmwater_forecast = Forecast(self.env, input_data, samples_per_hour=1)
            

        self.calculate()

    def find_dependent_devices_in(self, system_list):
        for system in system_list:
            system.attach_to_thermal_consumer(self)

    def connected(self):
        return self.heat_storage is not None

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
        room_energy = room_power * (self.env.step_size / 3600.0)
        temp_delta = room_energy / (self.avg_room_volume *  specific_heat_capacity_air)
        self.temperature_room += temp_delta

    def get_consumption_power(self):
        # convert to kW
        return self.current_power / 1000.0

    def get_consumption_energy(self):
        # convert to kWh
        return self.get_consumption_power() * (self.env.step_size / 3600.0)

    def get_warmwater_consumption_power(self):
        #demand_liters_per_hour = self.warmwater_forecast.get_forecast_at(self.env.now)
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
        date = datetime.fromtimestamp(self.env.now)
        date_aware = date.replace(tzinfo=utc)
        return self.weather_forecast.get_temperature_estimate(date_aware)

    def linear_interpolation(self, a, b, x):
        return a * (1 - x) + b * x


class ElectricalConsumer(BaseSystem):

    """
    Demand based on pamiru's data (22 residents in a 12 apartment house)

    env - simpy simulation environment
    power_meter - PowerMeter
    residents - house residents
    """


    def __init__(self, system_id, env, residents=22):
        super(ElectricalConsumer, self).__init__(system_id, env)

        self.power_meter = None
        self.residents = residents
        self.total_consumption = 0.0  # kWh
        ##! TODO: this will have to replaced by a database"
        global electrical_forecast
        if electrical_forecast == None:
            raw_dataset = self.get_data_until(self.env.now)
            #cast to float and convert to kW
            dataset = [float(val) / 1000.0 for val in raw_dataset]
            electrical_forecast = Forecast(self.env, dataset, samples_per_hour=1)
        self.electrical_forecast = electrical_forecast

        # list of 24 values representing relative demand per hour
        self.demand_variation = [1 for i in range(24)]
        
        self.new_data_interval = 24 * 60 * 60 #append data each day
        self.last_forecast_update = self.env.now


    def find_dependent_devices_in(self, system_list):
        for system in system_list:
            system.attach_to_electrical_consumer(self)

    def connected(self):
        return self.power_meter is not None


    def step(self):
        consumption = self.get_consumption_energy()
        self.total_consumption += consumption
        self.power_meter.consume_energy(consumption)
        self.power_meter.current_power_consum = self.get_consumption_power()
        ##copyconstructed means its running a forecasting
        if self.env.demo and self.env.now - self.last_forecast_update > self.new_data_interval:
                self.update_forecast_data()
        
    def update_forecast_data(self):
        
        raw_dataset = self.get_data_until(self.env.now, self.last_forecast_update)
        #cast to float and convert to kW
        dataset = [float(val) / 1000.0 for val in raw_dataset]
        self.electrical_forecast.append_values(dataset)
        self.last_forecast_update = self.env.now
        

    def get_consumption_power(self):
        time_tuple = time.gmtime(self.env.now)
        demand = self.electrical_forecast.get_forecast_at(self.env.now)
        #demand = 1
        # calculate variation using demand and variation
        return demand * self.demand_variation[time_tuple.tm_hour]

    def get_consumption_energy(self):
        return self.get_consumption_power() * (self.env.step_size / 3600.0)
    
    def get_data_until(self, timestamp, start_timestamp=None):
        #! TODO: reading data from csv will have to be replaced by live/fake data from database
        date = datetime.fromtimestamp(timestamp)
        path = os.path.join(os.path.realpath('server'), "forecasting/tools/Electricity_2013.csv")
        raw_dataset = DataLoader.load_from_file(path, "Strom - Verbrauchertotal (Aktuell)", "\t")
        dates = DataLoader.load_from_file(path, "Datum", "\t")
        
        if date.year == 2014: 
            path = os.path.join(os.path.realpath('server'), "forecasting/tools/Electricity_until_may_2014.csv") 
            raw_dataset += DataLoader.load_from_file(path, "Strom - Verbrauchertotal (Aktuell)", "\t")
            dates += DataLoader.load_from_file(path, "Datum", "\t")

        dates = [int(date) for date in dates]
        now_index = approximate_index(dates, self.env.now)
        
        #take data until simulated now time
        if start_timestamp == None:
            return raw_dataset[:now_index]
        else:
            start_index = approximate_index(dates, start_timestamp)
            return raw_dataset[start_index:now_index]
