import random
import unittest
import BHKW
import time
from Simulation import BHKW_Simulation

class TestBHKW(unittest.TestCase):

    def setUp(self):
        #BHWK.TIME_STEP = 0.1
        self.simulation = BHKW_Simulation()
        self.simulation.start()
        #self.simulation.BHKW = BHKW.BHKW(0)
    
    def tearDown(self):
        self.simulation.immediateOff()

    def testStartUp(self):
        self.assertEqual(self.simulation.getWorkload(0), 0)
        self.simulation.BHKW.turnOn()
        #assert, that BHKW doesnt immediatly work at deisred power
        self.assertTrue(self.simulation.getWorkload(0) != 75)
        time.sleep(1.0)
        # but workload should still rise a bit
        self.assertTrue(self.simulation.getWorkload(0) != 0)

        #just to avoid interference with other tests
        self.simulation.immediateOff()

    def testTurnOff(self):
        #set values directly
        self.simulation.BHKW.currentWorkload.value = 20.0
        self.simulation.BHKW.calculateParameters(20.0)

        self.simulation.BHKW.turnOff()
        # with timestep= 0.01, turning off takes approx 2.7 sec
        time.sleep(3.0)

        self.assertEqual(self.simulation.BHKW.currentWorkload.value,0.0)

    def testMeasuredData(self):
        # values from vitobloc_200_EM datasheet
        self.simulation.BHKW.calculateParameters(50.0)
        self.assertEqual(self.simulation.BHKW.currentElectricalPower.value,25)

        self.simulation.BHKW.calculateParameters(75.0)
        self.assertEqual(self.simulation.BHKW.currentThermalPower.value, 64)

    def testMapping(self):
        self.simulation.BHKW.currentGasInput.value = 145.0 # maximum
        
        self.assertEqual(self.simulation.BHKW.getMappedSensor(sID=3).value, 100.0)

    def testRandomVariations(self):
        self.simulation.BHKW.currentWorkload.value = 50.0
        values = []
        for i in range(100):
            values.append(self.simulation.BHKW.currentWorkload.value)#should randomly change
            time.sleep(0.01)
        self.assertTrue(self.simulation.BHKW.currentWorkload.value != 50.0 * 100)





if __name__ == '__main__':
    unittest.main()
