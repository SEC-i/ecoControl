from django.db.models.signals import post_syncdb
from server.models import Device, Sensor, WeatherSource


def install_devices(**kwargs):
    if len(Device.objects.all()) == 0:
        hs = Device(name='Heat Storage', device_type=Device.HS)
        hs.save()
        pm = Device(name='Power Meter', device_type=Device.PM)
        pm.save()
        cu = Device(name='Cogeneration Unit', device_type=Device.CU)
        cu.save()
        plb = Device(name='Peak Load Boiler', device_type=Device.PLB)
        plb.save()
        tc = Device(name='Thermal Consumer', device_type=Device.TC)
        tc.save()
        ec = Device(name='Electrical Consumer', device_type=Device.EC)
        ec.save()
        ce = Device(name='Code Executer', device_type=Device.CE)
        ce.save()

        sensors = []
        sensors.append(
            Sensor(device=hs, name='Temperature', key='get_temperature', unit='C', value_type=Sensor.FLOAT))
        sensors.append(
            Sensor(device=cu, name='Workload', key='workload', unit='%', value_type=Sensor.FLOAT))
        sensors.append(
            Sensor(device=plb, name='Workload', key='workload', unit='%', value_type=Sensor.FLOAT))
        sensors.append(Sensor(device=tc, name='Thermal Consumption',
                       key='get_consumption_power', unit='%', value_type=Sensor.FLOAT))
        sensors.append(Sensor(device=tc, name='Warm Warter Consumption',
                       key='get_warmwater_consumption_power', unit='%', value_type=Sensor.FLOAT))
        sensors.append(Sensor(device=tc, name='Outside Temperature',
                       key='get_outside_temperature', unit='%', value_type=Sensor.FLOAT))
        sensors.append(Sensor(device=ec, name='Electrical Consumption',
                       key='get_consumption_power', unit='%', value_type=Sensor.FLOAT))
        Sensor.objects.bulk_create(sensors)
        print "Default power systems initialized"
        
def save_weather_source(**kwargs):
    if len(WeatherSource.objects.all()) == 0:
        w = WeatherSource()
        w.save()

post_syncdb.connect(install_devices)
post_syncdb.connect(save_weather_source)
