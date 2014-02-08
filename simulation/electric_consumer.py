from device import Device, Sensor

seconds_per_hour = 60 * 60

class ElectricConsumer(Device):
    def __init__(self, device_id):
        self.device_id = device_id
        self.name = "Electric Consumer"
        self.sensors = {"electric_consumption":Sensor(name="electric_consumption", id=0, value=5, unit=r"kW"),
                        "energy_infeed":Sensor(name="energy_infeed", id=1, value=0, unit=r"kWh"),
                        "energy_external":Sensor(name="energy_external", id=2, value=0, unit=r"kWh")}
        self.bhkw_energy = 0

    def update(self, time_delta, bhkw):
        time_delta_hour = time_delta / seconds_per_hour
        
        energy_delta = self.bhkw_energy - self.sensors["electric_consumption"].value * time_delta_hour
        # bhkw produces less energy than we need
        if energy_delta < 0:
            self.sensors["energy_external"].value += abs(energy_delta)
        # bhkw produces more energy than we need
        else:
            self.sensors["energy_infeed"].value += energy_delta
            
    
    def add_electric_energy(self,energy):
        self.bhkw_energy = energy
        
    def get_power_demand(self):
        return self.sensors["electric_consumption"].value
