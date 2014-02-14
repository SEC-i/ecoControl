import math
import simpy
from simpy.rt import RealtimeEnvironment

from energy_systems import BHKW, HeatStorage, PeakLoadBoiler

heat_storage_capacity = 500

simulation_speed = 1

gas_price_per_kwh = 0.0655


def print_msg(msg):
    if(env.now % simulation_speed == 0):
        print(msg)

def bhkw_generator(env, bhkw, heat_storage):
    while True:
        if bhkw.running:
            print_msg('BHKW workload:\t%f %%\tTotal:\t%f kWh (%f Euro)' % (bhkw.get_workload(), bhkw.total_gas_consumption, bhkw.total_gas_consumption*gas_price_per_kwh))
            if bhkw.producing():
                heat_storage.add_energy(bhkw.get_thermal_power(True))
        else:
            print_msg('BHKW stopped.')
        yield env.timeout(1)


def plb_generator(env, plb, heat_storage):
    while True:
        plb.analyze_demand()
        if plb.running:
            print_msg('PLB workload:\t%f %%\tTotal:\t%f kWh (%f Euro)' % (plb.get_workload(), plb.total_gas_consumption, plb.total_gas_consumption*gas_price_per_kwh))
            if plb.producing:
                heat_storage.add_energy(plb.get_thermal_power(True))
        else:
            print_msg('PLB stopped.')
        yield env.timeout(1)


def thermal_consumer(env, heat_storage, bhkw, plb):
    print('Starting BHKW...')
    bhkw.start()
    print('Starting PLB...')
    plb.start()
    while True:
        consumption = 20 + 10 * \
            math.fabs(
                math.sin(((env.now / simulation_speed) % 100.0) / 100.0 * 2 * math.pi))

        heat_storage.consume_energy(consumption)
        msg = ('\n== %d =============\nThermal demand:\t%f kW\n' %
              ((env.now / simulation_speed), consumption))
        msg += ('HS level:\t%f kWh' %
               (heat_storage.level()))

        print_msg(msg)
        yield env.timeout(1)

env = RealtimeEnvironment(
    initial_time=0, factor=1.0 / simulation_speed, strict=True)

# define power systems
heat_storage = HeatStorage()
bhkw = BHKW(heat_storage=heat_storage)
plb = PeakLoadBoiler(heat_storage=heat_storage)

env.process(thermal_consumer(env, heat_storage, bhkw, plb))
env.process(bhkw_generator(env, bhkw, heat_storage))
env.process(plb_generator(env, plb, heat_storage))

env.run()
