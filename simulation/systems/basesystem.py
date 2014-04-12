
class BaseSystem(object):

    def __init__(self, env):
        self.env = env

    @classmethod
    def copyconstruct(cls, env, other_system):
        #instantiate a new object of type other_system
        system = type(other_system)(env)
        # just a shallow copy, so no dict copy
        system.__dict__ = other_system.__dict__.copy()
        system.env = env
        return system
