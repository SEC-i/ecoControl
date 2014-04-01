import time

import simpy
from simpy.util import start_delayed

from environment import ForwardableRealtimeEnvironment

from systems.code import CodeExecuter
from systems.producers import CogenerationUnit, PeakLoadBoiler
from systems.storages import HeatStorage, PowerMeter
from systems.consumers import ThermalConsumer, SimpleElectricalConsumer
from systems.forecastconsumer import ForecastConsumer

from helpers import BulkProcessor, SimulationBackgroundRunner


class Simulation(object):
    def __init__(self,copyconstructed=False):

        if copyconstructed:
            return
         # initialize real-time environment
        self.env = ForwardableRealtimeEnvironment()

        # initialize power systems
        self.heat_storage = HeatStorage(self.env)
        self.power_meter = PowerMeter(self.env)
        self.cu = CogenerationUnit(self.env, self.heat_storage, self.power_meter)
        self.plb = PeakLoadBoiler(self.env, self.heat_storage)
        self.thermal_consumer = ForecastConsumer(self.env, self.heat_storage)
        self.electrical_consumer = SimpleElectricalConsumer(self.env, self.power_meter)

        # initilize code executer
        self.code_executer = CodeExecuter(self.env, {
            'env': self.env,
            'heat_storage': self.heat_storage,
            'power_meter': self.power_meter,
            'cu': self.cu,
            'plb': self.plb,
            'thermal_consumer': self.thermal_consumer,
            'electrical_consumer': self.electrical_consumer,
            'time': time,
        })

        # initialize BulkProcessor and add it to env
        self.bulk_processor = BulkProcessor(
            self.env, [self.code_executer, self.cu, self.plb, self.heat_storage, self.thermal_consumer, self.electrical_consumer])
        self.env.process(self.bulk_processor.loop())

    @classmethod
    def copyconstruct(cls, otherSimulation):
        simulation = Simulation()
        simulation.env = ForwardableRealtimeEnvironment(otherSimulation.env.initial_time,otherSimulation.env.measurement_interval)
        simulation.env.env_start = otherSimulation.env.env_start
        simulation.heat_storage = HeatStorage.copyconstruct(simulation.env, otherSimulation.heat_storage)



        thread = SimulationBackgroundRunner(simulation.env)
        thread.start()

        return simulation



    def get_systems(self):
        return (self.env, self.heat_storage, self.power_meter, self.cu, self.plb,
            self.thermal_consumer, self.electrical_consumer, self.code_executer)

    def forward(self, seconds):
        self.env.forward = seconds
