import math
import simpy
from simpy.rt import RealtimeEnvironment
from simpy.util import start_delayed

from producers import BHKW, PeakLoadBoiler
from storages import HeatStorage
from consumers import ThermalConsumer

# initialize real-time environment
env = RealtimeEnvironment(
    initial_time=0, factor=1.0/3600.0, strict=False)

# verbose logging by default
env.quiet = False

# initialize power systems
heat_storage = HeatStorage(env=env)
bhkw = BHKW(env=env, heat_storage=heat_storage)
plb = PeakLoadBoiler(env=env, heat_storage=heat_storage)
thermal = ThermalConsumer(env=env, heat_storage=heat_storage)

# add power system to simulation environment
env.process(thermal.update())
env.process(bhkw.update())

# start plb 10h after simulation start
start_delayed(env, plb.update(), 10 * 3600)
