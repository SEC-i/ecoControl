import math


class BaseSystem(object):

    def __init__(self, env):
        self.env = env

    @classmethod
    def copyconstruct(cls, env, other_system):
        # instantiate a new object of type other_system
        system = type(other_system)(env)
        # just a shallow copy, so no dict copy
        system.__dict__ = other_system.__dict__.copy()
        system.env = env
        return system

    def connected(self):
        raise NotImplemented


def interpolate_year(day):
    """
    input: int between 0,365
    output: float between 0,1
    interpolates a year day to 1=winter, 0=summer
    """
    # shift summer days at 180-365
    # 1'April = 90th day
    day_shift = day + 90
    day_shift %= 365
    day_float = float(day) / 365.0
    interpolation = math.cos(day_float * math.pi * 2)
    # shift to 0-1
    interpolation /= 2
    interpolation += 0.5
    return interpolation
