import simpy
from simpy.util import start_delayed

from environment import ForwardableRealtimeEnvironment

from systems.code import CodeExecuter
from systems.producers import CogenerationUnit, PeakLoadBoiler
from systems.storages import HeatStorage, PowerMeter
from systems.consumers import ThermalConsumer, SimpleElectricalConsumer


def get_new_simulation():
    # initialize real-time environment
    env = ForwardableRealtimeEnvironment()

    # initialize power systems
    heat_storage = HeatStorage(env)
    power_meter = PowerMeter(env)
    cu = CogenerationUnit(env, heat_storage, power_meter)
    plb = PeakLoadBoiler(env, heat_storage)
    thermal_consumer = ThermalConsumer(env, heat_storage)
    electrical_consumer = SimpleElectricalConsumer(env, power_meter)

    # initilize code executer
    code_executer = CodeExecuter(env, {
        'env': env,
        'heat_storage': heat_storage,
        'power_meter': power_meter,
        'cu': cu,
        'plb': plb,
        'thermal_consumer': thermal_consumer,
        'electrical_consumer': electrical_consumer,
    })
    env.process(code_executer.loop())

    # add power system to simulation environment
    env.process(thermal_consumer.loop())
    env.process(electrical_consumer.loop())
    env.process(cu.loop())
    env.process(heat_storage.loop())

    # start plb 10h after simulation start
    start_delayed(env, plb.loop(), 10 * 3600)

    return (env, heat_storage, power_meter, cu, plb,
            thermal_consumer, electrical_consumer, code_executer)
