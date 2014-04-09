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
        
    def test_target_temperature_simulate_consumption(self):
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
