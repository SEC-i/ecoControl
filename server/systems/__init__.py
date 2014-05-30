from producers import CogenerationUnit, PeakLoadBoiler
from storages import HeatStorage, PowerMeter
from consumers import ThermalConsumer, ElectricalConsumer

from server.models import Device


def get_initialized_scenario():
        devices = list(Device.objects.all())
        system_list = []
        for device in devices:
            for device_type, class_name in Device.DEVICE_TYPES:
                if device.device_type == device_type:
                    system_class = globals()[class_name]
                    system_list.append(system_class(device.id))

        return system_list


def get_user_function(systems):
    local_names = ['device_%s' % system.id for system in systems]

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