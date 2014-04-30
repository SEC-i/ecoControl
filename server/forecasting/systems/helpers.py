from math import cos, pi


class BaseSystem(object):

    def __init__(self, system_id, env):
        self.id = system_id
        self.env = env

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
    interpolation = cos(day_float * pi * 2)
    # shift to 0-1
    return (interpolation / 2) + 0.5
