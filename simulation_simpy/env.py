from simpy.core import Environment
from simpy.rt import RealtimeEnvironment


class ForwardableRealtimeEnvironment(RealtimeEnvironment):

    def __init__(self, initial_time=0, factor=1.0, strict=True):
        RealtimeEnvironment.__init__(self, initial_time, factor, strict)

        # start_time = time.time()
        self.start_time = 1388534400  # 01.01.2014 00:00

        # verbose logging by default
        self.quiet = False

        self.forward = 0
        self.clear_data()

    def connect_devices(self, bhkw, plb, heat_storage, thermal):
        self.bhkw = bhkw
        self.plb = plb
        self.heat_storage = heat_storage
        self.thermal = thermal

    def step(self):
        if self.forward > 0:
            forward_to = self.now + self.forward
            sim_delta = self.forward - self.now

            forward_time = self.now
            while self.now < forward_to:
                Environment.step(self)

                # add measurement if simulation time has changed
                if self.now > forward_time:
                    forward_time = self.now
                    self.append_measurement()

            self.env_start += self.forward
            self.forward = 0
        else:
            return RealtimeEnvironment.step(self)

    def clear_data(self):
        self.data = {
            'time': [],
            'bhkw_workload': [],
            'bhkw_electrical_power': [],
            'bhkw_thermal_power': [],
            'bhkw_total_gas_consumption': [],
            'plb_workload': [],
            'plb_thermal_power': [],
            'plb_total_gas_consumption': [],
            'hs_level': [],
            'thermal_consumption': []
        }

    def append_measurement(self):
        self.data['time'].append(self.get_time())
        self.data['bhkw_workload'].append(round(self.bhkw.get_workload(), 2))
        self.data['bhkw_electrical_power'].append(round(self.bhkw.get_electrical_power(), 2))
        self.data['bhkw_thermal_power'].append(round(self.bhkw.get_thermal_power(), 2))
        self.data['bhkw_total_gas_consumption'].append(round(self.bhkw.total_gas_consumption, 2))
        self.data['plb_workload'].append(round(self.plb.get_workload(), 2))
        self.data['plb_thermal_power'].append(round(self.plb.get_thermal_power(), 2))
        self.data['plb_total_gas_consumption'].append(round(self.plb.total_gas_consumption, 2))
        self.data['hs_level'].append(round(self.heat_storage.level(), 2))
        self.data['thermal_consumption'].append(round(self.thermal.get_consumption(), 2))

    def get_time(self):
        return self.start_time + self.now
