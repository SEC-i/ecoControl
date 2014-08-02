import unittest

from server.devices.base import BaseEnvironment
from server.forecasting.devices.producers import SimulatedCogenerationUnit
from server.forecasting.devices.storages import SimulatedHeatStorage, SimulatedPowerMeter

from helpers import values_comparison
from mock import Mock

gas_price_per_kwh = 0.0655


class SimulatedCogenerationUnitTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        print "\ntesting producers",

    def setUp(self):
        self.env = BaseEnvironment()
        self.heat_storage = Mock(spec=SimulatedHeatStorage)()
        self.power_meter = Mock(spec=SimulatedPowerMeter)
        self.cu = SimulatedCogenerationUnit(1, self.env)
        self.cu.heat_storage = self.heat_storage
        self.cu.power_meter = self.power_meter


    def test_creation(self):
        self.assertGreaterEqual(self.cu.workload, 0)
        self.assertGreater(self.cu.config['max_gas_input'], 0)
        self.assertTrue(0 <= self.cu.config['electrical_efficiency'] <= 1)
        self.assertTrue(0 <=  self.cu.config['thermal_efficiency'] <= 1)

        self.assertTrue(0 <= self.cu.max_efficiency_loss <= 1)
        self.assertGreaterEqual(self.cu.config['maintenance_interval_hours'], 0)

        self.assertTrue(0 <= self.cu.config['minimal_workload'] <= 1)

        self.assertGreaterEqual(self.cu.config['minimal_off_time'], 0)

        self.assertEqual(self.cu.off_time, self.env.now)

        self.assertEqual(self.cu.current_electrical_production, 0)
        self.assertEqual(self.cu.total_electrical_production, 0)
        self.assertTrue(self.cu.thermal_driven)

        self.assertIsNone(self.cu.overwrite_workload)

    def test_get_electrical_energy_production(self):
        # the method should return the energy produced in one time intervall
        self.cu.current_electrical_production = 20.0 # Energy per hour
        expected_energy = self.cu.current_electrical_production * self.env.step_size / 3600.0

        result_energy = self.cu.get_electrical_energy_production()

        self.assertEqual(expected_energy, result_energy)

    def test_get_thermal_energy_production(self):
        # the method should return the energy produced in one time intervall
        self.cu.current_thermal_production = 20.0 # Energy per hour
        expected_energy = self.cu.current_thermal_production * self.env.step_size / 3600.0
        result_energy = self.cu.get_thermal_energy_production()

        self.assertEqual(expected_energy, result_energy)

    def test_calculate_new_workload(self):
        # calculates a workload
        # it considers overwrites workload and
        # the mode and
        # offtime

        #consider mode thermal
        self.heat_storage.get_required_energy.return_value = 3
        expected_workload = self.cu.get_calculated_workload_thermal()
        self.cu.thermal_driven = True
        calculated_workload = self.cu.calculate_new_workload()
        self.assertEqual(calculated_workload, expected_workload,
            "thermal workload is wrong")

        #consider mode electric
        self.heat_storage.target_temperature = 1000
        self.power_meter.current_power_consum = 3
        expected_workload = self.cu.get_calculated_workload_electric()
        self.cu.thermal_driven = False
        calculated_workload = self.cu.calculate_new_workload()
        self.assertEqual(calculated_workload, expected_workload,
                            "electrical workload is wrong expected: \
                            {0}. got: {1}"\
                            .format(expected_workload, calculated_workload))

        #consider overwrite of workload
        self.heat_storage.get_required_energy.return_value = 3
        expected_workload = self.cu.get_calculated_workload_thermal()
        self.cu.thermal_driven = True
        self.cu.overwrite_workload = 0.25
        calculated_workload = self.cu.calculate_new_workload()
        self.assertEqual(calculated_workload, 0.25,
            "overwritten workload is wrong expected: {0}. got: {1}"
            .format(0.25, calculated_workload))

        #consider offtime
        self.cu.overwrite_workload = None
        self.heat_storage.get_required_energy.return_value = 3
        expected_workload = 0
        self.cu.thermal_driven = True
        self.cu.off_time = self.env.now + 1
        calculated_workload = self.cu.calculate_new_workload()
        self.assertEqual(calculated_workload, expected_workload,
            "overwritten workload is wrong expected: {0}. got: {1}"
            .format(expected_workload, calculated_workload))

    def test_get_operating_costs(self):
        # are sum of gas_costs and maintenance
        self.cu.total_gas_consumption = 6.0
        self.cu.total_electrical_production = 3
        # needed, because the maintenance_costs are calculated
        # out of the electrical_production

        result = self.cu.get_operating_costs()

        # greater because of additional maintenance costs
        self.assertGreater(result, gas_price_per_kwh*6.0)

    def test_get_efficiency_loss_factor(self):
        # given efficiency is reached only on maximum workload
        # at minumum workload the efficiency is decreased with
        # max_efficiency_loss
        # the method returns the remaining efficiency
        self.cu.workload = 0.40
        self.cu.config['minimal_workload'] = 0.40
        self.cu.max_efficiency_loss = 0.05

        calculated_loss = self.cu.get_efficiency_loss_factor()

        self.assertEqual(calculated_loss, 0.95)

    def test_get_calculated_workload_thermal(self):
        # the function returns the needed workload based on the thermal demand
        # dont't know why but the workload is mapped to 0-99
        required_energy = 5
        gas_input = 20 # unit is energy: kWh
        thermal_efficiency = 0.6

        self.heat_storage.get_required_energy.return_value = required_energy
        self.cu.config['max_gas_input'] = gas_input
        self.cu.config['thermal_efficiency'] = thermal_efficiency

        max_energy = thermal_efficiency * gas_input
        expected_workload = required_energy / max_energy

        calculated_result = self.cu.get_calculated_workload_thermal()

        self.assertEqual(calculated_result, expected_workload)

    def test_get_calculated_workload_electric(self):
        # the function returns the needed workload based on the electric demand
        # dont't know why but the workload is mapped to 0-99
        self.heat_storage.target_temperature = 100
        self.heat_storage.get_temperature.return_value = 0

        required_energy = 5.0
        gas_input = 20.0 # unit is energy: kWh
        electrical_efficiency = 0.6
        minimal_workload = 20.0

        self.power_meter.current_power_consum = required_energy
        self.cu.config['max_gas_input'] = gas_input
        self.cu.config['electrical_efficiency'] = electrical_efficiency

        max_energy = electrical_efficiency*gas_input
        expected_workload = required_energy/max_energy

        calculated_result = self.cu.get_calculated_workload_electric()

        self.assertAlmostEqual(calculated_result, expected_workload)

    def test_get_calculated_workload_electric_heat_storage_filled(self):
        # if the target_temperature of the heat-storage is reached
        # the workload has to be zero
        self.heat_storage.target_temperature = 100
        self.heat_storage.temperature = 100

        self.power_meter.current_power_consum = 5.0
        self.cu.config['max_gas_input'] = 20.0 # unit is energy: kWh
        self.cu.config['electrical_efficiency'] = 0.60

        calculated_result = self.cu.get_calculated_workload_electric()

        self.assertAlmostEqual(calculated_result, 0)

class SimulatedCogenerationUnitMethodUpdateParametersTest(unittest.TestCase):
    def setUp(self):
        self.env = BaseEnvironment()
        self.heat_storage = Mock(spec=SimulatedHeatStorage)
        self.power_meter = SimulatedPowerMeter(0, self.env)
        self.cu = SimulatedCogenerationUnit(1, self.env)
        self.cu.heat_storage = self.heat_storage
        self.cu.power_meter = self.power_meter

        self.cu.config['minimal_workload'] = 0.20
        self.cu.off_time = self.env.now - 1
        self.gas_input = 20.0
        self.cu.config['max_gas_input'] = self.gas_input
        self.electrical_efficiency = 0.25
        self.cu.config['electrical_efficiency'] = self.electrical_efficiency
        self.thermal_efficiency = 0.7
        self.cu.config['thermal_efficiency'] = self.thermal_efficiency
        self.total_hours_of_operation = 1
        self.cu.total_hours_of_operation = self.total_hours_of_operation

    def test_normal_workload(self):
        '''The given workload shouldn't be altered if the workload is valid.
            current gas consumption,
            current electrical production,
            current thermal production and
            total_hours_of_operation
            should be set.
        '''
        precalculated_workload = 0.5

        self.cu.set_workload(precalculated_workload)
        self.cu.consume_and_produce_energy()

        expected_current_gas_consumption = self.gas_input * \
            precalculated_workload

        complete_current_power = expected_current_gas_consumption * \
            self.cu.get_efficiency_loss_factor()

        expected_current_electrical_production = self.electrical_efficiency * \
            complete_current_power
        expected_current_thermal_production = self.thermal_efficiency * \
            complete_current_power

        # assumption: self.env.step_size are seconds per step
        self.total_hours_of_operation += self.env.step_size/(60.0*60.0)

        self.assertEqual(self.cu.workload, precalculated_workload,
            "new workload is wrong. " +
            values_comparison(self.cu.workload, precalculated_workload))
        self.assertEqual(self.cu.current_gas_consumption,
            expected_current_gas_consumption,
            "current_gas_consumption is wrong. " +
            values_comparison(self.cu.current_gas_consumption,
                expected_current_gas_consumption))
        self.assertAlmostEqual(self.cu.current_electrical_production,
            expected_current_electrical_production)
        self.assertAlmostEqual(self.cu.current_thermal_production,
            expected_current_thermal_production)
        self.assertEqual(self.cu.total_hours_of_operation,
            self.total_hours_of_operation,
            "total_hours_of_operation is wrong. " +
            values_comparison(self.cu.total_hours_of_operation,
                self.total_hours_of_operation))

    def test_power_on_count(self):
        ''' the cu should increment the power on count
        if the cu was turned off
        and is turned on again'''
        precalculated_workload = 0.5
        self.cu.workload = 0 # means the cu was turned off
        power_on_count = 0
        self.cu.power_on_count = power_on_count

        self.cu.set_workload(precalculated_workload)

        self.assertEqual(self.cu.power_on_count, power_on_count + 1)

    def test_power_on_count_unaffected(self):
        ''' the cu musn't increment the power on count
        if the cu was turned on'''
        precalculated_workload = 0.35
        self.cu.workload = 25 # means the cu was turned on
        power_on_count = 0
        self.cu.power_on_count = power_on_count

        self.cu.set_workload(precalculated_workload)

        self.assertEqual(self.cu.power_on_count, power_on_count)

    def test_too_low_workload(self):
        ''' The workload should be zero if the given workload is
        less than the minimal workload.'''
        precalculated_workload = 0.10
        old_hours = self.total_hours_of_operation

        self.cu.set_workload(precalculated_workload)

        self.assertEqual(self.cu.workload, 0,
            "workload is wrong. " +
            values_comparison(self.cu.workload, 0))
        self.assertEqual(self.cu.current_gas_consumption, 0,
            "current_gas_consumption is wrong. " +
            values_comparison(self.cu.current_gas_consumption, 0))
        self.assertEqual(self.cu.current_electrical_production, 0,
            "current_electrical_production is wrong. " +
            values_comparison(self.cu.current_electrical_production, 0))
        self.assertEqual(self.cu.current_thermal_production, 0,
            "current_thermal_production is wrong. " +
            values_comparison(self.cu.current_thermal_production, 0))
        self.assertEqual(self.cu.total_hours_of_operation, old_hours,
            "total_hours_of_operation is wrong. " +
            values_comparison(self.cu.total_hours_of_operation, old_hours))

    def test_too_high_workload(self):
        '''If the workload is greater than 1 it should be truncated to 1.'''
        precalculated_workload = 2.0

        self.cu.set_workload(precalculated_workload)
        self.cu.consume_and_produce_energy()

        expected_current_gas_consumption = self.gas_input

        complete_current_power = expected_current_gas_consumption * \
            self.cu.get_efficiency_loss_factor()

        expected_current_electrical_production = self.electrical_efficiency * \
            complete_current_power
        expected_current_thermal_production = self.thermal_efficiency * \
            complete_current_power
        # assumption: self.env.step_size are seconds per step
        self.total_hours_of_operation += self.env.step_size/(60.0*60.0)

        self.assertEqual(self.cu.workload, 1,
            "wrong workload. " +
            values_comparison(self.cu.workload, 1))
        self.assertEqual(self.cu.current_gas_consumption,
            expected_current_gas_consumption,
            "wrong current_gas_consumption. " +
            values_comparison(self.cu.current_gas_consumption,
            expected_current_gas_consumption))
        self.assertEqual(self.cu.current_electrical_production,
            expected_current_electrical_production,
            "wrong expected_current_electrical_production. " +
            values_comparison(self.cu.current_electrical_production,
            expected_current_electrical_production))
        self.assertEqual(self.cu.current_thermal_production,
            expected_current_thermal_production,
            "wrong current_thermal_production. " +
            values_comparison(self.cu.current_thermal_production,
            expected_current_thermal_production))
        self.assertEqual(self.cu.total_hours_of_operation,
            self.total_hours_of_operation,
            "wrong total_hours_of_operation. " +
            values_comparison(self.cu.total_hours_of_operation,
            self.total_hours_of_operation))

    def test_workload_off_time_effective(self):
        '''If the offtime is in the future the bhkw must stay turned off.'''
        self.cu.off_time = self.env.now + 1
        old_hours = self.total_hours_of_operation

        self.cu.set_workload(self.cu.calculate_new_workload())

        self.assertEqual(self.cu.workload, 0,
            "workload is wrong. " +
            values_comparison(self.cu.workload, 0))
        self.assertEqual(self.cu.current_gas_consumption, 0,
            "current_gas_consumption is wrong. " +
            values_comparison(self.cu.current_gas_consumption, 0))
        self.assertEqual(self.cu.current_electrical_production, 0,
            "current_electrical_production is wrong." +
            values_comparison(self.cu.current_electrical_production, 0))
        self.assertEqual(self.cu.current_thermal_production, 0,
            "current_thermal_production is wrong . " +
            values_comparison(self.cu.current_thermal_production, 0))
        self.assertEqual(self.cu.total_hours_of_operation, old_hours,
            "total_hours_of_operation is wrong. " +
            values_comparison(self.cu.total_hours_of_operation, old_hours))

    def test_turn_bhkw_off(self):
        '''If the cu is turned off, there must be an offtime
        which determines the time the cu stays turned off
        '''
        self.cu.workload = 0.30
        new_workload = 0
        self.cu.thermal_driven = True
        required_energy = 0.0
        self.heat_storage.get_required_energy.return_value = required_energy
        off_time = self.env.now
        self.cu.off_time = off_time

        self.cu.set_workload(new_workload)

        self.assertGreater(self.cu.off_time, off_time)

    def test_consume_and_produce_energy(self):
        '''increases total_gas_consumtion,
        total_thermal_production and
        total_electrical_production
        all are measured in energy'''
        self.cu.total_gas_consumption = 0
        self.cu.total_thermal_production = 0
        self.cu.total_electrical_production = 0
        self.cu.workload = 1

        self.cu.consume_and_produce_energy()

        self.assertGreater(self.cu.total_gas_consumption,0,
            "wrong total_gas_consumption. " +
            values_comparison(self.cu.total_gas_consumption,0))
        self.assertGreater(self.cu.total_thermal_production,0,
            "wrong total_thermal_production " +
            values_comparison(self.cu.total_thermal_production,0))
        self.assertGreater(self.cu.total_electrical_production,0,
            "wrong total_electrical_production" +
            values_comparison(self.cu.total_electrical_production,0))

class SimulatedCogenerationUnitMethodStepTest(unittest.TestCase):
    def setUp(self):
        self.env = BaseEnvironment()
        self.heat_storage = Mock(spec=SimulatedHeatStorage)()
        self.power_meter = SimulatedPowerMeter(0, self.env)
        self.cu = SimulatedCogenerationUnit(1, self.env)
        self.cu.heat_storage = self.heat_storage
        self.cu.power_meter = self.power_meter

        self.max_gas_input = 19.0
        self.cu.config['max_gas_input'] = self.max_gas_input
        self.electrical_efficiency = 0.25
        self.cu.config['electrical_efficiency'] = self.electrical_efficiency
        self.thermal_efficiency = 0.6
        self.cu.config['thermal_efficiency'] = self.thermal_efficiency
        self.max_efficiency_loss = 0.10
        self.cu.max_efficiency_loss = self.max_efficiency_loss
        self.maintenance_interval_hours = 2000
        self.cu.config['maintenance_interval_hours'] = self.maintenance_interval_hours
        self.minimal_workload = 0.40
        self.cu.config['minimal_workload'] = self.minimal_workload
        self.cu.config['minimal_off_time'] = 5.0 * 60.0
        self.off_time = self.env.now
        self.cu.off_time = self.off_time
        self.current_electrical_production = 0.0
        self.cu.current_electrical_production = self.current_electrical_production
        self.total_electrical_production = 0.0
        self.cu.total_electrical_production = self.total_electrical_production
        self.total_thermal_production = 0.0
        self.cu.total_thermal_production = self.total_thermal_production

        self.total_gas_consumption = 0.0
        self.cu.total_gas_consumption = self.total_gas_consumption


        self.cu.overwrite_workload = None
        self.cu.running = True

        self.heat_storage.input_energy = 0
        self.power_meter.energy_produced = 0

#
#   test step()
##        '''step calculates a new workload depending on the mode
#        in dependence of the workload the attributes
#        of the cu:
#        the total_electrical_production
#        the total_gas_consumption
#        total_thermal_production
#        will be altered
#        energy_produced of the power_meter will be increased
#        input_energy of the heat_storage will be increased
#        if the cu is turned off. a off time must be set.
#        '''

    def test_step_not_running(self):
        self.cu.workload = 1
        self.cu.running = False
        self.cu.thermal_driven = True
        self.heat_storage.required_energy = 20

        self.heat_storage.get_required_energy.return_value = 20
        self.heat_storage.temperature = 0.0
        self.heat_storage.get_temperature.return_value = 0.0
        self.heat_storage.target_temperature = 0.0
        self.heat_storage.input_energy = 0

        self.cu.step()

        self.assertEqual(self.cu.workload, 0, "wrong workload. " +
            values_comparison(self.cu.workload, 0))
        self.assertEqual(self.cu.total_electrical_production, 0,
            "wrong total_electrical_production. " +
            values_comparison(self.cu.total_electrical_production, 0))
        self.assertEqual(self.cu.total_gas_consumption, 0,
            "wrong total_gas_consumption. " +
            values_comparison(self.cu.total_gas_consumption, 0))
        self.assertEqual(self.cu.total_thermal_production, 0,
            "wrong total_thermal_production. " +
            values_comparison(self.cu.total_thermal_production, 0))
        self.assertEqual(self.power_meter.energy_produced, 0,
            "wrong energy_produced (power_meter). " +
            values_comparison(self.power_meter.energy_produced, 0))
        self.assertEqual(self.heat_storage.input_energy, 0,
            "wrong input_energy (heat_storage). " +
            values_comparison(self.heat_storage.input_energy, 0))

    def test_step_running_thermal_too_little_workload(self):
        '''if the workload is too low, the cu will be turned off
        and the effective workload is zero'''
        self.cu.thermal_driven = True

        self.heat_storage.get_required_energy.return_value = 0.1
        self.power_meter.energy_produced = 0.0 #ToDo

        self.cu.step()

        # caluclates_workload
        # = required_energy/max_gas_amount_input*thermal_efficiency
        # 0.1/(19*0.65) < 40 (minimal workload)

        self.assertEqual(self.cu.workload, 0, "wrong workload. " +
            values_comparison(self.cu.workload, 0))
        self.assertEqual(self.cu.total_electrical_production, 0,
            "wrong total_electrical_production. " +
            values_comparison(self.cu.total_electrical_production, 0))
        self.assertEqual(self.cu.total_gas_consumption, 0,
            "wrong total_gas_consumption. " +
            values_comparison(self.cu.total_gas_consumption, 0))
        self.assertEqual(self.cu.total_thermal_production, 0,
            "wrong total_thermal_production. " +
            values_comparison(self.cu.total_thermal_production, 0))
        self.assertEqual(self.power_meter.energy_produced, 0,
            "wrong energy_produced (power_meter). " +
            values_comparison(self.power_meter.energy_produced, 0))
        self.assertEqual(self.heat_storage.input_energy, 0,
            "wrong input_energy (heat_storage). " +
            values_comparison(self.heat_storage.input_energy, 0))

    def test_step_thermal(self):
        #if the mode is thermal the cu will produce energy
        #according to the thermal demand
        self.cu.thermal_driven = True

        required_energy = 5.0
        self.heat_storage.get_required_energy.return_value = required_energy

        self.cu.step()

        expected_workload = self.calculate_workload(required_energy,
                                self.thermal_efficiency)
        new_gas_consumption = self.calculate_gas_consumption(expected_workload)
        self.total_gas_consumption += new_gas_consumption

        new_electrical_energy = self.calculate_energy(expected_workload,
                                    self.electrical_efficiency)
        self.total_electrical_production += new_electrical_energy

        new_thermal_energy = self.calculate_energy(expected_workload,
                                    self.thermal_efficiency)
        self.total_thermal_production += new_thermal_energy

        expected_energy_produced = self.cu.get_electrical_energy_production()
        expected_input_energy = self.cu.get_thermal_energy_production()

        self.assertAlmostEqual(self.cu.workload, expected_workload,
            "wrong workload. " +
            values_comparison(self.cu.workload, expected_workload))
        self.assertAlmostEqual(self.cu.total_electrical_production,
            self.total_electrical_production,
            msg="wrong total_electrical_production. " +
            values_comparison(self.cu.total_electrical_production,
            self.total_electrical_production))
        self.assertAlmostEqual(self.cu.total_gas_consumption,
            self.total_gas_consumption,
            msg="wrong total_gas_consumption. " +
            values_comparison(self.cu.total_gas_consumption,
                self.total_gas_consumption))
        self.assertAlmostEqual(self.cu.total_thermal_production,
            self.total_thermal_production,
            msg="wrong total_thermal_production. " +
            values_comparison(self.cu.total_thermal_production,
            self.total_thermal_production))
        self.assertAlmostEqual(self.power_meter.energy_produced,
            expected_energy_produced,
            msg= "wrong energy_produced(power_meter)" +
            values_comparison(self.power_meter.energy_produced,
            expected_energy_produced))
        self.heat_storage.add_energy.assert_called_with(expected_input_energy)

    def test_step_electric(self):
        #if the mode is electric the cu will produce energy
        #according to the electric demand

        self.cu.thermal_driven = False

        self.heat_storage.temperature = 0.0
        self.heat_storage.get_temperature.return_value = 0.0
        self.heat_storage.target_temperature = 90.0
        required_energy = 2.0
        self.power_meter.current_power_consum = required_energy

        self.cu.step()

        expected_workload = self.calculate_workload(required_energy,
                                self.electrical_efficiency)

        new_gas_consumption = self.calculate_gas_consumption(expected_workload)
        self.total_gas_consumption += new_gas_consumption

        new_electrical_energy = self.calculate_energy(expected_workload,
                                    self.electrical_efficiency)
        self.total_electrical_production += new_electrical_energy

        new_thermal_energy = self.calculate_energy(expected_workload,
                                    self.thermal_efficiency)
        self.total_thermal_production += new_thermal_energy

        expected_energy_produced = self.cu.get_electrical_energy_production()
        expected_input_energy = self.cu.get_thermal_energy_production()
        self.assertAlmostEqual(self.cu.workload, expected_workload,
            msg="wrong workload " +
            values_comparison(self.cu.workload, expected_workload))
        self.assertAlmostEqual(self.cu.total_electrical_production,
            self.total_electrical_production,
            msg="wrong total_electrical_production " +
            values_comparison(self.cu.total_electrical_production,
            self.total_electrical_production))
        self.assertAlmostEqual(self.cu.total_gas_consumption,
            self.total_gas_consumption,
            msg="wrong total_gas_consumption " +
            values_comparison(self.cu.total_gas_consumption,
            self.total_gas_consumption))
        self.assertAlmostEqual(self.cu.total_thermal_production,
            self.total_thermal_production,
            msg="wrong total_thermal_production. " +
            values_comparison(self.cu.total_thermal_production,
            self.total_thermal_production))
        self.assertAlmostEqual(self.power_meter.energy_produced,
            expected_energy_produced,
            msg="wrong energy_produced(power_meter)" +
            values_comparison(self.power_meter.energy_produced,
            expected_energy_produced))
        self.heat_storage.add_energy.assert_called_with(expected_input_energy)


    def test_step_turn_on_forbidden(self):
        ''' the cu musn't be paused (self_offtime active)'''
        #initialize with valid parameters
        self.cu.running = True

        # the offtime is effective!
        now = self.env.now
        self.cu.off_time = now + 1

        self.cu.thermal_driven = False

        self.heat_storage.get_temperature.return_value = 0.0
        self.heat_storage.target_temperature = 90.0
        self.heat_storage.get_required_energy.return_value=1000

        required_energy = 2.0
        self.power_meter.current_power_consum = required_energy

        self.cu.step()

        self.assertEqual(self.cu.workload, 0, "wrong workload " +
            values_comparison(self.cu.workload, 0))
        self.assertEqual(self.cu.total_electrical_production, 0,
            "wrong total_electrical_production " +
            values_comparison(self.cu.total_electrical_production, 0))
        self.assertEqual(self.cu.total_gas_consumption, 0,
            "wrong total_gas_consumption. " +
            values_comparison(self.cu.total_gas_consumption, 0))
        self.assertEqual(self.cu.total_thermal_production, 0,
            "wrong total_thermal_production " +
            values_comparison(self.cu.total_thermal_production, 0))
        self.assertEqual(self.power_meter.energy_produced, 0,
            "energy_produced(power_meter) " +
            values_comparison(self.power_meter.energy_produced, 0))
        self.heat_storage.add_energy.assert_called_with(0)

    def test_step_turn_target_temperature_reached(self):
        '''if the heat storage is too hot, the cu musn't produce energy
            although there is a demand for electrical energy'''
        self.cu.thermal_driven = False

        self.heat_storage.get_temperature.return_value = 10.0
        self.heat_storage.target_temperature = 10.0

        required_energy = 2.0
        self.power_meter.current_power_consum = required_energy

        self.cu.step()

        self.assertEqual(self.cu.workload, 0, "wrong workload " +
            values_comparison(self.cu.workload, 0))
        self.assertEqual(self.cu.total_electrical_production, 0,
            "wrong total_electrical_production " +
            values_comparison(self.cu.total_electrical_production, 0))
        self.assertEqual(self.cu.total_gas_consumption, 0,
            "wrong total_gas_consumption. " +
            values_comparison(self.cu.total_gas_consumption, 0))
        self.assertEqual(self.cu.total_thermal_production, 0,
            "wrong total_thermal_production " +
            values_comparison(self.cu.total_thermal_production, 0))
        self.assertEqual(self.power_meter.energy_produced, 0,
            "energy_produced(power_meter) " +
            values_comparison(self.power_meter.energy_produced, 0))
        self.heat_storage.add_energy.assert_called_with(0)

    def test_step_workload_too_high(self):
        '''if the workload is too high, the cu will be running at a workload
        of 100 %'''

        self.cu.thermal_driven = False

        self.heat_storage.get_temperature.return_value = 0.0
        self.heat_storage.target_temperature = 90.0
        self.heat_storage.get_required_energy.return_value=1000

        required_energy = 500.0
        self.power_meter.current_power_consum = required_energy

        self.cu.step()

        expected_workload = 1
        new_gas_consumption = self.calculate_gas_consumption(expected_workload)
        self.total_gas_consumption += new_gas_consumption

        new_electrical_energy = self.calculate_energy(expected_workload,
                                    self.electrical_efficiency)
        self.total_electrical_production += new_electrical_energy

        new_thermal_energy = self.calculate_energy(expected_workload,
                                    self.thermal_efficiency)
        self.total_thermal_production += new_thermal_energy

        self.assertEqual(self.cu.workload, expected_workload,
            "wrong workload" +
            values_comparison(self.cu.workload, expected_workload))
        self.assertEqual(self.cu.total_electrical_production,
            self.total_electrical_production,
            "wrong total_electrical_production. " +
            values_comparison(self.cu.total_electrical_production,
            self.total_electrical_production))
        self.assertAlmostEqual(self.cu.total_gas_consumption,
            self.total_gas_consumption,
            "total_gas_consumption " + values_comparison(
                self.cu.total_gas_consumption, self.total_gas_consumption))
        self.assertAlmostEqual(self.cu.total_thermal_production,
            self.total_thermal_production, "wrong total_thermal_production" +
                values_comparison(self.cu.total_thermal_production,
                self.total_thermal_production))
        self.assertEqual(self.power_meter.energy_produced,
            new_electrical_energy, "wrong energy_produced (power_meter)" +
            values_comparison(self.power_meter.energy_produced,
            new_electrical_energy))
        self.heat_storage.add_energy.assert_called_with(new_thermal_energy)

    def test_step_turn_bhkw_off(self):
        '''If the cu is turned off, there must be an offtime
        which determines the time the cu stays turned off
        '''
        self.cu.workload = 30
        self.cu.thermal_driven = True

        self.heat_storage.get_temperature.return_value = 0.0
        self.heat_storage.target_temperature = 90.0

        required_energy = 0.0
        self.heat_storage.get_required_energy.return_value = required_energy
        minimal_off_time = 40.0 * 60.0
        self.cu.config['minimal_off_time'] = minimal_off_time

        self.cu.step()

        self.assertGreaterEqual(self.cu.off_time,
            self.off_time + minimal_off_time)

    def calculate_energy(self, workload, efficiency):
        return self.max_gas_input * workload * efficiency * \
            self.cu.get_efficiency_loss_factor() * self.env.step_size/(60*60)

    def calculate_gas_consumption(self, workload):
        return self.max_gas_input * workload * \
            self.env.step_size/(60*60)

    def calculate_workload(self, energy_demand, efficiency):
        return energy_demand/(self.max_gas_input * efficiency)