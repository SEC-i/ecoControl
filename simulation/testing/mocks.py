class HeatStorageMock():
    def __init__(self):
        self.required_energy = 0.0
        self.temperature = 0.0
        self.target_temperature = 0.0
        
    def get_require_energy(self):
        return self.required_energy
        
    def add_energy(self, energy):
        pass
    
    def get_temperature(self):
        return self.temperature
