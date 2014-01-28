import Simulation


class Consumer:


    def __init__(self,time_step,stored_heat):
        self.current_power_demand = 10 #kW
        self.current_heat_demand = 40        
        self.time_step = time_step

    def consume(self, time_delta,consume_object):
        if time_delta < self.time_step:
            # didnt update
            return False

        self.

