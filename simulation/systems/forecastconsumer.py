from consumers import ThermalConsumer
from forecasting.weatherforecast import Forecast


class ForecastConsumer(ThermalConsumer):

    def __init__(self, env, heatstorage):
        ThermalConsumer.__init__(self, env, heatstorage)
        self.env = env
        self.heat_storage = heatstorage
        # consumption since last meausrement
        self.consumed = 0

        self.weather_forecast = Forecast(self.env)

    @classmethod
    def copyconstruct(cls, env, other_forecast_consumer, heat_storage):
        forecast_consumer = ForecastConsumer(env,heat_storage)
        forecast_consumer.__dict__ = other_forecast_consumer.__dict__.copy()    # just a shallow copy, so no dict copy
        forecast_consumer.heat_storage = heat_storage
        forecast_consumer.env = env
        return forecast_consumer



    def step(self):
        self.simulate_consumption()
        consumption = self.get_consumption_energy() + self.get_warmwater_consumption_energy()
        self.consumed += consumption
        self.total_consumption += consumption
        self.heat_storage.consume_energy(consumption)

    def get_outside_temperature(self):
        return self.weather_forecast.get_temperature_estimate(self.env.now)

    