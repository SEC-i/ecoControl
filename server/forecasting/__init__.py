import time
import logging
import calendar
from datetime import datetime
from threading import Thread

from server.models import Device, DeviceConfiguration, Configuration, Sensor, SensorValue
from server.systems import get_user_function, execute_user_function
from server.helpers_thread import write_pidfile_or_fail

from helpers import MeasurementStorage, parse_value

from server.systems.base import BaseEnvironment
from server.forecasting.systems.producers import SimulatedCogenerationUnit, SimulatedPeakLoadBoiler
from server.forecasting.systems.storages import SimulatedHeatStorage, SimulatedPowerMeter
from server.forecasting.systems.consumers import SimulatedThermalConsumer, SimulatedElectricalConsumer

DEFAULT_FORECAST_INTERVAL = 14 * 24 * 3600.0
DEFAULT_FORECAST_STEP_SIZE = 3 * 60.0
DEFAULT_FORECAST_MEASUREMENT_INTERVAL = 15 * 60.0 # has to be multiple of DEFAULT_FORECAST_STEP_SIZE
logger = logging.getLogger('simulation')


def get_forecast(initial_time, interval=DEFAULT_FORECAST_INTERVAL, step_size=DEFAULT_FORECAST_STEP_SIZE, measurement_interval=DEFAULT_FORECAST_MEASUREMENT_INTERVAL, configurations=None, code=None):
    env = BaseEnvironment(initial_time=initial_time, step_size=step_size)

    if configurations is None:
        configurations = DeviceConfiguration.objects.all()

    (env, systems) = get_initialized_scenario(env, configurations)

    measurements = MeasurementStorage(env, systems)
    user_function = get_user_function(systems, code)

    forward = interval
    measurement = 0
    valid = True
    while forward > 0:
        if execute_user_function(user_function, env, systems, get_forecast):
            # call step function for all systems
            for system in systems:
                system.step()

            if measurement == 0:
                measurements.take_and_cache()
                measurement = measurement_interval
            else:
                measurement -= env.step_size

            env.now += env.step_size
            forward -= env.step_size
        else:
            valid = False
            break

    return {
        'start': datetime.fromtimestamp(initial_time).isoformat(),
        'step': measurement_interval,
        'end': datetime.fromtimestamp(env.now).isoformat(),
        'sensors': measurements.get_cached(),
        'valid': valid
    }


def get_initialized_scenario(env, configurations):
        devices = list(Device.objects.all())
        systems = []
        for device in devices:
            for device_type, class_name in Device.DEVICE_TYPES:
                if device.device_type == device_type:
                    system_class = globals()['Simulated%s' % class_name]
                    systems.append(system_class(device.id, env))

        for device in systems:
            # connect power systems
            device.find_dependent_devices_in(systems)
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

        return (env, systems)


class DemoSimulation(Thread):
    stored_simulation = None

    def __init__(self, initial_time, configurations=None):
        Thread.__init__(self)
        self.daemon = True

        self.steps_per_second = 3600.0 / 120
        self.forward = 3600 * 24 * 30

        initial_time = (int(initial_time) / 3600) * 3600.0

        env = BaseEnvironment(initial_time=initial_time, demo=True)

        if configurations is None:
            configurations = DeviceConfiguration.objects.all()

        (self.env, self.systems) = get_initialized_scenario(env, configurations)

        self.measurements = MeasurementStorage(self.env, self.systems, demo=True)
        self.user_function = get_user_function(self.systems)

        self.running = False

    @classmethod
    def start_or_get(cls, print_visible=False):
        """
        This method start a new demo simulation
        if neccessary and it makes sure that only
        one demo simulation can run at once
        """
        if not write_pidfile_or_fail("/tmp/simulation.pid"):
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
        while self.running:
            if execute_user_function(self.user_function, self.env, self.systems, get_forecast):

                # call step function for all systems
                for system in self.systems:
                    system.step()

                self.measurements.take_and_save()

                if self.forward > 0:
                    self.forward -= self.env.step_size
                else:
                    time.sleep(1.0 / self.steps_per_second)

                self.env.now += self.env.step_size
            else:
                # poll for new user_function
                self.user_function = get_user_function(self.systems)

                logger.warning('user_function failed')
                time.sleep(1)

    def start(self):
        self.running = True
        Thread.start(self)

    def fast_forward(self, seconds):
        self.forward = seconds
        self.start()
        self.measurements.flush_data()

    def is_forwarding(self):
        return self.forward > 0.0


def get_initial_time():
    try:
        latest_value = SensorValue.objects.latest('timestamp')
        return calendar.timegm(latest_value.timestamp.timetuple())
    except SensorValue.DoesNotExist:
        return 1356998400  # Tuesday 1st January 2013 12:00:00
