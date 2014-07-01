import logging

from django.core.exceptions import ObjectDoesNotExist

from base import BaseEnvironment
from producers import CogenerationUnit, PeakLoadBoiler
from storages import HeatStorage, PowerMeter
from consumers import ThermalConsumer, ElectricalConsumer
from server.models import Device, Configuration, DeviceConfiguration

logger = logging.getLogger('simulation')

def get_initialized_scenario():
        devices = list(Device.objects.all())
        systems = []
        env = BaseEnvironment()
        for device in devices:
            for device_type, class_name in Device.DEVICE_TYPES:
                if device.device_type == device_type:
                    system_class = globals()[class_name]
                    systems.append(system_class(device.id, env))

        # configurations = DeviceConfiguration.objects.all()
        # for device in systems:
        #     # configure systems
        #     for configuration in configurations:
        #         if configuration.device_id == device.id:
        #             value = parse_value(configuration)
        #             if configuration.key in device.config:
        #                 device.config[configuration.key] = value

        return (env, systems)


def get_user_function(systems, code=None):
    local_names = ['env', 'forecast'] + ['device_%s' % x.id for x in systems]

    if code is None:
        with open('server/user_code.py', "r") as code_file:
            code = code_file.read()

    lines = []
    lines.append("def user_function(%s):" %
                 (",".join(local_names)))

    for line in code.split("\n"):
        lines.append("\t" + line)
    lines.append("\tpass")  # make sure function is not empty

    source = "\n".join(lines)
    namespace = {}
    exec source in namespace  # execute code in namespace

    return namespace['user_function']


def execute_user_function(user_function, env, systems, forecast):
    try:
        user_function(env, forecast, *systems)
        return True
    except:
        return False


def perform_configuration(data):
    configurations = []
    device_configurations = []
    for config in data:
        if all(x in config for x in ['device', 'key', 'value', 'type', 'unit']):
            if config['device'] == '0':
                try:
                    existing_config = Configuration.objects.get(
                        key=config['key'])
                    existing_config.value = config['value']
                    existing_config.value_type = int(
                        config['type'])
                    existing_config.unit = config['unit']
                    existing_config.save()
                except Configuration.DoesNotExist:
                    configurations.append(
                        Configuration(key=config['key'], value=config['value'], value_type=int(config['type']), unit=config['unit']))
            else:
                try:
                    device = Device.objects.get(id=config['device'])
                    for device_type, class_name in Device.DEVICE_TYPES:
                        if device.device_type == device_type:
                            system_class = globals()[class_name]

                    # Make sure that key is present in corresponding system
                    # class
                    if config['key'] in system_class(0, BaseEnvironment()).config:
                        try:
                            existing_config = DeviceConfiguration.objects.get(
                                device=device, key=config['key'])
                            existing_config.device = device
                            existing_config.value = config['value']
                            existing_config.value_type = int(
                                config['type'])
                            existing_config.unit = config['unit']
                            existing_config.save()
                        except DeviceConfiguration.DoesNotExist:
                            device_configurations.append(
                                DeviceConfiguration(device=device, key=config['key'], value=config['value'], value_type=int(config['type']), unit=config['unit']))
                except ObjectDoesNotExist:
                    logger.error("Unknown device %s" % config['device'])
                except ValueError:
                    logger.error(
                        "ValueError value_type '%s' not an int" % config['type'])
        else:
            logger.error("Incomplete config data: %s" % config)

    if len(configurations) > 0:
        Configuration.objects.bulk_create(configurations)
    if len(device_configurations) > 0:
        DeviceConfiguration.objects.bulk_create(device_configurations)