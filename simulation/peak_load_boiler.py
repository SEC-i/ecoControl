from device import Sensor, GeneratorDevice

seconds_per_hour = 60 * 60

class PLB(GeneratorDevice):

    def __init__(self, device_id, power):
        GeneratorDevice.__init__(self, device_id)
        
        self.name = "Peakload Boiler"
        self.gas_input = power # kw
        self.gas_cost = 0.0654 #per kWH
        self.thermal_power = self.gas_input * 0.8 #kw efficiency up to 90 % are possible
        self.sensors = {"workload":Sensor(name="workload", id=0, value=0, unit=r"%",graph_id=1),
                        "gas_input":Sensor(name="gas_input", id=1, value=0, unit=r"kw",graph_id=1),
                        "thermal_power":Sensor(name="thermal_power", id=2, value=0, unit=r"kw",graph_id=1),
                        "gas_cost_sum":Sensor(name="gas_cost_sum",id=3,value=0,unit="Euro")}

    def update(self,time_delta,heat_storage):
        time_delta_hour = time_delta / seconds_per_hour
        needed_thermal_energy = heat_storage.get_energy_demand()
        # comparison from overall energy demand (kwh) and power (kw) of an hour doesnt require time quotient
        # 12.5 -> maximal thermal power from BHKW
        if needed_thermal_energy >  12.5:
                
            self.power_on()
            heat_storage.add_energy(self.thermal_power * time_delta_hour)
        else:
            self.power_off()
        
        self.sensors["gas_cost_sum"] += self.gas_cost * self.sensors["gas_input"].value * time_delta_hour

    def power_on(self):
        self.sensors["workload"].value = 99
        self.sensors["gas_input"].value = self.gas_input
        self.sensors["thermal_power"].value = self.thermal_power

    def power_off(self):
        self.sensors["workload"].value = 0
        self.sensors["gas_input"].value = 0
        self.sensors["thermal_power"].value = 0
