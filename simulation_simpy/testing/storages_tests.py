import unittest

# add parent folder to path
import os
parent_directory = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__)))
os.sys.path.insert(0, parent_directory)

from systems.storages import HeatStorage, PowerMeter
from environment import ForwardableRealtimeEnvironment


class HeatStorageTests(unittest.TestCase):

    def setUp(self):
        self.env = ForwardableRealtimeEnvironment()
        self.heat_storage = HeatStorage(env=self.env)

    def test_add_and_consume_energy(self):
        self.heat_storage.add_energy(123)
        self.assertEqual(
            self.heat_storage.energy_stored(), 123 / self.env.accuracy)
        self.heat_storage.consume_energy(123)
        self.assertEqual(self.heat_storage.energy_stored(), 0)

        for i in range(int(self.env.accuracy)):
            self.heat_storage.add_energy(543)

        self.assertEqual(int(self.heat_storage.energy_stored()), 543)

    # def test_level(self):
    #     self.assertEqual(self.heat_storage.level(), 0)
    #     energy = self.heat_storage.capacity * self.env.accuracy
    #     self.heat_storage.add_energy(energy)
    #     self.assertEqual(self.heat_storage.level(), 99)

    # def test_undersupplied(self):
    #     self.assertTrue(self.heat_storage.undersupplied())
    #     energy = self.heat_storage.undersupplied_threshold * self.env.accuracy
    #     self.heat_storage.add_energy(energy)
    #     self.assertFalse(self.heat_storage.undersupplied())


class PowerMeterTests(unittest.TestCase):

    def setUp(self):
        self.env = ForwardableRealtimeEnvironment()
        self.power_meter = PowerMeter(env=self.env)

    def test_add_energy(self):
        self.power_meter.add_energy(123)
        self.assertEqual(
            self.power_meter.energy_produced, 123 / self.env.accuracy)
        self.assertEqual(self.power_meter.total_fed_in_electricity, 0)
        self.power_meter.consume_energy(0)
        self.assertEqual(self.power_meter.total_fed_in_electricity, 123 / self.env.accuracy)


if __name__ == '__main__':
    unittest.main()
