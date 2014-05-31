import time
import logging
import calendar

from server.models import Device, DeviceConfiguration, Configuration, Sensor, SensorValue
from server.systems import get_user_function
from server.helpers import write_pidfile_or_fail

from environments import DummyEnvironment, ForwardableRealtimeEnvironment
from helpers import BulkProcessor, SimulationBackgroundRunner, MeasurementStorage, parse_value

from server.forecasting.systems.producers import SimulatedCogenerationUnit, SimulatedPeakLoadBoiler
from server.forecasting.systems.storages import SimulatedHeatStorage, SimulatedPowerMeter
from server.forecasting.systems.consumers import SimulatedThermalConsumer, SimulatedElectricalConsumer
import cProfile


logger = logging.getLogger('simulation')


def get_forecast(initial_time, configurations=None, code=None):
    env = DummyEnvironment(initial_time)

    if configurations is None:
        configurations = DeviceConfiguration.objects.all()

    systems = get_initialized_scenario(env, configurations)

    measurements = MeasurementStorage(env, systems)
    user_function = get_user_function(systems, code)

    forward = 14 * 24 * 3600
    while forward > 0:
        measurements.take_and_cache()

        user_function(*systems)

        # call step function for all systems
        for system in systems:
            system.step()

        env.now += 120.0
        forward -= 120.0

    return measurements.get()


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
                    if configuration.key in dir(device):
                        setattr(device, configuration.key, value)

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


class DemoSimulation(object):
    stored_simulation = None

    def __init__(self, initial_time, configurations=None):
        initial_time = (int(initial_time) / 3600) * 3600.0

        # initialize real-time environment
        self.env = ForwardableRealtimeEnvironment(initial_time=initial_time)

        if configurations is None:
            configurations = DeviceConfiguration.objects.all()

        self.devices = get_initialized_scenario(self.env, configurations)

        self.measurements = MeasurementStorage(self.env, self.devices)
        self.env.register_step_function(self.measurements.take_and_save)

        self.thread = None
        self.running = False

        # initialize BulkProcessor and add it to env
        self.bulk_processor = BulkProcessor(self.env, self.devices)
        self.env.process(self.bulk_processor.loop())

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

    def start(self):
        self.running = True
        self.thread = SimulationBackgroundRunner(self.env)
        self.thread.start()

    def fast_forward(self, seconds):
        self.env.forward = seconds
        self.start()
        self.measurements.flush_data()

    def is_forwarding(self):
        return self.env.forward > 0.0

    def get_total_bilance(self):
        return self.cu.get_operating_costs() + self.plb.get_operating_costs() - \
            self.pm.get_reward() + self.pm.get_costs()


def get_initial_time():
    try:
        latest_value = SensorValue.objects.latest('timestamp')
        return calendar.timegm(latest_value.timestamp.timetuple())
    except SensorValue.DoesNotExist:
        return 1356998400  # Tuesday 1st January 2013 12:00:00
