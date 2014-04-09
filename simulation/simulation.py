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
    def __init__(self,initial_time=1356998400,copyconstructed=False):

        if copyconstructed:
            return
         # initialize real-time environment
        self.env = ForwardableRealtimeEnvironment(initial_time=initial_time)

        # initialize power systems
        self.heat_storage = HeatStorage(self.env)
        self.power_meter = PowerMeter(self.env)
        self.cu = CogenerationUnit(self.env, self.heat_storage, self.power_meter)
        self.plb = PeakLoadBoiler(self.env, self.heat_storage)
        self.thermal_consumer = ForecastConsumer(self.env, self.heat_storage)
        #self.thermal_consumer = ThermalConsumer(self.env, self.heat_storage)
        self.electrical_consumer = SimpleElectricalConsumer(self.env, self.power_meter)

        self.initialize_helpers()

    """returns a copy of the simulation, starting at the timepoint of the old simulation""" 
    @classmethod
    def copyconstruct(cls, old_sim):
        new_sim = Simulation(copyconstructed=True)
        #start new simulation at timepoint of old simulation
        env = ForwardableRealtimeEnvironment(old_sim.env.now, old_sim.env.measurement_interval)

        new_sim.env = env
        new_sim.env.env_start = old_sim.env.env_start
        new_sim.heat_storage = HeatStorage.copyconstruct(env, old_sim.heat_storage)

        new_sim.power_meter = PowerMeter.copyconstruct(env,old_sim.power_meter)
        new_sim.thermal_consumer = ForecastConsumer.copyconstruct(new_sim.env, old_sim.thermal_consumer, new_sim.heat_storage)
        #new_sim.thermal_consumer = ThermalConsumer.copyconstruct(env,
        #          old_sim.thermal_consumer, new_sim.heat_storage)

        new_sim.electrical_consumer = SimpleElectricalConsumer.copyconstruct(env, old_sim.electrical_consumer, new_sim.power_meter)

        new_sim.plb = PeakLoadBoiler.copyconstruct(env, old_sim.plb, new_sim.heat_storage)
        new_sim.cu = CogenerationUnit.copyconstruct(env, old_sim.cu, new_sim.heat_storage, new_sim.power_meter)


        new_sim.initialize_helpers()


        return new_sim



    def get_systems(self):
        return (self.env, self.heat_storage, self.power_meter, self.cu, self.plb,
            self.thermal_consumer, self.electrical_consumer, self.code_executer)

    def forward(self, seconds):
        self.env.forward = seconds

    def initialize_helpers(self):
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

