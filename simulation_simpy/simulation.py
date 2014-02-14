import math
import simpy
from simpy.rt import RealtimeEnvironment

from energy_systems import BHKW, HeatStorage, PeakLoadBoiler, ThermalConsumer

simulation_speed = 1
gas_price_per_kwh = 0.0655


def print_msg(msg):
    if(env.now % simulation_speed == 0):
        print(msg)


def bhkw_generator(env, bhkw, heat_storage):
    print('Starting BHKW...')
    bhkw.start()
    while True:
        if bhkw.running:
            print_msg('BHKW workload:\t%f %%\tTotal:\t%f kWh (%f Euro)' %
                      (bhkw.get_workload(), bhkw.total_gas_consumption, bhkw.total_gas_consumption * gas_price_per_kwh))
            if bhkw.get_workload() > 0:
                heat_storage.add_energy(bhkw.get_thermal_power(True))
        else:
            print_msg('BHKW stopped.')
        yield env.timeout(1)


def plb_generator(env, plb, heat_storage):
    print('Starting PLB...')
    plb.start()
    while True:
        plb.analyze_demand()
        if plb.running:
            print_msg('PLB workload:\t%f %%\tTotal:\t%f kWh (%f Euro)' %
                      (plb.get_workload(), plb.total_gas_consumption, plb.total_gas_consumption * gas_price_per_kwh))
            if plb.get_workload() > 0:
                heat_storage.add_energy(plb.get_thermal_power(True))
        else:
            print_msg('PLB stopped.')
        yield env.timeout(1)


def thermal_consumer(env, thermal, heat_storage):
    while True:
        consumption = thermal.get_consumption()
        heat_storage.consume_energy(consumption)
        msg = ('Thermal demand:\t%f kW\n' % (consumption))
        msg += ('HS level:\t%f kWh' %
               (heat_storage.level()))
        print_msg(msg)
        yield env.timeout(1)


def main(env):
    while True:
        print_msg('\n== %d =============' % (env.now / simulation_speed))
        yield env.timeout(1)

env = RealtimeEnvironment(
    initial_time=0, factor=1.0 / simulation_speed, strict=True)

# define power systems
heat_storage = HeatStorage()
bhkw = BHKW(heat_storage=heat_storage)
plb = PeakLoadBoiler(heat_storage=heat_storage)
thermal = ThermalConsumer(env=env)

# add power system to simulation environment
env.process(main(env))
env.process(thermal_consumer(env, thermal, heat_storage))
env.process(bhkw_generator(env, bhkw, heat_storage))
env.process(plb_generator(env, plb, heat_storage))
