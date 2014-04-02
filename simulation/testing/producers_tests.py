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
        # Attention! The assumption of the generator is that the measurement- 
        # intervall ist always one hour
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
        
        self.assertEqual(self.g_generator.get_operating_costs(), \
                            4*gas_price_per_kwh)
        
class CogenerationUnitTest(unittest.TestCase):

    def setUp(self):
        self.env = ForwardableRealtimeEnvironment()
        self.heat_storage = HeatStorageMock()
        self.power_meter = PowerMeter(env=self.env)
        self.cu = CogenerationUnit(env=self.env, \
            heat_storage=self.heat_storage, power_meter=self.power_meter )
        
        
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
        ####
        # test step()
        ####        
        '''step calculates a new workload depending on the mode

    
       
        in dependence of the workload the attributes 
        of the cu:
        the total_electrical_production
        the total_gas_consumption
        total_thermal_production 
        will be altered
        energy_produced of the power_meter will be increased
        input_energy of the heat_storage will be increased
        '''
        
    def test_step_not_running(self):
        self.cu.workload = 1
        self.cu.running = False
        self.cu.thermal_driven = True        
        self.heat_storage.required_energy = 20
        
        self.cu.step()
        
        self.assertEqual(self.cu.workload, 0)
        self.assertEqual(self.cu.total_electrical_production, 0)
        self.assertEqual(self.cu.total_gas_consumption, 0)
        self.assertEqual(self.cu.total_thermal_production, 0)
        self.assertEqual(self.power_meter.energy_produced, 0)
        self.assertEqual(self.heat_storage.input_energy, 0)
        
    def test_step_running_thermal_too_little_workload(self):
        '''if the workload is too low, the cu will be turned off 
        and the effective workload is zero'''
        last_workload = 80
        
        self.initialize_cu_running()
        self.cu.thermal_driven = True        
        self.heat_storage.required_energy = 0.1
        self.power_meter.energy_produced = 0.0
        self.cu.minimal_workload = 40.0
        self.cu.total_electrical_production = 0.0
        self.cu.total_thermal_production = 0.0
        
        self.cu.step()
        
        # caluclates_workload 
        # = required_energy/max_gas_amount_input*thermal_efficiency
        # 0.1/(19*0.65) < 40 (minimal workload)
        
        self.assertEqual(self.cu.workload, 0)
        self.assertEqual(self.cu.total_electrical_production, 0)
        self.assertEqual(self.cu.total_gas_consumption, 0)
        self.assertEqual(self.cu.total_thermal_production, 0)
        self.assertEqual(self.power_meter.energy_produced, 0)
        self.assertEqual(self.heat_storage.input_energy, 0)
              
    def test_step_thermal(self):
        #initialize with valid parameters
        self.initialize_cu_valid()
        self.cu.thermal_driven = True
        # initialize values
        gas_input = 19.0
        thermal_efficiency = 0.65
        electrical_efficiency = 0.25            
        total_electrical_production = 0.0
        total_gas_consumption = 0.0
        total_thermal_production = 0.0
        
        self.initialize_cu_with_values(gas_input, thermal_efficiency, \
            electrical_efficiency, total_electrical_production, \
            total_gas_consumption, total_thermal_production)
            
        self.cu.minimal_workload = 5.0
        required_energy = 5.0
        self.heat_storage.required_energy = required_energy
        self.heat_storage.input_energy = 0
        self.power_meter.energy_produced = 0
        
        self.cu.step()
        
        expected_workload = required_energy/(gas_input*thermal_efficiency)*99 
        # ca 0.4 * 99 = 40.1(%)
        new_gas_consumption = gas_input*expected_workload/99.0 * \
            self.env.step_size/(60*60)
        total_gas_consumption += new_gas_consumption
        
        new_electrical_energy = gas_input*expected_workload/99.0 * \
            electrical_efficiency * self.cu.get_efficiency_loss_factor() * \
            self.env.step_size/(60*60)            
        total_electrical_production += new_electrical_energy
        
        new_thermal_energy = gas_input*expected_workload/99.0 * \
            thermal_efficiency * self.cu.get_efficiency_loss_factor() * \
            self.env.step_size/(60*60)            
        total_thermal_production += new_thermal_energy
        
        expected_energy_produced = self.cu.get_electrical_energy_production()
        expected_input_energy = self.cu.get_thermal_energy_production() 
         
        self.assertEqual(self.cu.workload, expected_workload)
        self.assertEqual(self.cu.total_electrical_production, \
            total_electrical_production)
        self.assertAlmostEqual(self.cu.total_gas_consumption, \
            total_gas_consumption)
        self.assertEqual(self.cu.total_thermal_production, \
            total_thermal_production)
        self.assertEqual(self.power_meter.energy_produced, \
            expected_energy_produced)
        self.assertEqual(self.heat_storage.input_energy, expected_input_energy)
        
    def test_step_electric(self):
        #initialize with valid parameters
        self.initialize_cu_valid()
        
        self.cu.thermal_driven = False 
        
        self.heat_storage.temperature = 0.0
        self.heat_storage.target_temperature = 90.0
        
        # initialize values
        gas_input = 19.0
        thermal_efficiency = 0.65
        electrical_efficiency = 0.25
        total_electrical_production = 0.0
        total_gas_consumption = 0.0
        total_thermal_production = 0.0
        
        self.initialize_cu_with_values(gas_input, thermal_efficiency, \
            electrical_efficiency, total_electrical_production, \
            total_gas_consumption, total_thermal_production)
            
        self.cu.minimal_workload = 0.0
        required_energy = 2.0
        self.power_meter.current_power_consum = required_energy
        self.heat_storage.input_energy = 0
        self.power_meter.energy_produced = 0
        self.cu.step()
        
        expected_workload = required_energy/(gas_input*electrical_efficiency) * \
            99 # ca 0.4 * 99 = 40.1(%)
        new_gas_consumption = gas_input*expected_workload/99.0 * \
        self.env.step_size/(60*60)
        total_gas_consumption += new_gas_consumption
        
        new_electrical_energy = gas_input*expected_workload/99.0 * \
            electrical_efficiency * self.cu.get_efficiency_loss_factor() * \
            self.env.step_size/(60*60)            
        total_electrical_production += new_electrical_energy
        
        new_thermal_energy = gas_input*expected_workload/99.0 * \
            thermal_efficiency * self.cu.get_efficiency_loss_factor() * \
            self.env.step_size/(60*60)            
        total_thermal_production += new_thermal_energy   
        
        expected_energy_produced = self.cu.get_electrical_energy_production()
        expected_input_energy = self.cu.get_thermal_energy_production() 
         
        self.assertEqual(self.cu.workload, expected_workload)
        self.assertEqual(self.cu.total_electrical_production, \
            total_electrical_production)
        self.assertAlmostEqual(self.cu.total_gas_consumption, \
            total_gas_consumption)
        self.assertAlmostEqual(self.cu.total_thermal_production, \
            total_thermal_production)
        self.assertEqual(self.power_meter.energy_produced, \
            expected_energy_produced)
        self.assertEqual(self.heat_storage.input_energy, expected_input_energy)
        
        
    def test_step_turn_on_forbidden(self):
        ''' the cu musn't be paused (self_offtime active)'''
        #initialize with valid parameters
        self.cu.running = True
        
        # the offtime is effective!
        now = self.env.now
        self.cu.off_time = now + 1
        
        self.cu.thermal_driven = False 
        
        self.heat_storage.temperature = 0.0
        self.heat_storage.target_temperature = 90.0
        
        # initialize values
        gas_input = 19.0
        thermal_efficiency = 0.65
        electrical_efficiency = 0.25
        total_electrical_production = 0.0
        total_gas_consumption = 0.0
        total_thermal_production = 0.0
        self.initialize_cu_with_values(gas_input, thermal_efficiency, \
            electrical_efficiency, total_electrical_production, \
            total_gas_consumption, total_thermal_production)
        required_energy = 2.0
        self.power_meter.current_power_consum = required_energy
        self.heat_storage.input_energy = 0
        self.power_meter.energy_produced = 0
        
        self.cu.step()
                
        self.assertEqual(self.cu.workload, 0)
        self.assertEqual(self.cu.total_electrical_production, 0)
        self.assertEqual(self.cu.total_gas_consumption, 0)
        self.assertEqual(self.cu.total_thermal_production, 0)
        self.assertEqual(self.power_meter.energy_produced, 0)
        self.assertEqual(self.heat_storage.input_energy, 0)
        
    def test_step_turn_target_temperature_reached(self):
        '''if the heat storage is too hot, the cu musn't produce energy
            although there is a demand for electrical energy'''
        self.initialize_cu_valid()
        self.cu.thermal_driven = False
        self.heat_storage.temperature = 10.0
        self.heat_storage.target_temperature = 10.0
        
        # initialize values
        gas_input = 19.0
        thermal_efficiency = 0.65
        electrical_efficiency = 0.25
        total_electrical_production = 0.0
        total_gas_consumption = 0.0
        total_thermal_production = 0.0
        self.initialize_cu_with_values(gas_input, thermal_efficiency, \
            electrical_efficiency, total_electrical_production, \
            total_gas_consumption, total_thermal_production)
        required_energy = 2.0
        self.power_meter.current_power_consum = required_energy
        self.heat_storage.input_energy = 0
        self.power_meter.energy_produced = 0
        
        self.cu.step()
                
        self.assertEqual(self.cu.workload, 0)
        self.assertEqual(self.cu.total_electrical_production, 0)
        self.assertEqual(self.cu.total_gas_consumption, 0)
        self.assertEqual(self.cu.total_thermal_production, 0)
        self.assertEqual(self.power_meter.energy_produced, 0)
        self.assertEqual(self.heat_storage.input_energy, 0)
        
    def test_step_workload_too_high(self):
        '''if the workload is too high, the cu will be running at a workload 
        of 99 %'''
        
        #initialize with valid parameters
        self.initialize_cu_valid()
        
        self.cu.thermal_driven = False 
        
        self.heat_storage.temperature = 0.0
        self.heat_storage.target_temperature = 90.0
        
        # initialize values
        gas_input = 19.0
        thermal_efficiency = 0.65
        electrical_efficiency = 0.25
        total_electrical_production = 0.0
        total_gas_consumption = 0.0
        total_thermal_production = 0.0
        
        self.initialize_cu_with_values(gas_input, thermal_efficiency, \
            electrical_efficiency, total_electrical_production, \
            total_gas_consumption, total_thermal_production)
            
        self.cu.minimal_workload = 0.0
        required_energy = 500.0
        self.power_meter.current_power_consum = required_energy
        self.heat_storage.input_energy = 0
        self.power_meter.energy_produced = 0
        self.cu.step()
        
        expected_workload = 99
        new_gas_consumption = gas_input*expected_workload/99.0 * \
            self.env.step_size/(60*60)
        total_gas_consumption += new_gas_consumption
        
        new_electrical_energy = gas_input*expected_workload/99.0 * \
            electrical_efficiency \
            * self.cu.get_efficiency_loss_factor() * self.env.step_size/(60*60)            
        total_electrical_production += new_electrical_energy
        
        new_thermal_energy = gas_input*expected_workload/99.0 * \
            thermal_efficiency * self.cu.get_efficiency_loss_factor() * \
            self.env.step_size/(60*60)            
        total_thermal_production += new_thermal_energy   
        
        expected_energy_produced = self.cu.get_electrical_energy_production()
        expected_input_energy = self.cu.get_thermal_energy_production() 
         
        self.assertEqual(self.cu.workload, expected_workload)
        self.assertEqual(self.cu.total_electrical_production, \
            total_electrical_production)
        self.assertAlmostEqual(self.cu.total_gas_consumption, \
            total_gas_consumption)
        self.assertAlmostEqual(self.cu.total_thermal_production, \
            total_thermal_production)
        self.assertEqual(self.power_meter.energy_produced, \
            expected_energy_produced)
        self.assertEqual(self.heat_storage.input_energy, expected_input_energy)
        
        
    def test_get_electrical_energy_production(self):
        # the method should return the energy produced in one time intervall
        self.cu.current_electrical_production = 20.0 # Energy per hour
        self.env.steps_per_measurement = 2.0 # twice per hour
        expected_energy = 20.0/2.0
        
        result_energy = self.cu.get_electrical_energy_production()
            
        self.assertEqual(expected_energy, result_energy)
        
    def test_get_thermal_energy_production(self):
        # the method should return the energy produced in one time intervall
        self.cu.current_thermal_production = 20.0 # Energy per hour
        self.env.steps_per_measurement = 2.0 # twice per hour
        expected_energy = 20.0/2.0
        
        result_energy = self.cu.get_thermal_energy_production()
            
        self.assertEqual(expected_energy, result_energy)
        
    def test_calculate_new_workload(self):
        # calculates a workload
        # it considers overwrites workload and 
        # the mode
        # the offtime
        
        
        #consider mode thermal
        self.heat_storage.required_energy = 3
        expected_workload = self.cu.get_calculated_workload_thermal()
        self.cu.thermal_driven = True
        calculated_workload = self.cu.calculate_new_workload()
        self.assertEqual(calculated_workload, expected_workload, \
            "thermal workload is wrong")
        
        #consider mode electric
        self.heat_storage.target_temperature = 1000
        self.power_meter.current_power_consum = 3
        expected_workload = self.cu.get_calculated_workload_electric()
        self.cu.thermal_driven = False
        calculated_workload = self.cu.calculate_new_workload()
        self.assertEqual(calculated_workload, expected_workload, \
                            "electrical workload is wrong expected: \
                            {0}. got: {1}"\
                            .format(expected_workload, calculated_workload))
        
        #consider overwrite of workload
        self.heat_storage.required_energy = 3
        expected_workload = self.cu.get_calculated_workload_thermal()
        self.cu.thermal_driven = True
        self.cu.overwrite_workload = 25.0
        calculated_workload = self.cu.calculate_new_workload()
        self.assertEqual(calculated_workload, 25.0, "overwritten workload \
                            is wrong expected: {0}. got: {1}"\
                            .format(25.0, calculated_workload))
        
        
    def test_get_operating_costs(self):
        # are sum of gas_costs and maintenance
        self.cu.total_gas_consumption = 6.0
        self.cu.total_electrical_production = 3
        # needed, because the maintenance_costs are calculated 
        # out of the electrical_production
        
        result = self.cu.get_operating_costs()
        
        self.assertGreater(result, gas_price_per_kwh*6.0) 
        # greater because of additional maintenance costs
        
    def test_get_efficiency_loss_factor(self):
        # given efficiency is reached only on maximum workload
        # at minumum workload the efficiency is decreased with
        # max_efficiency_loss
        # the method returns the remaining efficiency
        self.cu.workload = 40
        self.cu.minimal_workload = 40
        self.cu.max_efficiency_loss = 5
        
        calculated_loss = self.cu.get_efficiency_loss_factor()
        
        self.assertEqual(calculated_loss, 1-0.05)
     
    def test_get_calculated_workload_thermal(self):
        # the function returns the needed workload based on the thermal demand
        # dont't know why but the workload is mapped to 0-99
        required_energy = 5
        gas_input = 20 # unit is energy: kWh
        thermal_efficiency = 0.6
        
        self.heat_storage.required_energy = required_energy
        self.cu.max_gas_input = gas_input
        self.cu.thermal_efficiency = thermal_efficiency
        
        max_energy = thermal_efficiency*gas_input
        expected_workload = required_energy/max_energy *99.0 
        
        calculated_result = self.cu.get_calculated_workload_thermal()
        
        self.assertEqual(calculated_result, expected_workload) 
          
    def test_get_calculated_workload_electric(self):
        # the function returns the needed workload based on the electric demand
        # dont't know why but the workload is mapped to 0-99
        self.heat_storage.target_temperature = 100
        self.heat_storage.temperature = 0
        
        required_energy = 5.0
        gas_input = 20.0 # unit is energy: kWh
        electrical_efficiency = 0.6
        minimal_workload = 20.0
        
        self.power_meter.current_power_consum = required_energy
        self.cu.max_gas_input = gas_input
        self.cu.electrical_efficiency = electrical_efficiency
        
        max_energy = electrical_efficiency*gas_input
        expected_workload = required_energy/max_energy   
        
        calculated_result = self.cu.get_calculated_workload_electric()
        
        self.assertAlmostEqual(calculated_result, expected_workload*99.0) 
       # self.assertAlmostEqual(calculated_result, expected_workload)
        
    def test_get_calculated_workload_electric_heat_storage_filled(self):
        # if the target_temperature of the heat-storage is reached
        # the workload has to be zero 
        self.heat_storage.target_temperature = 100
        self.heat_storage.temperature = 100
        
        self.power_meter.current_power_consum = 5.0
        self.cu.max_gas_input = 20.0 # unit is energy: kWh
        self.cu.electrical_efficiency = 0.6
    
        calculated_result = self.cu.get_calculated_workload_electric()
        
        self.assertAlmostEqual(calculated_result, 0)
     
    def initialize_cu_valid(self):
        self.cu.running = True
        now = self.env.now
        self.cu.off_time = now - 1
        
    def initialize_cu_running(self):
        self.cu.running = True
        self.cu.max_gas_input = 19.0
        self.cu.thermal_efficiency = 0.65
        self.cu.total_gas_consumption = 0.0
        self.cu.minimal_workload = 40.0
        
    def initialize_cu_with_values(self, gas_input, thermal_efficiency, \
            electrical_efficiency, total_electrical_production, \
            total_gas_consumption, total_thermal_production):
        self.cu.max_gas_input = gas_input
        self.cu.thermal_efficiency = thermal_efficiency
        self.cu.electrical_efficiency = electrical_efficiency
        self.cu.total_electrical_production = total_electrical_production
        self.cu.total_gas_consumption = total_gas_consumption
        self.cu.total_thermal_production = total_thermal_production
        
'''       
    def test_update_parameters_power_on_count(self):
        # the bhkw was turned off
        # the new workload is sane
        # and the bhkw can be turned on again
        # the bhkw should increment the power on count
        precalculated_workload = 35 
        power_on_count = 0
        self.cu.minimal_workload = 20
        self.cu.workload = 0
        self.cu.power_on_count = power_on_count
        now = self.env.now
        self.cu.off_time = now - 1
        
        self.cu.update_parameters(precalculated_workload)
        
        self.assertEqual(self.cu.power_on_count, power_on_count+1)

    def test_update_parameters_too_low_workload(self):
        precalculated_workload = 10 
        self.cu.minimal_workload = 20

        now = self.env.now
        self.cu.off_time = now - 1
        
        self.cu.update_parameters(precalculated_workload)
        
        self.assertEqual(self.cu.workload, 0)
        
    def test_update_parameters_workload_off_time_effective(self):
        precalculated_workload = 10 
        self.cu.minimal_workload = 20

        now = self.env.now
        self.cu.off_time = now + 1
        
        self.cu.update_parameters(precalculated_workload)
        
        self.assertEqual(self.cu.workload, 0)
        
    def test_update_parameters_normal_workload(self):
        precalculated_workload = 35 
        self.cu.minimal_workload = 20

        now = self.env.now
        self.cu.off_time = now - 1
        
        self.cu.update_parameters(precalculated_workload)
        
        self.assertEqual(self.cu.workload, precalculated_workload)
        
    def test_update_parameters_too_high_workload(self):
        precalculated_workload = 109
        #assumption: max workload: 99

        now = self.env.now
        self.cu.off_time = now - 1
        
        self.cu.update_parameters(precalculated_workload)
        
        self.assertEqual(self.cu.workload, 99)
        
    def test_update_parameters_normal_workload_consumption_production(self):
        precalculated_workload = 35 
        self.cu.minimal_workload = 20
        
        max_gas_input = 20
        self.cu.max_gas_input = max_gas_input
        
        electrical_efficiency = 0.2
        thermal_effiency = 0.7
        
        now = self.env.now
        self.cu.off_time = now - 1
        
        total_hours_of_operation = 1
        self.cu.total_hours_of_operation = total_hours_of_operation
        
        self.cu.update_parameters(precalculated_workload)
        
        # assumption: max_gas_input is energy per stepsize
        # but the unit of current_gas_consumption is power
        expected_gas_consumption = (precalculated_workload*max_gas_input)/self.env.step_size
        efficiency_loss = self.cu.get_efficiency_loss_factor()
        expected_electrical_production = expected_gas_consumption * electrical_efficiency* efficiency_loss
        expected_thermal_production = expected_gas_consumption * thermal_effiency* efficiency_loss
        # assumption: self.env.step_size are seconds per step
        expected_hours_of_operation = total_hours_of_operation + self.env.step_size/(60.0*60.0)
        
        #the following will fail, the method uses an incomprehensible 0.99 factor
        self.assertEqual(self.cu.current_gas_consumption, \
            expected_gas_consumption)
        self.assertEqual(self.cu.current_electrical_production, \
            expected_electrical_production)
        self.assertEqual(self.cu.current_thermal_production, \
            expected_thermal_production)
        self.assertEqual(self.cu.total_hours_of_operation, expected_hours_of_operation)


    def test_update_parameters_increase_hours_of_operation(self):
        precalculated_workload = 35 
        self.cu.minimal_workload = 20
        
        now = self.env.now
        self.cu.off_time = now - 1
        
        total_hours_of_operation = 1
        self.cu.total_hours_of_operation = total_hours_of_operation
        
        self.cu.update_parameters(precalculated_workload)
    
        # assumption: self.env.step_size are seconds per step
        expected_hours_of_operation = total_hours_of_operation + self.env.step_size/(60.0*60.0)
        
        self.assertEqual(self.cu.total_hours_of_operation, expected_hours_of_operation)
      
    def test_update_parameters_hours_of_operation_unchanged_workload_too_low(self):
        # workload too low
        precalculated_workload = 10 
        self.cu.minimal_workload = 20
        
        now = self.env.now
        self.cu.off_time = now - 1
        
        total_hours_of_operation = 1
        self.cu.total_hours_of_operation = total_hours_of_operation
        
        self.cu.update_parameters(precalculated_workload)
        
        self.assertEqual(self.cu.total_hours_of_operation, total_hours_of_operation)
        
    def test_update_parameters_hours_of_operation_unchanged_offtime_effective(self):
        precalculated_workload = 30
        self.cu.minimal_workload = 20
        
        #off-time is effective
        now = self.env.now
        self.cu.off_time = now + 1
        
        total_hours_of_operation = 1
        self.cu.total_hours_of_operation = total_hours_of_operation
        
        self.cu.update_parameters(precalculated_workload)
        
        self.assertEqual(self.cu.total_hours_of_operation, total_hours_of_operation)

    #def test_consume_gas(self):
    #pass'''
        

if __name__ == '__main__':
    unittest.main()
