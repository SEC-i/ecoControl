import Device
from Device import Sensor

class Heating(Device.Device):
    def __init__(self,device_id):
        Device.Device.__init__(self, device_id)

        self.sensors = {"electric_demand":Sensor(name="electric_demand", id=0, value=10, unit=r"kW", max_value=1000),
                        "heat_demand":Sensor(name="heat_demand", id=0, value=10, unit=r"kW", max_value=1000)}

    def consume_power(self, heat_storage):
        heat_storage.consume_power(self.current_power_demand)

    def update(self,time_delta,heat_storage):
        pass

