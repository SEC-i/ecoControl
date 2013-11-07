import random
import unittest
import BHKW
import time

class TestBHKW(unittest.TestCase):

    def setUp(self):
        #BHWK.TIME_STEP = 0.1
        self.BHKW = BHKW.BHKW(0)
    
    def tearDown(self):
        self.BHKW.immediateOff()

    def testStartUp(self):
        self.assertEqual(self.BHKW.currentWorkload.value, 0)
        self.BHKW.turnOn()
        #assert, that BHKW doesnt immediatly work at deisred power
        self.assertTrue(self.BHKW.currentWorkload.value != 75)
        time.sleep(0.1)
        # but workload should still rise a bit
        self.assertTrue(self.BHKW.currentWorkload.value != 0)

        #just to avoid interference with other tests
        self.BHKW.immediateOff()

    def testTurnOff(self):
        #set values directly
        self.BHKW.currentWorkload.value = 20.0
        self.BHKW._calculate(20.0)

        self.BHKW.turnOff()
        # with timestep= 0.01, turning off takes approx 2.7 sec
        time.sleep(3.0)

        self.assertEqual(self.BHKW.currentWorkload.value,0.0)

    def testMeasuredData(self):
        # values from vitobloc_200_EM datasheet
        self.BHKW._calculate(50.0)
        self.assertEqual(self.BHKW.currentElectricalPower.value,25)

        self.BHKW._calculate(75.0)
        self.assertEqual(self.BHKW.currentThermalPower.value, 64)

    def testMapping(self):
        self.BHKW.currentGasInput.value = 145.0 # maximum
        
        self.assertEqual(self.BHKW.getMappedSensor(sID=3).value, 100.0)

    def testRandomVariations(self):
        self.BHKW.currentWorkload.value = 50.0
        values = []
        for i in range(100):
            values.append(self.BHKW.currentWorkload.value)#should randomly change
            time.sleep(0.01)
        self.assertTrue(self.BHKW.currentWorkload.value != 50.0 * 100)





if __name__ == '__main__':
    unittest.main()
