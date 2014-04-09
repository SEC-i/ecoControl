import unittest
import time
import os
parent_directory = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__)))
os.sys.path.insert(0, parent_directory)
from systems.consumers import ThermalConsumer
from environment import ForwardableRealtimeEnvironment
from systems.storages import HeatStorage

class ThermalConsumerTests(unittest.TestCase):
    def setUp(self):
        env = ForwardableRealtimeEnvironment()
        heat_storage = HeatStorage(env)
        self.consumer = ThermalConsumer(env, heat_storage)
 
    '''def test_step(self):
       # pass
        verbrauch wird berechnet 
        total_consumption wird erhoeht
        energy wird aus dem Heatstorage entnommen
        '''
    '''def test_simulate_consumption(self):
        # sets self.target_temperature(the demand of warmth)
        # dependent on the current time
        # sets self.room_power power,
        # the current power of the heating of the room

        # self.calculate_room_temperature()
        #    #sets self.temperature_room

        # sets self.current_power
        # encreases the current power if its too cold, else decreases
        it'''
    
    def test_simulate_consumption_increase_current_power(self):
        '''the current_power should be increased if the current temperature 
        is below the target temperature'''
        self.consumer.temperature_room = 0
        self.consumer.target_temperature = 30
        last_current_power = 20
        self.consumer.current_power = last_current_power
        
        self.consumer.simulate_consumption()
        
        self.assertGreater(self.consumer.current_power, last_current_power)
        
    def test_simulate_consumption_decrease_current_power(self):
        '''the current_power should be decreased if the current temperature 
        is below the target temperature'''
        self.consumer.temperature_room = 30
        self.consumer.target_temperature = 0
        last_current_power = 20
        self.consumer.current_power = last_current_power
        
        self.consumer.simulate_consumption()
        
        self.assertLess(self.consumer.current_power, last_current_power)
        
        
    def test_room_power_simulate_consumption(self):
        # sets self.room_power power,
        # the current power of the heating of the room
        # the value comes from the former current_power
    
        '''def test_temperature_room(self):
        # during simulate_consumption
        # set by calculate_room_temperature
        # depends on room_power,
        # heat capacity
        # time delta'''
        
    def test_target_temperature_simulate_consumption(self):
        '''the target temperature of the consumer should be set
        according to the daily demand'''
        daily_demand = [19, 19, 3, 19, 6, 19, 19, 20, 21, 20, 20, 21, 
            20, 21, 21, 21, 21, 22, 22, 5, 22, 22, 21, 19]
    
        env = ForwardableRealtimeEnvironment()
        heat_storage = HeatStorage(env)
        consumer = ThermalConsumer(env, heat_storage)
        consumer.daily_demand = daily_demand
            
        for current_time in range(24): 
            time_in_seconds = current_time*60*60
            env = ForwardableRealtimeEnvironment(initial_time=time_in_seconds)
            consumer.env = env
            consumer.target_temperature = 0
        
            consumer.simulate_consumption()

            expected_temperature = daily_demand[current_time]
            self.assertEqual(consumer.target_temperature, expected_temperature)
        
        '''def test_calculate_room_temperature(self):
        # sets the room_temperature with respect to
        # the current temperature,
        # the heat_capacity       
        # the current power (consuption) of the room'''
        
if __name__ == '__main__':
    unittest.main()
