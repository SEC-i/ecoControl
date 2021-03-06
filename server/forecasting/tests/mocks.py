class HeatStorageMock():

    def __init__(self):
        self.required_energy = 0.0
        self.temperature = 0.0
        self.target_temperature = 0.0
        self.input_energy = 0

    def get_required_energy(self):
        return self.required_energy

    def add_energy(self, energy):
        self.input_energy += energy

    def get_temperature(self):
        return self.temperature