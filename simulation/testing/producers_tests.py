import unittest

# add parent folder to path
import os
parent_directory = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__)))
os.sys.path.insert(0, parent_directory)
from environment import ForwardableRealtimeEnvironment
from systems.producers import CogenerationUnit, GasPoweredGenerator
from systems.storages import HeatStorage, PowerMeter
from mocks import HeatStorageMock

from systems.data import gas_price_per_kwh

class GasPoweredGeneratorTests(unittest.TestCase):

    def setUp(self):
        self.env = ForwardableRealtimeEnvironment()
        self.g_generator = GasPoweredGenerator(env=self.env)
        
    def test_gas_powered_generator_creation(self):
        self.assertTrue(self.g_generator.running)

        self.assertEqual(self.g_generator.workload, 0)
        self.assertEqual(self.g_generator.current_gas_consumption, 0)
        self.assertEqual(self.g_generator.current_thermal_production, 0) 
        self.assertEqual(self.g_generator.total_gas_consumption, 0.0)
        self.assertEqual(self.g_generator.total_thermal_production, 0.0)

        self.assertEqual(self.g_generator.total_hours_of_operation, 0)
        self.assertEqual(self.g_generator.power_on_count, 0)
    
    def test_start(self):
        self.g_generator.running = False
        self.g_generator.start()
        
        self.assertTrue(self.g_generator.running)    
        
        
    def test_stop(self):
        self.g_generator.running = True
        self.g_generator.stop()
        
        self.assertFalse(self.g_generator.running)
    
    def test_consume_gas(self):
        # Attention! The assumption of the generator is that the measurement intervall ist always one hour
        # Otherwise the values are physically wrong because their unit is kWh!
         self.g_generator.total_gas_consumption = 0.0
         self.g_generator.total_thermal_production = 0.0
         self.g_generator.current_gas_consumption = 3.0
         self.g_generator.current_thermal_production = 4.0
         self.env.steps_per_measurement = 20.0
         
         self.g_generator.consume_gas()
         
         self.assertEqual(self.g_generator.total_gas_consumption, 3/20.0)
         self.assertEqual(self.g_generator.total_thermal_production, 4/20.0)
        
    def test_get_operating_costs(self):
        self.g_generator.total_gas_consumption = 4
        
        self.assertEqual(self.g_generator.get_operating_costs(), 4*gas_price_per_kwh)
        
class CogenerationUnitTest(unittest.TestCase):

    def setUp(self):
        self.env = ForwardableRealtimeEnvironment()
        self.heat_storage = HeatStorageMock()
        self.power_meter = PowerMeter(env=self.env)
        self.cu = CogenerationUnit(env=self.env, heat_storage=self.heat_storage, power_meter=self.power_meter )
        
        
    def test_creation(self):
        self.assertGreaterEqual(self.cu.workload, 0)
        self.assertGreater(self.cu.max_gas_input, 0)
        self.assertTrue(0 <= self.cu.electrical_efficiency <= 1)
        self.assertTrue(0 <=  self.cu.thermal_efficiency <= 1)
        
        self.assertTrue(0 <= self.cu.max_efficiency_loss <= 1)
        self.assertGreater(self.cu.maintenance_interval, 0)
        
        self.assertTrue(0 <= self.cu.minimal_workload <= 100)

        self.assertGreaterEqual(self.cu.minimal_off_time, 0)
        
        self.assertEqual(self.cu.off_time, self.env.now)

        self.assertEqual(self.cu.current_electrical_production, 0)
        self.assertEqual(self.cu.total_electrical_production, 0) 
        self.assertTrue(self.cu.thermal_driven)
        self.assertGreaterEqual(self.cu.electrical_driven_minimal_production, 0),

        self.assertIsNone(self.cu.overwrite_workload)
        
    def test_step_not_running(self):
        self.cu.workload = 1
        self.cu.running = False
        
        self.cu.step()
        
        self.assertEqual(self.cu.workload, 0)
        
    def test_step_running_thermal_turn_up_workload(self):
        last_workload = 50
        
        self.initialize_cu_running()
        self.cu.thermal_driven = True
        self.cu.workload = last_workload
        self.power_meter.energy_produced = 0.0
        self.heat_storage.required_energy = 10
        
        self.cu.step()
        
        # expected_workload = required_energy/max_gas_amount_input*thermal_efficiency
        # expected_workload ca 0.81, which is greater than the last workload of 50%
        # and greater than the minimal workload.
        
        self.assertGreater(self.cu.workload, last_workload)
        self.assertGreater(self.cu.total_gas_consumption, 0)
        self.assertGreater(self.power_meter.energy_produced, 0)
        
    def test_step_running_thermal_turn_down_workload(self):
        last_workload = 80
        
        self.initialize_cu_running()
        self.cu.thermal_driven = True
        self.cu.workload = last_workload
        self.power_meter.energy_produced = 0.0
        self.heat_storage.required_energy = 5
        
        self.cu.step()
        
        # expected_workload = required_energy/max_gas_amount_input*thermal_efficiency
        # expected_workload ca 0.40, which is less than the last workload of 80%
        # and greater than the minimal workload.
        
        self.assertLess(self.cu.workload, last_workload)
        self.assertGreater(self.cu.total_gas_consumption, 0) 
        self.assertGreater(self.power_meter.energy_produced, 0)
        
    def test_step_running_thermal_too_little_workload(self):
        last_workload = 80
        
        self.initialize_cu_running()
        self.cu.workload = last_workload
        self.cu.thermal_driven = True        
        self.heat_storage.required_energy = 0
        self.power_meter.energy_produced = 0.0
        
        self.cu.step()
        
        # expected_workload = required_energy/max_gas_amount_input*thermal_efficiency
        # expected_workload ca 0.40, which is less than the last workload of 80%
        # and greater than the minimal workload.
        
        self.assertEqual(self.cu.workload, 0)
        self.assertEqual(self.cu.total_gas_consumption, 0)
        self.assertEqual(self.power_meter.energy_produced, 0)
        
    
    def initialize_cu_running(self):
        self.cu.running = True
        self.cu.max_gas_input = 19.0
        self.cu.thermal_efficiency = 0.65
        self.cu.total_gas_consumption = 0.0
        self.cu.minimal_workload = 40.0
        
    
        

if __name__ == '__main__':
    unittest.main()
