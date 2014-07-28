import time
from datetime import datetime
import os
import cProfile

from django.utils.timezone import utc

from server.devices.consumers import ThermalConsumer, ElectricalConsumer
from server.forecasting.devices.data.old_demands import warm_water_demand_workday, warm_water_demand_weekend
from server.forecasting.forecasting.weather import get_temperature
from server.forecasting.forecasting import StatisticalForecast, DayTypeForecast,\
    DSHWForecast
from server.forecasting.forecasting.dataloader import DataLoader
from server.forecasting.forecasting.helpers import approximate_index
from server.settings import BASE_DIR


electrical_forecast = None
all_data = None

class SimulatedThermalConsumer(ThermalConsumer):

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

    def __init__(self, device_id, env):

        super(SimulatedThermalConsumer, self).__init__(device_id, env)

        # list of 24 values representing target_temperature per hour
        self.daily_demand = [19, 19, 19, 19, 19, 19, 19, 20, 21,
                             20, 20, 21, 20, 21, 21, 21, 21, 22, 22, 22, 22, 22, 21, 19]
        self.config['target_temperature'] = self.daily_demand[0]

        self.total_consumed = 0

        self.current_power = 0

        # only build once, to save lots of time
        #self.warmwater_forecast = StatisticalForecast(self.env, input_data, samples_per_hour=1)

        self.calculate()

    def calculate(self):

        self.current_power = 0
        self.total_heated_volume = self.config['total_heated_floor'] * self.room_height
        self.config['avg_room_volume'] = self.total_heated_volume / \
            (self.config['apartments'] * self.config['avg_rooms_per_apartment'])
        # Assume 3 walls per room to not count multiple
        avg_wall_size = self.config['avg_room_volume'] / self.room_height * 3
        # Assume each appartment have an average of 0.8 outer walls per
        # apartment
        self.outer_wall_surface = avg_wall_size * self.config['apartments'] * 0.8
        self.max_power = self.config['total_heated_floor'] * \
            float(self.heating_constant)

        # Assume a window size of 2 square meters
        self.window_surface = 2 * self.config['avg_windows_per_room'] * \
            self.config['avg_rooms_per_apartment'] * self.config['apartments']

    def step(self):
        self.simulate_consumption()
        consumption = self.get_consumption_energy(
        ) + self.get_warmwater_consumption_energy()
        self.total_consumed += consumption
        self.heat_storage.consume_energy(consumption)

    def heat_room(self):
        # Convert from J/(m^3 * K) to kWh/(m^3 * K)
        specific_heat_capacity_air = 1000.0 / 3600.0
        room_power = self.get_consumption_power() - self.heat_loss_power()
        room_energy = room_power * (self.env.step_size / 3600.0)
        temp_delta = room_energy / \
            (self.config['avg_room_volume'] * specific_heat_capacity_air)
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
            (self.temperature_warmwater - self.heat_storage.config['base_temperature']) * \
            specific_heat_capacity_water
        return power_demand * self.config['residents']

    def get_warmwater_consumption_energy(self):
        return self.get_warmwater_consumption_power() * (self.env.step_size / 3600.0)

    def simulate_consumption(self):
        # Calculate variation using daily demand
        hours = datetime.fromtimestamp(self.env.now).replace(tzinfo=utc).hour
        self.config['target_temperature'] = self.daily_demand[hours]

        self.heat_room()

        # The heating powers to full capacity in 60 min
        slope = self.max_power * (self.env.step_size / (60 * 60.0))
        if self.temperature_room > self.config['target_temperature']:
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
        return (heat_flow_wall + heat_flow_window) / 1000.0  # kW

    def get_outside_temperature(self):
        date = datetime.fromtimestamp(self.env.now).replace(tzinfo=utc)
        
        return float(get_temperature(self.env, date))

    def linear_interpolation(self, a, b, x):
        return a * (1 - x) + b * x


class SimulatedElectricalConsumer(ElectricalConsumer):

    """
    Demand based on pamiru's data (22 residents in a 12 apartment house)

    env - simulation environment
    power_meter - PowerMeter
    residents - house residents
    """
    dataset = []
    dates = []

    def __init__(self, device_id, env):
        super(SimulatedElectricalConsumer, self).__init__(device_id, env)

        self.power_meter = None
        self.total_consumption = 0.0  # kWh

        global electrical_forecast
        if electrical_forecast == None and not env.is_demo_simulation():
            # ! TODO: this will have to replaced by a database"
            raw_dataset = self.get_data_until(self.env.now)
            # cast to float and convert to kW
            dataset = [float(val) / 1000.0 for val in raw_dataset]
            hourly_data = StatisticalForecast.make_hourly(dataset, 6)
            electrical_forecast = DSHWForecast(
                self.env, hourly_data, samples_per_hour=1)
        self.electrical_forecast = electrical_forecast

        self.new_data_interval = 24 * 60 * 60  # append data each day
        self.last_forecast_update = self.env.now
        
        #if self.env.demo_mode or not self.env.forecast:
        #    self.all_data = self.get_all_data2014()
        global all_data
        if all_data == None:
            all_data = self.get_all_data2014()

    def step(self):
        consumption = self.get_consumption_energy()
        self.total_consumption += consumption
        self.power_meter.consume_energy(consumption)
        self.power_meter.current_power_consum = self.get_consumption_power()
        # if this is not a forecast consumer, update the statistical forecasting periodically
        if self.env.is_demo_simulation() and self.env.now - self.last_forecast_update > self.new_data_interval:
            self.update_forecast_data()
            
    def get_all_data2014(self):
        sep = os.path.sep
        path = os.path.join(BASE_DIR, "server" + sep +  "forecasting" + sep + "demodata" +sep+ "demo_electricity_2014.csv")
        raw_dataset = DataLoader.load_from_file(
            path, "Strom - Verbrauchertotal (Aktuell)", "\t")
        dates = DataLoader.load_from_file(path, "Datum", "\t")
        dates = [int(date) for date in dates]
        raw_dataset = [float(val) / 1000.0 for val in raw_dataset]
        return {"dates" : dates, "dataset" : raw_dataset}

    def update_forecast_data(self):
        raw_dataset = self.get_data_until(
            self.env.now, self.last_forecast_update)
        # cast to float and convert to kW
        dataset = [float(val) / 1000.0 for val in raw_dataset]
        self.electrical_forecast.append_values(dataset)
        self.last_forecast_update = self.env.now

    def get_consumption_power(self):
        time_tuple = time.gmtime(self.env.now)
        
        
        date_index = approximate_index(all_data["dates"], self.env.now)

        if self.env.forecast:
            return self.electrical_forecast.get_forecast_at(self.env.now)
        else:
            date_index = approximate_index(all_data["dates"], self.env.now)
            return float(all_data["dataset"][date_index])
            

    def get_consumption_energy(self):
        return self.get_consumption_power() * (self.env.step_size / 3600.0)

    def get_data_until(self, timestamp, start_timestamp=None):
        #! TODO: reading data from csv will have to be replaced by live/fake data from database
        date = datetime.utcfromtimestamp(timestamp).replace(tzinfo=utc)
        if self.__class__.dataset == [] or self.__class__.dates == []:
            sep = os.path.sep
            path = os.path.join(BASE_DIR, "server" + sep + "forecasting" + sep + "demodata" +sep+ "demo_electricity_2013.csv")
            raw_dataset = DataLoader.load_from_file(
                path, "Strom - Verbrauchertotal (Aktuell)", "\t")
            dates = DataLoader.load_from_file(path, "Datum", "\t")

            if date.year == 2014:
                path = os.path.join(BASE_DIR, "server" + sep + "forecasting" + sep + "demodata" + sep+"demo_electricity_2014.csv")
                raw_dataset += DataLoader.load_from_file(
                    path, "Strom - Verbrauchertotal (Aktuell)", "\t")
                dates += DataLoader.load_from_file(path, "Datum", "\t")

            self.__class__.dates = [int(date) for date in dates]
            self.__class__.dataset = raw_dataset

        dates = self.__class__.dates
        dataset = self.__class__.dataset

        now_index = approximate_index(dates, self.env.now)

        # take data until simulated now time
        if start_timestamp == None:
            return dataset[:now_index]
        else:
            start_index = approximate_index(dates, start_timestamp)
            return dataset[start_index:now_index]
