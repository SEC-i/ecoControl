import logging
import os
from django.core.exceptions import ObjectDoesNotExist

from base import BaseEnvironment
from producers import CogenerationUnit, PeakLoadBoiler
from storages import HeatStorage, PowerMeter
from consumers import ThermalConsumer, ElectricalConsumer
from server.models import System, Configuration, SystemConfiguration
from server.settings import BASE_DIR

logger = logging.getLogger('simulation')

def get_initialized_scenario():
        systems = list(System.objects.all())
        systems = []
        env = BaseEnvironment()
        for system in systems:
            for system_type, class_name in System.DEVICE_TYPES:
                if system.system_type == system_type:
                    system_class = globals()[class_name]
                    systems.append(system_class(system.id, env))

        # configurations = SystemConfiguration.objects.all()
        # for system in systems:
        #     # configure systems
        #     for configuration in configurations:
        #         if configuration.system_id == system.id:
        #             value = parse_value(configuration)
        #             if configuration.key in system.config:
        #                 system.config[configuration.key] = value

        return (env, systems)


def get_user_function(systems, code=None):
    local_names = ['env', 'forecast'] + ['system_%s' % x.id for x in systems]

    if code is None:
        with open(os.path.join(BASE_DIR,'server','user_code.py'), "r") as code_file:
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
    system_configurations = []
    for config in data:
        if all(x in config for x in ['system', 'key', 'value', 'type', 'unit']):
            if config['system'] == '0':
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
                    system = System.objects.get(id=config['system'])
                    for system_type, class_name in System.DEVICE_TYPES:
                        if system.system_type == system_type:
                            system_class = globals()[class_name]

                    # Make sure that key is present in corresponding system
                    # class
                    if config['key'] in system_class(0, BaseEnvironment()).config:
                        try:
                            existing_config = SystemConfiguration.objects.get(
                                system=system, key=config['key'])
                            existing_config.system = system
                            existing_config.value = config['value']
                            existing_config.value_type = int(
                                config['type'])
                            existing_config.unit = config['unit']
                            existing_config.save()
                        except SystemConfiguration.DoesNotExist:
                            system_configurations.append(
                                SystemConfiguration(system=system, key=config['key'], value=config['value'], value_type=int(config['type']), unit=config['unit']))
                except ObjectDoesNotExist:
                    logger.error("Unknown system %s" % config['system'])
                except ValueError:
                    logger.error(
                        "ValueError value_type '%s' not an int" % config['type'])
        else:
            logger.error("Incomplete config data: %s" % config)

    if len(configurations) > 0:
        Configuration.objects.bulk_create(configurations)
    if len(system_configurations) > 0:
        SystemConfiguration.objects.bulk_create(system_configurations)