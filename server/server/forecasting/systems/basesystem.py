
class BaseSystem(object):

    def __init__(self,env):
        self.env = env

    @classmethod
    def copyconstruct(cls, env, other_system):
        system = type(other_system)(env) #instaniate a new object of type other_system
        system.__dict__ = other_system.__dict__.copy()    # just a shallow copy, so no dict copy
        return system