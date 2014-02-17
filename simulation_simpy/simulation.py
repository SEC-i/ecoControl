import math
import simpy
from simpy.util import start_delayed

from environment import ForwardableRealtimeEnvironment

from systems.producers import CogenerationUnit, PeakLoadBoiler
from systems.storages import HeatStorage, ElectricalInfeed
from systems.consumers import ThermalConsumer, ElectricalConsumer

# initialize real-time environment
env = ForwardableRealtimeEnvironment(
    initial_time=0, factor=1.0/3600.0, strict=False)

# initialize power systems
heat_storage = HeatStorage(env=env)
electrical_infeed = ElectricalInfeed()
cu = CogenerationUnit(env=env, heat_storage=heat_storage, electrical_infeed=electrical_infeed)
plb = PeakLoadBoiler(env=env, heat_storage=heat_storage)
thermal_consumer = ThermalConsumer(env=env, heat_storage=heat_storage)
electrical_consumer = ElectricalConsumer(env=env, electrical_infeed=electrical_infeed)

# add power system to simulation environment
env.process(thermal_consumer.update())
env.process(electrical_consumer.update())
env.process(cu.update())

# start plb 10h after simulation start
start_delayed(env, plb.update(), 10 * 3600)
