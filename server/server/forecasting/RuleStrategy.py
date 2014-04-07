


class RuleStrategy(object):
    """docstring for RuleStrategy"""
    def __init__(self, env, simulation_manager):
        super(RuleStrategy, self).__init__()
        self.env = env
        self.simulation_manager = simulation_manager


    #priorities:
    #1 ensure heatstorage 

    def validate_heatstorage_fill(self):
        (sim,measurements) = self.simulation_manager.forecast_for(60 * 60 * 24 * 7)

