from consumers import ThermalConsumer


class ForecastConsumer(ThermalConsumer):

    def __init__(self, env, heatstorage):
        ThermalConsumer.__init__(self, env, heatstorage)
        self.env = env
        #consumption since last meausrement
        self.consumed = 0

    def step(self):
        self.simulate_consumption()
        consumption = self.get_consumption_energy() + self.get_warmwater_consumption_energy()
        self.consumed += consumption
        self.total_consumption += consumption
        self.heat_storage.consume_energy(consumption)

    def get_outside_temperature(self):
        return self.weather_forecast.get_temperature_estimate(self.env.now)
