import os
from time import gmtime
from datetime import datetime
from django.utils.timezone import utc


from server.devices.consumers import ThermalConsumer, ElectricalConsumer
from server.forecasting.simulation.demodata.old_demands import warm_water_demand_workday, warm_water_demand_weekend
from server.forecasting.weather import get_temperature
from server.forecasting.statistical import StatisticalForecast, DayTypeForecast,\
    DSHWForecast
from server.forecasting.dataloader import DataLoader
from server.forecasting.helpers import approximate_index, linear_interpolation
from server.settings import BASE_DIR


electrical_forecast = None
all_data = None

sep = os.path.sep
DATA_PATH = BASE_DIR + sep + "server" + sep + "forecasting" + sep + "simulation" + sep + "demodata"

class SimulatedThermalConsumer(ThermalConsumer):
    """The simulation of the thermal consume (heating and warm water) of a house

    Usied formulas from
    http://www.model.in.tum.de/um/research/groups/ai/fki-berichte/postscript/fki-227-98.pdf and
    http://www.inference.phy.cam.ac.uk/is/papers/DanThermalModellingBuildings.pdf
    """

    def __init__(self, device_id, env):

        super(SimulatedThermalConsumer, self).__init__(device_id, env)

        self.total_consumed = 0

        # only build once, to save lots of time
        #self.warmwater_forecast = StatisticalForecast(self.env, input_data, samples_per_hour=1)

        self.calculate()

    def calculate(self):
        """Update the heating parameters when a house parameter is changed.
        Therefore some assumptions are made"""
        self.current_power = 0
        self.total_heated_volume = self.config['total_heated_floor'] * self.room_height
        self.config['avg_room_volume'] = self.total_heated_volume / \
            (self.config['apartments'] * self.config['avg_rooms_per_apartment'])
        #: Assume 3 walls per room to not count multiple
        avg_wall_size = self.config['avg_room_volume'] / self.room_height * 3
        #: Assume each apartment have an average of 0.8 outer walls
        self.outer_wall_surface = avg_wall_size * self.config['apartments'] * 0.8
        self.max_power = self.config['total_heated_floor'] * \
            float(self.heating_constant)
        #: Assume a size of 2 square meters per singel window
        self.window_surface = 2 * self.config['avg_windows_per_room'] * \
            self.config['avg_rooms_per_apartment'] * self.config['apartments']

    def step(self):
        """Simulate the heating and consume according energy"""
        self.simulate_consumption()
        consumption = self.get_consumption_energy(
        ) + self.get_warmwater_consumption_energy()
        self.total_consumed += consumption
        self.heat_storage.consume_energy(consumption)

    def simulate_consumption(self):
        """Determine the heating power of the whole house considerung the rooms target temperature.
        """
        hours = datetime.fromtimestamp(self.env.now).replace(tzinfo=utc).hour
        self.config['target_temperature'] = self.daily_demand[hours]

        self.heat_apartments()

        #: The heating powers to full capacity in 60 min
        slope = self.max_power * (self.env.step_size / (60 * 60.0))
        if self.temperature_room > self.config['target_temperature']:
            self.current_power -= slope
        else:
            self.current_power += slope

        # Clamp to maximum power
        self.current_power = max(min(self.current_power, self.max_power), 0.0)

    def get_consumption_energy(self):
        """Returns consumed thermal energy for heating in kWh during current time-step"""
        return self.get_consumption_power() * (self.env.step_size / 3600.0)

    def heat_apartments(self):
        """Increases the rooms temperature.
        With the current heating power an amount of energy for the current time-step is produced.
        This energy and the specific heat capacity of air (1000 J/(m^3 * K)) is needed for the temperature calculation."""
        # Convert from J/(m^3 * K) to kWh/(m^3 * K)
        specific_heat_capacity_air = 1000.0 / 3600.0
        room_power = self.get_consumption_power() - self.heat_loss_power()
        room_energy = room_power * (self.env.step_size / 3600.0)
        temp_delta = room_energy / \
            (self.config['avg_room_volume'] * specific_heat_capacity_air)
        self.temperature_room += temp_delta

    def heat_loss_power(self):
        """Returns the power in kW by with the house loses thermal energy at outer walls and windows.
        The outside temperature is needed for the temperature difference."""
        temp_delta = self.temperature_room - self.get_outside_temperature()
        heat_flow_window = self.window_surface * \
            self.heat_transfer_window * temp_delta
        heat_flow_wall = self.outer_wall_surface * \
            self.heat_transfer_wall * temp_delta
        return (heat_flow_wall + heat_flow_window) / 1000.0

    def get_outside_temperature(self):
        """The thermal energy demand depends on the outside temperature.
        For the current simulated time (self.env.now) the outside temperature is returned.
        """
        date = datetime.fromtimestamp(self.env.now).replace(tzinfo=utc)
        return float(get_temperature(self.env, date))

    def get_warmwater_consumption_power(self):
        """The energy needed for warm water is calculated by the amount of needed liters in average.
        For the time step the power is calculated which could heat the needed water of all residents to the given temperature
        (40 degrees Celsius default)."""
        #demand_liters_per_hour = self.warmwater_forecast.get_forecast_at(self.env.now)
        #: specific heat capacity water set to 0.001163708 kWh/(kg*K)
        specific_heat_capacity_water = 0.001163708
        time_tuple = gmtime(self.env.now)

        hour = time_tuple.tm_hour
        wday = time_tuple.tm_wday
        weight = time_tuple.tm_min / 60.0
        if wday in [5, 6]:  # weekend
            demand_liters_per_hour = linear_interpolation(
                warm_water_demand_weekend[hour],
                warm_water_demand_weekend[(hour + 1) % 24], weight)
        else:
            demand_liters_per_hour = linear_interpolation(
                warm_water_demand_workday[hour],
                warm_water_demand_workday[(hour + 1) % 24], weight)

        power_demand = demand_liters_per_hour * \
            (self.temperature_warmwater - self.heat_storage.base_temperature) * \
            specific_heat_capacity_water
        return power_demand * self.config['residents']

    def get_warmwater_consumption_energy(self):
        """Returns needed thermal energy for warm water in kWh during current time-step"""
        return self.get_warmwater_consumption_power() * (self.env.step_size / 3600.0)


class SimulatedElectricalConsumer(ElectricalConsumer):
    """The simulation of the electrical consume of a house based on forecasting."""
    dataset = []
    dates = []

    def __init__(self, device_id, env):
        super(SimulatedElectricalConsumer, self).__init__(device_id, env)

        # ! TODO: this will have to replaced by a database"
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

        # cache the forecast for better performance
        self.start_timestamp = self.env.initial_date
        global all_data
        if all_data == None:
            all_data = self.get_all_data2014()

    def step(self):
        """Calculate the current power and consume according energy for current time-step."""
        consumption = self.get_consumption_energy()
        self.total_consumption += consumption
        self.power_meter.consume_energy(consumption)
        self.power_meter.current_power_consum = self.get_consumption_power()
        if not self.env.is_demo_simulation() and \
            self.start_timestamp - self.last_forecast_update > self.new_data_interval:
            self.update_forecast_data()

    def get_all_data2014(self):
        sep = os.path.sep
        path = DATA_PATH + sep + "demo_electricity_2014.csv"
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
        """Use the forecast to determine the current power demand"""
        time_tuple = gmtime(self.env.now)
        date_index = approximate_index(all_data["dates"], self.env.now)

        if self.env.forecast:
            return self.electrical_forecast.get_forecast_at(self.env.now)
        else:
            date_index = approximate_index(all_data["dates"], self.env.now)
            return float(all_data["dataset"][date_index])

    def get_consumption_energy(self):
        """Returns needed electrical energy in kWh during current time-step"""
        return self.get_consumption_power() * (self.env.step_size / 3600.0)

    def get_data_until(self, timestamp, start_timestamp=None):
        date = datetime.utcfromtimestamp(timestamp).replace(tzinfo=utc)

        if self.__class__.dataset == [] or self.__class__.dates == []:
            path = DATA_PATH +sep+ "demo_electricity_2012.csv"
            raw_dataset = DataLoader.load_from_file(
                path, "Strom - Verbrauchertotal (Aktuell)", "\t")
            dates = DataLoader.load_from_file(path, "Datum", "\t")

            path = DATA_PATH + sep+ "demo_electricity_2013.csv"
            raw_dataset += DataLoader.load_from_file(
                path, "Strom - Verbrauchertotal (Aktuell)", "\t")
            dates += DataLoader.load_from_file(path, "Datum", "\t")

            if date.year == 2014:
                path = DATA_PATH + sep +"demo_electricity_2014.csv"
                raw_dataset += DataLoader.load_from_file(
                    path, "Strom - Verbrauchertotal (Aktuell)", "\t")
                dates += DataLoader.load_from_file(path, "Datum", "\t")

            self.__class__.dates = [int(date) for date in dates]
            self.__class__.dataset = raw_dataset

        dates = self.__class__.dates
        dataset = self.__class__.dataset

        now_index = approximate_index(dates, timestamp)

        # take data until simulated now time
        if start_timestamp == None:
            return dataset[:now_index]
        else:
            start_index = approximate_index(dates, start_timestamp)
            return dataset[start_index:now_index]