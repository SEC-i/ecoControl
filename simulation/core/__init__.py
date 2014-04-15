import sys
import os
import time
from copy import deepcopy

import simpy
from simpy.util import start_delayed

from core.environment import ForwardableRealtimeEnvironment

from systems.code import CodeExecuter
from systems.producers import CogenerationUnit, PeakLoadBoiler
from systems.storages import HeatStorage, PowerMeter
from systems.consumers import ThermalConsumer, SimpleElectricalConsumer, ForecastConsumer

from helpers import BulkProcessor, SimulationBackgroundRunner, MeasurementCache, parse_hourly_demand_values


class Simulation(object):
    # initial_time = Tuesday 1st January 2013 12:00:00

    def __init__(self, initial_time=1356998400, copyconstructed=False):

        if copyconstructed:
            return
        # initialize real-time environment
        if initial_time % 3600 != 0.0:
            # ensure that initial_time always at full hour, to avoid
            # measurement bug
            initial_time = (int(initial_time) / 3600) * 3600.0
        self.env = ForwardableRealtimeEnvironment(initial_time=initial_time)

        # initialize power systems
        self.heat_storage = HeatStorage(self.env)
        self.power_meter = PowerMeter(self.env)
        self.cu = CogenerationUnit(
            self.env, self.heat_storage, self.power_meter)
        self.plb = PeakLoadBoiler(self.env, self.heat_storage)
        self.thermal_consumer = ForecastConsumer(self.env, self.heat_storage)
        #self.thermal_consumer = ThermalConsumer(self.env, self.heat_storage)
        self.electrical_consumer = SimpleElectricalConsumer(
            self.env, self.power_meter)

        self.initialize_helpers()

    """returns a copy of the simulation, starting at the timepoint of the old simulation"""
    @classmethod
    def copyconstruct(cls, old_sim):
        new_sim = Simulation(copyconstructed=True)
        # start new simulation at timepoint of old simulation
        env = ForwardableRealtimeEnvironment(
            old_sim.env.now, old_sim.env.measurement_interval)

        new_sim.env = env
        new_sim.env.env_start = old_sim.env.env_start
        new_sim.heat_storage = HeatStorage.copyconstruct(
            env, old_sim.heat_storage)

        new_sim.power_meter = PowerMeter.copyconstruct(
            env, old_sim.power_meter)
        new_sim.thermal_consumer = ForecastConsumer.copyconstruct(
            new_sim.env, old_sim.thermal_consumer, new_sim.heat_storage)
        # new_sim.thermal_consumer = ThermalConsumer.copyconstruct(env,
        #          old_sim.thermal_consumer, new_sim.heat_storage)

        new_sim.electrical_consumer = SimpleElectricalConsumer.copyconstruct(
            env, old_sim.electrical_consumer, new_sim.power_meter)

        new_sim.plb = PeakLoadBoiler.copyconstruct(
            env, old_sim.plb, new_sim.heat_storage)
        new_sim.cu = CogenerationUnit.copyconstruct(
            env, old_sim.cu, new_sim.heat_storage, new_sim.power_meter)

        new_sim.initialize_helpers()

        return new_sim

    def get_systems(self):
        return (
            self.env, self.heat_storage, self.power_meter, self.cu, self.plb,
            self.thermal_consumer, self.electrical_consumer, self.code_executer)

    def forward(self, seconds):
        self.env.forward = seconds

    def initialize_helpers(self):
        # initilize code executer
        self.code_executer = CodeExecuter(self.env, {
            'env': self.env,
            'heat_storage': self.heat_storage,
            'power_meter': self.power_meter,
            'cu': self.cu,
            'plb': self.plb,
            'thermal_consumer': self.thermal_consumer,
            'electrical_consumer': self.electrical_consumer,
            'time': time,
        })

        # initialize BulkProcessor and add it to env
        self.bulk_processor = BulkProcessor(
            self.env, [self.code_executer, self.cu, self.plb, self.heat_storage, self.thermal_consumer, self.electrical_consumer])
        self.env.process(self.bulk_processor.loop())

    def get_total_bilance(self):
        return self.cu.get_operating_costs() + self.plb.get_operating_costs() - \
            self.power_meter.get_reward() + self.power_meter.get_costs()

    def get_measurements(self, measurements, start=None):
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
            ('hs_total_input', [round(self.heat_storage.input_energy, 2)]),
            ('hs_total_output', [round(self.heat_storage.output_energy, 2)]),
            ('hs_empty_count', [round(self.heat_storage.empty_count, 2)]),
            ('total_thermal_consumption',
             [round(self.thermal_consumer.total_consumption, 2)]),
            ('total_electrical_consumption',
             [round(self.electrical_consumer.total_consumption, 2)]),
            ('infeed_reward', [round(self.power_meter.get_reward(), 2)]),
            ('infeed_costs', [round(self.power_meter.get_costs(), 2)]),
            ('total_bilance', [round(self.get_total_bilance(), 2)]),
            ('code_execution_status',
             [1 if self.code_executer.execution_successful else 0])]

        output += measurements.get(start)

        return dict(output)


class SimulationManager:

    def __init__(self, initial_time=None):
        if initial_time != None:
            self.main_simulation = Simulation(initial_time=initial_time)
        else:
            self.main_simulation = Simulation()

        sim = self.main_simulation
        self.measurements = MeasurementCache(
            sim.env, sim.cu, sim.plb, sim.heat_storage,
            sim.thermal_consumer, sim.electrical_consumer)

        sim.env.register_step_function(self.measurements.take)

        self.thread = None

    def simulation_start(self, blocking=False):
        self.thread = SimulationBackgroundRunner(self.main_simulation.env)
        self.thread.start()
        if blocking:
            # wait on forwarding to end
            # cant use thread.join() here, because sim will not stop after
            # forward
            while self.is_main_forwarding():
                time.sleep(0.2)

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

    forecast_for(1,preStartCallback=setStuff)
    @param copy_sim: a simulation to copy, use the main simulation if this is left out
    
    """

    def forecast_for(self, seconds, blocking=False, pre_start_callback=None, copy_sim=None):

        if copy_sim != None:
            new_sim = Simulation.copyconstruct(copy_sim)
        else:
            new_sim = Simulation.copyconstruct(self.main_simulation)

        if pre_start_callback != None:
            pre_start_callback(new_sim)

        measurements = MeasurementCache(
            new_sim.env, new_sim.cu, new_sim.plb, new_sim.heat_storage,
            new_sim.thermal_consumer, new_sim.electrical_consumer)
        new_sim.env.register_step_function(measurements.take)

        new_sim.env.forward = seconds
        new_sim.env.stop_after_forward = True

        if blocking == False:
            thread = SimulationBackgroundRunner(new_sim.env)
            thread.start()
        else:
            t0 = time.time()
            new_sim.env.run()
            print "time for forecast: ", time.time() - t0, " seconds. simulated hours: ", seconds / (60.0 * 60.0)

        return (new_sim, measurements)

    def is_main_forwarding(self):
        return self.main_simulation.env.forward > 0.0

    def forward_main(self, seconds, blocking=False):
        self.main_simulation.env.forward = seconds
        if self.thread == None or not self.thread.isAlive():
            self.simulation_start(blocking)

    def get_main_measurements(self, start=None):
        return self.main_simulation.get_measurements(self.measurements, start)
