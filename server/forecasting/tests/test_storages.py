import unittest

from server.systems.base import BaseEnvironment
from server.forecasting.systems.storages import SimulatedHeatStorage, SimulatedPowerMeter

electrical_feed_in_reward_per_kwh = 0.0917
electrical_costs_per_kwh = 0.283


class SimulatedHeatStorageTests(unittest.TestCase):

    def setUp(self):
        self.env = BaseEnvironment()
        self.hs = SimulatedHeatStorage(0, env=self.env)

    def test_heat_storage_creation(self):
        self.assertGreater(self.hs.config['capacity'], 0)
        self.assertGreater(self.hs.base_temperature, 0)
        self.assertGreater(self.hs.config['min_temperature'], 0)

        self.assertGreater(self.hs.config['target_temperature'], self.hs.config['min_temperature'])
        self.assertGreater(
            self.hs.config['critical_temperature'], self.hs.config['target_temperature'])

        self.assertGreater(self.hs.specific_heat_capacity, 0)

        self.assertEqual(self.hs.input_energy, 0)
        self.assertEqual(self.hs.output_energy, 0)
        self.assertEqual(self.hs.empty_count, 0)

        self.assertGreater(self.hs.temperature_loss, 0)

    def test_energy_stored(self):
        self.hs.input_energy = 2
        self.hs.output_energy = 1
        self.assertEqual(self.hs.energy_stored(), 2 - 1)

    def test_get_require_energy(self):
        # target_energy should return the energy needed to fill the storage to
        # its target-temperature
        self.hs.input_energy = 9
        self.hs.output_energy = 1
        stored_energy = 9 - 1

        # get energy needed to get the energy needed to reach the
        # target_temperature from zero
        self.hs.base_temperature = 0
        self.hs.config['target_temperature'] = 70
        self.hs.specific_heat_capacity = 0.002
        self.hs.config['capacity'] = 2500
        target_energy = 0.002 * 70 * 2500

        # get energy needed to fill storage from the stored enrgy to its target
        # temperature
        required_energy = target_energy - stored_energy

        self.assertAlmostEqual(required_energy, self.hs.get_require_energy())

    def test_add_energy(self):
        self.hs.input_energy = 0
        for i in range(20):
            self.hs.add_energy(0.5)

        self.assertEqual(self.hs.input_energy, 20 * 0.5)

    def test_consume_energy(self):
        self.hs.input_energy = 2
        self.hs.output_energy = 0
        self.hs.consume_energy(2)

        self.assertEqual(self.hs.output_energy, 2)

    def test_consume_too_much_energy(self):
        self.hs.empty_count = 0
        self.hs.input_energy = 1
        self.hs.consume_energy(2)

        self.assertEqual(self.hs.empty_count, 1)
        self.assertEqual(self.hs.output_energy, 1)

    def test_get_temperatur(self):
        base_temperature = 1
        self.hs.base_temperature = base_temperature
        self.hs.input_energy = 1
        self.hs.ouput_energy = 0
        energy_stored = 1
        self.hs.config['capacity'] = 2500
        self.hs.specific_heat_capacity = 0.002

        # temperature = energy/capacity
        added_temperature = energy_stored / (2500 * 0.002)
        temperature = 1 + added_temperature

        self.assertEqual(temperature, self.hs.get_temperature())

    def test_get_energy_capacity(self):
        # max energy the storage can hold:
        # energy = capacity*TemperatureDiff
        max_temperature_diff = self.hs.config['critical_temperature'] - \
            self.hs.base_temperature
        max_energy = self.hs.specific_heat_capacity * \
            self.hs.config['capacity'] * max_temperature_diff

        self.assertEqual(max_energy, self.hs.get_energy_capacity())

    def test_undersupplied(self):
        self.hs.base_temperature = 0
        self.hs.input_energy = 0
        self.hs.config['min_temperature'] = 20

        self.assertTrue(self.hs.undersupplied())

        self.hs.base_temperature = 20

        self.assertFalse(self.hs.undersupplied())

    def test_step(self):
        self.hs.temperature_loss = 3.0 / 24.0   # per hour
        self.hs.config['capacity'] = 2500
        self.hs.specific_heat_capacity = 0.002
        self.env.step_size = 120  # 20 measurements per hour
        self.hs.output_energy = 0

        # capacity * temperature_loss
        energy_loss_per_hour = (2500 * 0.002) * (3.0 / 24.0)
        energy_loss_per_step = energy_loss_per_hour * \
            (self.env.step_size / 3600.0)  # divide steps

        self.hs.step()

        self.assertEqual(self.hs.output_energy, energy_loss_per_step)

        # Attention! The assumption of the storage is that the measurement intervall ist always one hour
        # If not the values are physically wrong!


class SimulatedPowerMeterTests(unittest.TestCase):

    def setUp(self):
        self.env = BaseEnvironment()
        self.power_meter = SimulatedPowerMeter(0, env=self.env)

    def test_power_meter_creation(self):
        self.assertEqual(self.power_meter.total_fed_in_electricity, 0)
        self.assertEqual(self.power_meter.total_purchased, 0)
        self.assertEqual(self.power_meter.energy_produced, 0)
        self.assertEqual(self.power_meter.energy_consumed, 0)

    def test_add_energy(self):
        self.power_meter.energy_produced = 0
        for i in range(20):
            self.power_meter.add_energy(0.5)

        self.assertEqual(self.power_meter.energy_produced, 20 * 0.5)

    def test_consume_energy(self):
        self.power_meter.energy_consumed = 0
        self.initialize_purchased_and_fed_in()

        for i in range(20):
            self.power_meter.consume_energy(0.5)

        self.assertEqual(self.power_meter.energy_consumed, 20 * 0.5)
        self.assertEqual(self.power_meter.total_purchased, 0)
        self.assertEqual(self.power_meter.total_fed_in_electricity, 0)

    def test_get_reward(self):
        self.power_meter.total_fed_in_electricity = 25

        self.assertEqual(
            self.power_meter.get_reward(), 25 * electrical_feed_in_reward_per_kwh)

    def test_get_costs(self):
        self.power_meter.total_purchased = 25

        self.assertEqual(
            self.power_meter.get_costs(), 25 * electrical_costs_per_kwh)

    def test_step_resets_energies(self):
        self.power_meter.energy_consumed = 3
        self.power_meter.energy_produced = 5

        self.power_meter.step()

        self.assertEqual(self.power_meter.energy_consumed, 0)
        self.assertEqual(self.power_meter.energy_produced, 0)

    def test_step_when_deficit_of_energy(self):
        self.power_meter.energy_consumed = 5
        self.power_meter.energy_produced = 3
        self.initialize_purchased_and_fed_in()

        self.power_meter.step()

        self.assertEqual(self.power_meter.total_purchased, 5 - 3)
        self.assertEqual(self.power_meter.total_fed_in_electricity, 0)

    def test_step_when_excess_of_energy(self):
        self.power_meter.energy_consumed = 3
        self.power_meter.energy_produced = 5
        self.initialize_purchased_and_fed_in()

        self.power_meter.step()

        self.assertEqual(self.power_meter.total_fed_in_electricity, 5 - 3)
        self.assertEqual(self.power_meter.total_purchased, 0)

    def test_step_no_energy_diff(self):
        self.power_meter.energy_consumed = 1
        self.power_meter.energy_produced = 1
        self.initialize_purchased_and_fed_in()

        self.power_meter.step()

        self.assertEqual(self.power_meter.total_fed_in_electricity, 0)
        self.assertEqual(self.power_meter.total_purchased, 0)

    def initialize_purchased_and_fed_in(self):
        self.power_meter.total_purchased = 0
        self.power_meter.total_fed_in_electricity = 0