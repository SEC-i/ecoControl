import logging
import calendar
from datetime import date

from django.db.models import Sum

from server.models import System, Sensor, SensorValue, SensorValueMonthlySum
from server.functions import get_configuration

logger = logging.getLogger('django')


def get_total_balance_by_date(month, year):

    start = date(year, month, 1)
    end = date(year, month, calendar.mdays[month])

    # calculate costs
    sensor_ids = Sensor.objects.filter(
        system__system_type__in=[System.CU, System.PLB]).values_list('id', flat=True)

    sensor_values_sum = SensorValueMonthlySum.objects.filter(
        timestamp__gte=start, timestamp__lte=end, sensor_id__in=sensor_ids)

    sensor_values = sensor_values_sum.filter(
        sensor__key='current_gas_consumption')

    total_gas_consumption = 0
    for sensor_value in sensor_values:
        total_gas_consumption += sensor_value.sum

    gas_costs = get_configuration('gas_costs')
    costs = total_gas_consumption * gas_costs

    # Calculate electrical purchase
    sensor_ids = Sensor.objects.filter(
        system__system_type=System.PM).values_list('id', flat=True)
    sensor_values_sum = SensorValueMonthlySum.objects.filter(
        timestamp__gte=start, timestamp__lte=end, sensor_id__in=sensor_ids)
    sensor_values = sensor_values_sum.filter(sensor__key='purchased')

    total_electrical_purchase = 0
    for sensor_value in sensor_values:
        total_electrical_purchase += sensor_value.sum

    electrical_costs = get_configuration('electrical_costs')
    costs += total_electrical_purchase * electrical_costs

    # calculate rewards

    # thermal consumption
    sensor_ids = Sensor.objects.filter(
        system__system_type=System.TC).values_list('id', flat=True)
    sensor_values_sum = SensorValueMonthlySum.objects.filter(
        timestamp__gte=start, timestamp__lte=end, sensor_id__in=sensor_ids)
    sensor_values = sensor_values_sum.filter(
        sensor__key='get_consumption_power')

    total_thermal_consumption = 0
    for sensor_value in sensor_values:
        total_thermal_consumption += sensor_value.sum

    thermal_revenues = get_configuration('thermal_revenues')
    rewards = total_thermal_consumption * thermal_revenues

    # warmwater consumption
    sensor_values_sum = SensorValueMonthlySum.objects.filter(
        timestamp__gte=start, timestamp__lte=end, sensor_id__in=sensor_ids)
    sensor_values = sensor_values_sum.filter(
        sensor__key='get_warmwater_consumption_power')

    total_warmwater_consumption = 0
    for sensor_value in sensor_values:
        total_warmwater_consumption += sensor_value.sum

    warmwater_revenues = get_configuration('warmwater_revenues')
    rewards += total_warmwater_consumption * \
        get_configuration('warmwater_revenues')

    # electrical consumption
    sensor_ids = Sensor.objects.filter(
        system__system_type=System.EC).values_list('id', flat=True)
    sensor_values_sum = SensorValueMonthlySum.objects.filter(
        timestamp__gte=start, timestamp__lte=end, sensor_id__in=sensor_ids)
    sensor_values = sensor_values_sum.filter(
        sensor__key='get_consumption_power')

    total_electrical_consumption = 0
    for sensor_value in sensor_values:
        total_electrical_consumption += sensor_value.sum

    electrical_revenues = get_configuration('electrical_revenues')
    rewards += total_electrical_consumption * electrical_revenues

    # electrical infeed
    sensor_ids = Sensor.objects.filter(
        system__system_type=System.PM).values_list('id', flat=True)
    sensor_values_sum = SensorValueMonthlySum.objects.filter(
        timestamp__gte=start, timestamp__lte=end, sensor_id__in=sensor_ids)
    sensor_values = sensor_values_sum.filter(sensor__key='fed_in_electricity')

    total_electrical_infeed = 0
    for sensor_value in sensor_values:
        total_electrical_infeed += sensor_value.sum

    feed_in_reward = get_configuration('feed_in_reward')
    rewards += total_electrical_infeed * feed_in_reward

    return {
        'costs': round(-costs, 2),
        'rewards': round(rewards, 2),
        'balance': round(rewards - costs, 2),
        'prices': {
            'gas_costs': -gas_costs,
            'electrical_costs': -electrical_costs,
            'thermal_revenues': thermal_revenues,
            'warmwater_revenues': warmwater_revenues,
            'electrical_revenues': electrical_revenues,
            'feed_in_reward': feed_in_reward
        },
        'kwh': {
            'gas_consumption': round(total_gas_consumption, 2),
            'electrical_purchase': round(total_electrical_purchase, 2),
            'thermal_consumption': round(total_thermal_consumption, 2),
            'warmwater_consumption': round(total_warmwater_consumption, 2),
            'electrical_consumption': round(total_electrical_consumption, 2),
            'electrical_infeed': round(total_electrical_infeed, 2)
        }
    }