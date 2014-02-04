import Device
from Device import Sensor
from Device import GeneratorDevice

milliseconds_per_hour = 1000 * 60 * 60

class PLB(GeneratorDevice):

    def __init__(self, device_id):
        GeneratorDevice.__init__(self, device_id)

        self.name = "Peakload Boiler"
        # research needed!
        self.gas_input = 20 # kw
        self.thermal_power = 18 #kw
        self.sensors = {"workload":Sensor(name="workload", id=0, value=0, unit=r"Bool")}

    def update(self,time_delta,heat_storage):
        time_delta_hour = time_delta / milliseconds_per_hour
        needed_thermal_energy = heat_storage.get_energy_demand()
        # comparison from overall energy demand (kwh) and power (kw) of an hour doesnt require time quotient
        # 81 -> maximal thermal power from BHKW
        if needed_thermal_energy > 81 or \
            heat_storage.sensors["temperature"].value < 60:
                
            self.sensors["workload"].value = 1
            heat_storage.add_energy(self.thermal_power * time_delta_hour)
        else:
            self.sensors["workload"].value = 0
