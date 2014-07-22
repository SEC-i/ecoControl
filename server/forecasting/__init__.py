import time
import logging
import calendar
from datetime import datetime
from threading import Thread

from server.models import Device, DeviceConfiguration, Configuration, Sensor, SensorValue
from server.systems import get_user_function
from server.helpers_thread import write_pidfile_or_fail

from helpers import MeasurementStorage, parse_value

from server.systems.base import BaseEnvironment
from server.forecasting.systems.producers import SimulatedCogenerationUnit, SimulatedPeakLoadBoiler
from server.forecasting.systems.storages import SimulatedHeatStorage, SimulatedPowerMeter
from server.forecasting.systems.consumers import SimulatedThermalConsumer, SimulatedElectricalConsumer
from server.forecasting.forecasting.auto_optimization import auto_optimize

DEFAULT_FORECAST_INTERVAL = 14 * 24 * 3600.0
DEFAULT_FORECAST_STEP_SIZE = 15 * 60.0
logger = logging.getLogger('simulation')

use_auto_optimization=False
auto_optimize_progress = 0

def get_forecast(initial_time, configurations=None, code=None, forward=None, forecast=True):
    env = BaseEnvironment(initial_time=initial_time,forecast=forecast, step_size=DEFAULT_FORECAST_STEP_SIZE)

    if configurations is None:
        configurations = DeviceConfiguration.objects.all()

    systems = get_initialized_scenario(env, configurations)

    measurements = MeasurementStorage(env, systems)
    user_function = get_user_function(systems, code)

    if forward == None:
        forward = DEFAULT_FORECAST_INTERVAL
    time_remaining = forward
    
    next_auto_optim = 0.0
    
    while time_remaining > 0:
        measurements.take_and_cache()

        user_function(*systems)

        if next_auto_optim <= 0.0 and use_auto_optimization:  
            auto_optimize(env,systems)
            next_auto_optim = 3600.0
            global auto_optimize_progress
            auto_optimize_progress = 100.0 - (time_remaining/float(forward)) * 100
        # call step function for all systems
        for system in systems:
            system.step()
        

        measurements.take_and_cache()

        env.now += env.step_size
        time_remaining -= env.step_size
        next_auto_optim -= env.step_size

    return {
        'start': datetime.fromtimestamp(initial_time).isoformat(),
        'step': DEFAULT_FORECAST_STEP_SIZE,
        'end': datetime.fromtimestamp(env.now).isoformat(),
        'sensors': measurements.get_cached()
    }


def get_initialized_scenario(env, configurations):
        devices = list(Device.objects.all())
        system_list = []
        for device in devices:
            for device_type, class_name in Device.DEVICE_TYPES:
                if device.device_type == device_type:
                    system_class = globals()['Simulated%s' % class_name]
                    system_list.append(system_class(device.id, env))

        for device in system_list:
            # connect power systems
            device.find_dependent_devices_in(system_list)
            if not device.connected():
                logger.error(
                    "Simulation: Device %s is not connected" % device.name)
                raise RuntimeError

            # configure systems
            for configuration in configurations:
                if configuration.device_id == device.id:
                    value = parse_value(configuration)
                    if configuration.key in device.config:
                        device.config[configuration.key] = value

            # load latest sensor values
            try:
                for sensor in Sensor.objects.filter(device_id=device.id):
                    value = SensorValue.objects.filter(
                        sensor=sensor).latest('timestamp').value
                    if sensor.setter != '':
                        callback = getattr(device, sensor.setter, None)
                        if callback is not None:
                            if hasattr(callback, '__call__'):
                                callback(value)
                            else:
                                setattr(device, sensor.setter, value)

            except SensorValue.DoesNotExist:
                logger.warning("Simulation: No sensor values \
                    found for sensor '%s' at device '%s'"
                               % (sensor.name, sensor.device.name))
            except Sensor.DoesNotExist:
                logger.warning(
                    'Could not find any sensor values to configure simulation')

            # re-calculate values
            device.calculate()

        return system_list


class DemoSimulation(Thread):
    stored_simulation = None
    

    def __init__(self, initial_time, configurations=None):
        Thread.__init__(self)
        self.daemon = True

        self.steps_per_second = 3600.0 / 120
        self.forward = 0

        initial_time = (int(initial_time) / 3600) * 3600.0
        # initialize real-time environment
        self.env = BaseEnvironment(initial_time=initial_time, demo=True)

        if configurations is None:
            configurations = DeviceConfiguration.objects.all()

        self.systems = get_initialized_scenario(self.env, configurations)

        self.measurements = MeasurementStorage(self.env, self.systems)
        self.user_function = get_user_function(self.systems)

        self.running = False

    @classmethod
    def start_or_get(cls, print_visible=False):
        """
        This method start a new demo simulation
        if neccessary and it makes sure that only
        one demo simulation can run at once
        """
        #if not write_pidfile_or_fail("/tmp/simulation.pid"):
        # Start demo simulation if in demo mode
        system_mode = Configuration.objects.get(key='system_mode')
        if system_mode.value == 'demo':
            if print_visible:
                print 'Starting demo simulation...'
            else:
                logger.debug('Starting demo simulation...')

            simulation = DemoSimulation(get_initial_time())
            simulation.start()
            cls.stored_simulation = simulation
            return simulation
        if cls.stored_simulation != None:
            return cls.stored_simulation

    def run(self):
        next_auto_optim = 0.0
        while self.running:
            self.user_function(*self.systems)
            
            if next_auto_optim <= 0.0 and use_auto_optimization:  
                auto_optimize(self.env,self.systems)
                next_auto_optim = 3600.0

            # call step function for all systems
            for system in self.systems:
                system.step()

            self.measurements.take_and_save()

            if self.forward > 0:
                self.forward -= self.env.step_size
            else:
                time.sleep(1.0 / self.steps_per_second)

            self.env.now += self.env.step_size
            next_auto_optim -= self.env.step_size

    def start(self):
        self.running = True
        Thread.start(self)

    def fast_forward(self, seconds):
        self.forward = seconds
        self.start()
        self.measurements.flush_data()

    def is_forwarding(self):
        return self.forward > 0.0

    def update_user_function(self):
        self.user_function = get_user_function(self.systems)

def activate_auto_optimization(state):
    global use_auto_optimization
    use_auto_optimization = state
    global auto_optimize_progress
    auto_optimize_progress = 0
    
def get_auto_optimize_progress():
    return auto_optimize_progress

def get_initial_time():
    try:
        latest_value = SensorValue.objects.latest('timestamp')
        return calendar.timegm(latest_value.timestamp.timetuple())
    except SensorValue.DoesNotExist:
        return 1356998400  # Tuesday 1st January 2013 12:00:00
