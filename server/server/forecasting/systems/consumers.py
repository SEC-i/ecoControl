import time
from data import outside_temperatures_2013, daily_electrical_demand, warm_water_demand_workday, warm_water_demand_weekend
from basesystem import BaseSystem


class ThermalConsumer(BaseSystem):

    """ physically based heating, using formulas from 
    http://www.model.in.tum.de/um/research/groups/ai/fki-berichte/postscript/fki-227-98.pdf and
    http://www.inference.phy.cam.ac.uk/is/papers/DanThermalModellingBuildings.pdf """

    def __init__(self, env, heat_storage):
        super(ThermalConsumer, self).__init__(env)

        self.heat_storage = heat_storage

        self.target_temperature = 20.0
        self.total_consumption = 0.0
        self.temperature_room = 12.0
        self.temperature_warmwater = 40.0

        # list of 24 values representing  target_temperature per hour

        self.daily_demand = [19, 19, 19, 19, 19, 19, 19, 20, 21,
                             20, 20, 21, 20, 21, 21, 21, 21, 22, 22, 22, 22, 22, 21, 19]

        # data from pamiru48
        # has 12 apartments with 22 persons
        self.total_heated_floor = 650.0  # m^2
        self.residents = 22
        # 2.5m high walls
        self.total_heated_volume = self.total_heated_floor * 2.5
        appartments = 12
        avg_rooms_per_appartment = 4
        avg_room_volume = self.total_heated_volume / \
            (appartments * avg_rooms_per_appartment)
        # avg surface of a cube side, so multiply with 6 to get the whole
        # surface
        avg_wall_size = avg_room_volume ** (2.0 / 3.0)  # m^2
        # lets have each appartment have an average of 1.5 outer walls
        self.outer_wall_surface = avg_wall_size * appartments * 1.5
        # assume 100W heating demand per m^2, rule of thumb for new housings
        self.max_power = self.total_heated_floor * 100.0  # W

        self.current_power = 0
        # m^2, avg per room, avg rooms per appartments, appartments
        self.window_surface = 4 * 4 * 12

        specific_heat_capacity_brick = 1360 * 10 ** 6  # J/(m^3 * K)
        # J / K, approximation for 5 walls including ceiling, 0.36m wall
        # thickness,
        heat_cap_brick_per_room = specific_heat_capacity_brick * \
            (avg_wall_size * 5 * 0.36)
        # avg rooms per appartent,number of appartments
        self.heat_cap_brick = heat_cap_brick_per_room * 4 * 12

        #J /( m^3 * K)
        self.specific_heat_capacity_air = 1290.0
        self.heat_capacity_air = self.specific_heat_capacity_air * \
            self.total_heated_volume

        # object factor--> we have some objects, which slow down heating and cooling
        #--> used to make heating and cooling look realistic ;)
        stuff_weight = self.total_heated_volume * 50.0  # assume 50.0 kilo per m^3 of heatable objects (wood)
        heat_capacity_stuff = stuff_weight * 600.0  # 600 = spec heat cap wood

        self.heat_capacity = self.heat_capacity_air + heat_capacity_stuff

        self.room_power = self.heat_capacity_air * self.temperature_room

    @classmethod
    def copyconstruct(cls, env, other_thermal_consumer, heat_storage):
        thermal_consumer = ThermalConsumer(env,heat_storage)
        thermal_consumer.__dict__ = other_thermal_consumer.__dict__.copy()    # just a shallow copy, so no dict copy
        return thermal_consumer



    def step(self):
        self.simulate_consumption()
        consumption = self.get_consumption_energy(
        ) + self.get_warmwater_consumption_energy()
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
        if wday in [5, 6]: #weekend
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
        self.target_temperature = self.daily_demand[time.gmtime(self.env.now).tm_hour]

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
        day = (time.gmtime(self.env.now).tm_yday + offset_days) % 365
        hour = time.gmtime(self.env.now).tm_hour
        return outside_temperatures_2013[day * 24 + hour]


    def linear_interpolation(self, a, b, x):
        return a * (1 - x) + b * x


class SimpleElectricalConsumer(BaseSystem):

    def __init__(self, env, power_meter):
        super(SimpleElectricalConsumer, self).__init__(env)

        self.power_meter = power_meter

        self.total_consumption = 0.0  # kWh

        # list of 24 values representing relative demand per hour
        self.demand_variation = [1 for i in range(24)]

    @classmethod
    def copyconstruct(cls, env, other_electrical_consumer, power_meter):
        electrical_consumer = SimpleElectricalConsumer(env, power_meter)
        electrical_consumer.__dict__ = other_electrical_consumer.__dict__.copy()    # just a shallow copy, so no dict copy
        electrical_consumer.power_meter = power_meter 
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
        # calculate variation using daily demand and variation
        return daily_electrical_demand[quarters] * self.demand_variation[time_tuple.tm_hour]

    def get_consumption_energy(self):
        return self.get_consumption_power() * (self.env.step_size / 3600.0)
