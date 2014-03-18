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
        self.cu.running = False
        
        self.cu.step()
        
        self.assertEqual(self.cu.workload, 0)
        self.fail('finish test')
        
    def test_step_running_thermal(self):
        self.cu.running = True
        self.cu.workload = 50
        self.cu.thermal_driven = True
        self.heat_storage.required_energy = 10
        
        # usage = 
        # anahnd aktueller workload und modus ablesen
        # waermebedarf von storage erfrageb
        # wie viel gas verbraucht wird
        # wie viel Stom und waerme produziert wird.  
        

if __name__ == '__main__':
    unittest.main()
