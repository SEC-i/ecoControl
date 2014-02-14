import simpy
from simpy.rt import RealtimeEnvironment

from energy_systems import BHKW, HeatStorage

heat_storage_capacity = 500

simulation_speed = 60

def print_msg(msg):
    if(env.now % simulation_speed == 0):
        print(msg)


def bhkw_generator(env, bhkw, heat_storage):
    print('Starting BHKW...')
    bhkw.start()
    while True:
        if(bhkw.running):
            if(bhkw.producing()):
                print_msg('BHKW workload: %f. Heat Storage level: %f' %
                     (bhkw.get_workload(), heat_storage.level()))
                heat_storage.add_energy(bhkw.get_thermal_power() / 2)
            else:
                print_msg('BHKW not producing. Heat Storage level: %f' %
                      (heat_storage.level()))
        else:
            print_msg('BHKW stopped.')
        yield env.timeout(1)


def thermal_consumer(env, heat_storage):
    while True:
        print_msg('Consuming thermal energy. Minute %f' %
              (env.now / simulation_speed))
        heat_storage.consume_energy(8)
        yield env.timeout(1)

env = RealtimeEnvironment(
    initial_time=0, factor=1.0 / simulation_speed, strict=True)

# define power systems
heat_storage = HeatStorage()
bhkw = BHKW(heat_storage=heat_storage)

env.process(bhkw_generator(env, bhkw, heat_storage))
env.process(thermal_consumer(env, heat_storage))

env.run()
