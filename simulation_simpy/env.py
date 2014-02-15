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

        # function which gets called every step in forward mode
        self.step_function = None

        self.last_step = self.now

    def step(self):
        if self.forward > 0:
            forward_to = self.now + self.forward
            sim_delta = self.forward - self.now

            while self.now < forward_to:
                self.handle_step_function()
                Environment.step(self)

            self.env_start += self.forward
            self.forward = 0
        else:
            self.handle_step_function()
            return RealtimeEnvironment.step(self)

    def handle_step_function(self):
        # call step_function whenever time has changed
        if self.now > self.last_step and self.step_function is not None:
            self.last_step = self.now
            self.step_function()

    def get_time(self):
        return self.start_time + self.now
