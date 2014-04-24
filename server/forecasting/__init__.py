import time
from copy import deepcopy

from environment import ForwardableRealtimeEnvironment
from helpers import BulkProcessor, SimulationBackgroundRunner, MeasurementCache

from systems.code import CodeExecuter
from systems.producers import CogenerationUnit, PeakLoadBoiler
from systems.storages import HeatStorage, PowerMeter
from systems.consumers import ThermalConsumer, SimpleElectricalConsumer


class Simulation(object):

    # initial_time = Tuesday 1st January 2013 12:00:00
    def __init__(self, config, initial_time=1356998400, copyconstructed=False):

        if copyconstructed:
            return
        # initialize real-time environment
        if initial_time % 3600 != 0.0:
            # ensure that initial_time always at full hour, to avoid
            # measurement bug
            initial_time = (int(initial_time) / 3600) * 3600.0
        self.env = ForwardableRealtimeEnvironment(initial_time=initial_time)

        # initialize power systems
        self.hs = HeatStorage(self.env)
        self.pm = PowerMeter(self.env)

        self.cu = CogenerationUnit(
            self.env, self.hs, self.pm)
        self.plb = PeakLoadBoiler(self.env, self.hs)
        self.tc = ThermalConsumer(self.env, self.hs)
        self.ec = SimpleElectricalConsumer(self.env, self.pm)

        self.measurements = MeasurementCache(
            self.env, self.cu, self.plb, self.hs,
            self.tc, self.ec)
        self.env.register_step_function(self.measurements.take)

        self.thread = None
        self.running = False

        self.configure(config)

        self.initialize_helpers()

    """returns a copy of the simulation, starting at the timepoint of the old simulation"""
    @classmethod
    def copyconstruct(cls, old_sim):
        copy = Simulation(copyconstructed=True)
        # start new simulation at timepoint of old simulation
        env = ForwardableRealtimeEnvironment(
            old_sim.env.now, old_sim.env.measurement_interval)

        copy.env = env
        copy.env.env_start = old_sim.env.env_start
        copy.hs = HeatStorage.copyconstruct(
            env, old_sim.hs)

        copy.pm = PowerMeter.copyconstruct(
            env, old_sim.pm)
        copy.tc = ThermalConsumer.copyconstruct(
            copy.env, old_sim.tc, copy.hs)

        copy.ec = SimpleElectricalConsumer.copyconstruct(
            env, old_sim.ec, copy.pm)

        copy.plb = PeakLoadBoiler.copyconstruct(
            env, old_sim.plb, copy.hs)
        copy.cu = CogenerationUnit.copyconstruct(
            env, old_sim.cu, copy.hs, copy.pm)

        copy.initialize_helpers()

        return copy

    def initialize_helpers(self):
        # initilize code executer
        self.ce = CodeExecuter(self.env, {
            'env': self.env,
            'hs': self.hs,
            'pm': self.pm,
            'cu': self.cu,
            'plb': self.plb,
            'tc': self.tc,
            'ec': self.ec,
            'time': time,
        })

        # initialize BulkProcessor and add it to env
        self.bulk_processor = BulkProcessor(
            self.env, [self.ce, self.cu, self.plb, self.hs, self.tc, self.ec])
        self.env.process(self.bulk_processor.loop())

    def configure(device_configurations):
        for (device_type, variable, value) in device_configurations:
            system = getattr(self, device_type, None)
            if system is not None and variable in dir(system):
                setattr(system, variable, value)

        # re-calculate values of tc
        self.tc.calculate()

    def start(self, blocking=False):
        self.thread = SimulationBackgroundRunner(self.env)
        self.thread.start()
        self.running = True
        if blocking:
            # wait on forwarding to end
            # cant use thread.join() here, because sim will not stop after
            # forward
            while self.is_forwarding():
                time.sleep(0.2)

    def forward(self, seconds, blocking=False):
        self.env.forward = seconds
        if self.thread == None or not self.thread.isAlive():
            self.start(blocking)

    def is_forwarding(self):
        return self.env.forward > 0.0

    """ create a new simulation instance, which copies the settings and timepoint of the main simulation and starts
    forwarding for specified seconds.
    required:
    @param seconds: seconds to forward
    optional:
    @param blocking: function blocks until forecast is done if True, otherwise will run threaded
    @param preStartCallback: pass a callback, which will receive the simulation  instance before it is started
    useful for passing settings before starting the simulation. f.e : 
    setStuff(sim):
        sim.stuff = 123

    get_forecasted_copy(1,preStartCallback=setStuff)
    @param copy_sim: a simulation to copy, use the main simulation if this is left out
    
    """

    def get_forecasted_copy(self, seconds, blocking=False, pre_start_callback=None, copy_sim=None):

        if copy_sim is None:
            new_sim = Simulation.copyconstruct(self)
        else:
            new_sim = Simulation.copyconstruct(copy_sim)

        if pre_start_callback != None:
            pre_start_callback(new_sim)

        new_sim.measurements = MeasurementCache(
            new_sim.env, new_sim.cu, new_sim.plb, new_sim.hs,
            new_sim.tc, new_sim.ec)
        new_sim.env.register_step_function(new_sim.measurements.take)

        new_sim.env.forward = seconds
        new_sim.env.stop_after_forward = True

        if blocking == False:
            thread = SimulationBackgroundRunner(new_sim.env)
            thread.start()
        else:
            t0 = time.time()
            new_sim.env.run()
            print "Time for forecast: ", time.time() - t0, " seconds. Simulated hours: ", seconds / (60.0 * 60.0)

        return new_sim

    def get_total_bilance(self):
        return self.cu.get_operating_costs() + self.plb.get_operating_costs() - \
            self.pm.get_reward() + self.pm.get_costs()

    def get_measurements(self, start=None):
        output = [
            ('cu_electrical_production',
             [round(self.cu.current_electrical_production, 2)]),
            ('cu_total_electrical_production',
             [round(self.cu.total_electrical_production, 2)]),
            ('cu_thermal_production',
             [round(self.cu.current_thermal_production, 2)]),
            ('cu_total_thermal_production',
             [round(self.cu.total_thermal_production, 2)]),
            ('cu_total_gas_consumption',
             [round(self.cu.total_gas_consumption, 2)]),
            ('cu_operating_costs', [round(self.cu.get_operating_costs(), 2)]),
            ('cu_power_ons', [self.cu.power_on_count]),
            ('cu_total_hours_of_operation',
             [round(self.cu.total_hours_of_operation, 2)]),
            ('plb_thermal_production',
             [round(self.plb.current_thermal_production, 2)]),
            ('plb_total_gas_consumption',
             [round(self.plb.total_gas_consumption, 2)]),
            ('plb_operating_costs',
             [round(self.plb.get_operating_costs(), 2)]),
            ('plb_power_ons', [self.plb.power_on_count]),
            ('plb_total_hours_of_operation',
             [round(self.plb.total_hours_of_operation, 2)]),
            ('hs_total_input', [round(self.hs.input_energy, 2)]),
            ('hs_total_output', [round(self.hs.output_energy, 2)]),
            ('hs_empty_count', [round(self.hs.empty_count, 2)]),
            ('total_thermal_consumption',
             [round(self.tc.total_consumption, 2)]),
            ('total_electrical_consumption',
             [round(self.ec.total_consumption, 2)]),
            ('infeed_reward', [round(self.pm.get_reward(), 2)]),
            ('infeed_costs', [round(self.pm.get_costs(), 2)]),
            ('total_bilance', [round(self.get_total_bilance(), 2)]),
            ('code_execution_status',
             [1 if self.ce.execution_successful else 0])]

        output += self.measurements.get(start)

        return dict(output)
