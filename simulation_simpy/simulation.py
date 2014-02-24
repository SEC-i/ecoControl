import simpy
from simpy.util import start_delayed

from environment import ForwardableRealtimeEnvironment

from systems.code import CodeExecuter
from systems.producers import CogenerationUnit, PeakLoadBoiler
from systems.storages import HeatStorage, ElectricalInfeed
from systems.consumers import SimpleThermalConsumer, ThermalConsumer, SimpleElectricalConsumer

def init_simulation():
    # initialize real-time environment
    env = ForwardableRealtimeEnvironment()
    
    # initialize power systems
    heat_storage = HeatStorage(env)
    electrical_infeed = ElectricalInfeed(env)
    cu = CogenerationUnit(env, heat_storage, electrical_infeed)
    plb = PeakLoadBoiler(env, heat_storage)
    #thermal_consumer = SimpleThermalConsumer(env, heat_storage)
    thermal_consumer = ThermalConsumer(env, heat_storage)
    electrical_consumer = SimpleElectricalConsumer(env, electrical_infeed)
    
    # initilize code executer
    code_executer = CodeExecuter(env, {
        'env': env,
        'heat_storage': heat_storage,
        'electrical_infeed': electrical_infeed,
        'cu': cu,
        'plb': plb,
        'thermal_consumer': thermal_consumer,
        'electrical_consumer': electrical_consumer,
    })
    env.process(code_executer.update())
    
    # add power system to simulation environment
    env.process(thermal_consumer.update())
    env.process(electrical_consumer.update())
    env.process(cu.update())
    
    # start plb 10h after simulation start
    start_delayed(env, plb.update(), 10 * 3600)
    
    return (env, heat_storage, electrical_infeed, cu, plb, \
        thermal_consumer, electrical_consumer, code_executer)
