import time

import simpy
from simpy.util import start_delayed

from environment import DemoEnvironment

from systems.base import CodeExecuter, UnitControlServer
from systems.producers import CogenerationUnit, PeakLoadBoiler
from systems.storages import HeatStorage, PowerMeter
from systems.consumers import ThermalConsumer, SimpleElectricalConsumer

from helpers import BulkProcessor


# initialize real-time environment
env = DemoEnvironment()

# initialize power systems
heat_storage = HeatStorage(env)
power_meter = PowerMeter(env)
cu = CogenerationUnit(env, heat_storage, power_meter)
plb = PeakLoadBoiler(env, heat_storage)
thermal_consumer = ThermalConsumer(env, heat_storage)
electrical_consumer = SimpleElectricalConsumer(env, power_meter)
unit_control_server = UnitControlServer(
    env, heat_storage, power_meter, cu, plb, thermal_consumer, electrical_consumer)

# initilize code executer
code_executer = CodeExecuter(env, {
    'env': env,
    'heat_storage': heat_storage,
    'power_meter': power_meter,
    'cu': cu,
    'plb': plb,
    'thermal_consumer': thermal_consumer,
    'electrical_consumer': electrical_consumer,
    'time': time,
})

# initialize BulkProcessor and add it to env
bulk_processor = BulkProcessor(
    env, [code_executer, cu, plb, heat_storage, thermal_consumer, electrical_consumer, unit_control_server])
env.process(bulk_processor.loop())
env.run()
