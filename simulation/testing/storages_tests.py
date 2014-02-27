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
        self.hs = HeatStorage(env=self.env)

    def test_add_and_consume_energy(self):
        self.hs.add_energy(12.3)
        self.assertEqual(
            self.hs.energy_stored(), 12.3 / self.env.steps_per_measurement)
        self.hs.consume_energy(12.3)
        self.assertEqual(self.hs.energy_stored(), 0)

        for i in range(int(self.env.steps_per_measurement)):
            self.hs.add_energy(54.3)

        self.assertTrue(abs(self.hs.energy_stored() - 54.3) < 0.01)

    def test_undersupplied(self):
        self.assertTrue(self.hs.undersupplied())

        temperature_delta = self.hs.min_temperature - self.hs.base_temperature
        min_energy_needed = temperature_delta * \
            self.hs.capacity * self.hs.specific_heat_capacity
        self.hs.add_energy(min_energy_needed * self.env.steps_per_measurement)
        self.assertFalse(self.hs.undersupplied())
        self.hs.consume_energy(1)
        self.assertTrue(self.hs.undersupplied())
        self.hs.add_energy(1)
        self.assertFalse(self.hs.undersupplied())

    def test_overload(self):
        self.hs.add_energy(
            self.hs.get_energy_capacity() * self.env.steps_per_measurement)
        self.assertEqual(
            self.hs.energy_stored(), self.hs.get_energy_capacity())
        # try to max-fill it another time
        self.hs.add_energy(
            self.hs.get_energy_capacity() * self.env.steps_per_measurement)
        self.assertEqual(
            self.hs.energy_stored(), self.hs.get_energy_capacity())


class PowerMeterTests(unittest.TestCase):

    def setUp(self):
        self.env = ForwardableRealtimeEnvironment()
        self.power_meter = PowerMeter(env=self.env)

    def test_add_energy(self):
        self.power_meter.add_energy(123)
        self.assertEqual(
            self.power_meter.energy_produced, 123)
        self.assertEqual(self.power_meter.total_fed_in_electricity, 0)
        self.power_meter.consume_energy(0)
        self.assertEqual(
            self.power_meter.total_fed_in_electricity, 123 / self.env.steps_per_measurement)


if __name__ == '__main__':
    unittest.main()
