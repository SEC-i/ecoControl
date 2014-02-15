from simpy.core import Environment
from simpy.rt import RealtimeEnvironment


class ForwardableRealtimeEnvironment(RealtimeEnvironment):

    def __init__(self, initial_time=0, factor=1.0, strict=True):
        RealtimeEnvironment.__init__(self, initial_time, factor, strict)
        self.forward = 0

    def step(self):
        if self.forward > 0:
            forward_to = self.now + self.forward
            sim_delta = self.forward - self.now

            while self.now < forward_to:
                Environment.step(self)

            self.env_start += self.forward
            self.forward = 0
        else:
            return RealtimeEnvironment.step(self)
