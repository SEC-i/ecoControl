from device import Device, Sensor

seconds_per_hour = 60 * 60

class ElectricConsumer(Device):
    def __init__(self, device_id):
        self.device_id = device_id
        self.name = "Electric Consumer"
        self.sensors = {"electric_consumption":Sensor(name="electric_consumption", id=0, value=3, unit=r"kW"),
                        "energy_infeed":Sensor(name="energy_infeed", id=1, value=0, unit=r"kWh"),
                        "energy_external":Sensor(name="energy_external", id=2, value=0, unit=r"kWh"),
                        "infeed_sum":Sensor(name="infeed_cost", id=3, value=0, unit=r"Euro"),
                        "consumption_reward_sum":Sensor(name="consumption_reward_sum",id=4,value=0,unit=r"Euro"),
                        "external_sum":Sensor(name="external_cost", id=5, value=0, unit=r"Euro")}
        self.bhkw_energy = 0
        self.maintenance_cost = 0.05
        self.infeed_reward = 0.0971 #KWK + vermiedene netzkosten + zuschlag
        self.consumption_reward = 0.0541 + 0.0205 + 0.00055 #KWKzuschlag + rueckerstattung stromsteuer + rueckerstattung energiesteuer + erdgas
        #TODO Bafa foerderung
        self.external_cost = 0.283

    def update(self, time_delta, bhkw):
        time_delta_hour = time_delta / seconds_per_hour
        
        energy_delta = self.bhkw_energy - self.sensors["electric_consumption"].value * time_delta_hour
        # bhkw produces less energy than we need
        if energy_delta < 0:
            self.sensors["energy_external"].value += abs(energy_delta)
            self.sensors["external_sum"].value += self.external_cost * energy_delta
        # bhkw produces more energy than we need
        else:
            self.sensors["energy_infeed"].value += energy_delta
            self.sensors["infeed_sum"].value += energy_delta * (self.infeed_reward-self.maintenance_cost)
        
        self.sensors["consumption_reward_sum"].value += self.sensors["electric_consumption"].value* time_delta_hour * (self.consumption_reward - self.maintenance_cost)
    
    def add_electric_energy(self,energy):
        self.bhkw_energy = energy
        
    def get_power_demand(self):
        return self.sensors["electric_consumption"].value
