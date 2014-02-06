import random
import unittest
import bhkw
import time
from simulation import BHKW_Simulation

class TestBHKW(unittest.TestCase):

    def setUp(self):
        #BHWK.TIME_STEP = 0.1
        self.simulation = BHKW_Simulation()
        self.simulation.start()
        #self.simulation.bhkw = bhkw.bhkw(0)
    
    def tearDown(self):
        self.simulation.immediate_off()

    def test_start_up(self):
        self.assertEqual(self.simulation.get_workload(0), 0)
        self.simulation.bhkw.turn_on()
        #assert, that bhkw doesnt immediatly work at deisred power
        self.assertTrue(self.simulation.get_workload(0) != 75)
        time.sleep(1.0)
        # but workload should still rise a bit
        self.assertTrue(self.simulation.get_workload(0) != 0)

        #just to avoid interference with other tests
        self.simulation.immediate_off()

    def test_turn_off(self):
        #set values directly
        self.simulation.bhkw.current_workload.value = 20.0
        self.simulation.bhkw.calculate_parameters(20.0)

        self.simulation.bhkw.turn_off()
        # with timestep= 0.01, turning off takes approx 2.7 sec
        time.sleep(3.0)

        self.assertEqual(self.simulation.bhkw.current_workload.value, 0.0)

    def test_measured_data(self):
        # values from vitobloc_200_EM datasheet
        self.simulation.bhkw.calculate_parameters(50.0)
        self.assertEqual(self.simulation.bhkw.current_electrical_power.value, 25)

        self.simulation.bhkw.calculate_parameters(75.0)
        self.assertEqual(self.simulation.bhkw.current_thermal_power.value, 64)

    def test_mapping(self):
        self.simulation.bhkw.current_gasinput.value = 145.0 # maximum
        
        self.assertEqual(self.simulation.bhkw.get_mapped_sensor(sID=3).value, 100.0)

    def test_random_variations(self):
        self.simulation.bhkw.current_workload.value = 50.0
        values = []
        for i in range(100):
            values.append(self.simulation.bhkw.current_workload.value)#should randomly change
            time.sleep(0.01)
        self.assertTrue(self.simulation.bhkw.current_workload.value != 50.0*100)



#TODO fix tests

# if __name__ == '__main__':
#     unittest.main()
