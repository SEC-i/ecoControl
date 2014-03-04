import unittest

# add parent folder to path
import os
parent_directory = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__)))
os.sys.path.insert(0, parent_directory)
from environment import ForwardableRealtimeEnvironment
from systems.producers import GasPoweredGenerator

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

if __name__ == '__main__':
    unittest.main()
