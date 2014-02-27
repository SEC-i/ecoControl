class BaseSystem(object):

    def __init__(self, env):
        self.env = env

    def step(self):
        raise NotImplementedError

    def loop(self):
        while True:
            self.step()
            yield self.env.timeout(self.env.step_size)


def sign(x):
    return 1 if x >= 0 else -1
