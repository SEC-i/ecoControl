import time
from copy import deepcopy

from environment import ForwardableRealtimeEnvironment
from helpers import BulkProcessor, SimulationBackgroundRunner, MeasurementStorage

from systems.code import CodeExecuter
from systems.producers import CogenerationUnit, PeakLoadBoiler
from systems.storages import HeatStorage, PowerMeter
from systems.consumers import ThermalConsumer, SimpleElectricalConsumer


class Simulation(object):

    # initial_time = Tuesday 1st January 2013 12:00:00
    def __init__(self, devices, config, initial_time=1356998400, copyconstructed=False):

        if copyconstructed:
            return
        # initialize real-time environment
        if initial_time % 3600 != 0.0:
            # ensure that initial_time always at full hour, to avoid
            # measurement bug
            initial_time = (int(initial_time) / 3600) * 3600.0
        self.env = ForwardableRealtimeEnvironment(initial_time=initial_time)

        self.devices = self.get_systems_list()

        self.measurements = MeasurementStorage(
            self.env, self.devices)
        self.env.register_step_function(self.measurements.take)

        self.thread = None
        self.running = False

        self.configure(config)

        # initialize BulkProcessor and add it to env
        self.bulk_processor = BulkProcessor(
            self.env, [self.ce, self.cu, self.plb, self.hs, self.tc, self.ec])
        self.env.process(self.bulk_processor.loop())

    def get_systems_list(self):
        system_list = []
        for device in devices:
            for device_type, class_name Device.DEVICE_TYPES:
                if device.device_type = device_type:
                    system_class = getattr(self, class_name)
                    self.devices.append(system_class(self.env))

        # connect power systems
        for device in self.devices:
            if isinstance(device, CogenerationUnit):
                for connected_device in self.devices:
                    if isinstance(device, HeatStorage):
                        device.heat_storage = connected_device
                    elif isinstance(device, PowerMeter):
                        device.power_meter = connected_device
            elif isinstance(device, PeakLoadBoiler) or isinstance(device, ThermalConsumer):
                for connected_device in self.devices:
                    if isinstance(device, HeatStorage):
                        device.heat_storage = connected_device
            elif isinstance(device, ElectricalConsumer):
                for connected_device in self.devices:
                    elif isinstance(device, PowerMeter):
                        device.power_meter = connected_device
            elif isinstance(device, CodeExecuter):
                device.register_local_variables(self.devices)

            if not device.connected():
                raise RuntimeError

        return system_list

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
