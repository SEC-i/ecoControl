class HeatStorageMock():
    def __init__(self):
        self.required_energy = 0
        
    def get_require_energy(self):
        return self.required_energy
        
    def add_energy(self, energy):
        pass
