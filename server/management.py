from django.db.models.signals import post_syncdb
from server.models import Device

def install_devices(**kwargs):
    if len(Device.objects.all()) == 0:
        devices = []
        devices.append(Device(name='Heat Storage', device_type=Device.HS))
        devices.append(Device(name='Power Meter', device_type=Device.PM))
        devices.append(Device(name='Cogeneration Unit', device_type=Device.CU))
        devices.append(Device(name='Peak Load Boiler', device_type=Device.PLB))
        devices.append(Device(name='Thermal Consumer', device_type=Device.TC))
        devices.append(Device(name='Electrical Consumer', device_type=Device.EC))
        devices.append(Device(name='Code Executer', device_type=Device.CE))

        Device.objects.bulk_create(devices)
        print "Default power systems initialized"

post_syncdb.connect(install_devices)