from urllib import urlopen, urlencode
import json
import datetime
from django.utils.timezone import utc


class UnitControlServer():

    def __init__(self, env, heat_storage, power_meter, cu, plb, thermal_consumer, electrical_consumer):
        self.interval = 60.0  # seconds
        self.id = 1

        self.env = env
        self.heat_storage = heat_storage
        self.power_meter = power_meter
        self.cu = cu
        self.plb = plb
        self.thermal_consumer = thermal_consumer
        self.electrical_consumer = electrical_consumer
        self.data = {
            'bhkw_consumption': 0,
            'bhkw_thermal_production': 0,
            'bhkw_electrical_production': 0,
            'bhkw_workload': 0,
            'plb_consumption': 0,
            'plb_thermal_production': 0,
            'plb_workload': 0,
            'hs_temperature': 0,
            'hs_max_temperature': 0,
            'hs_min_temperature': 0,
            'pm_feed_in': 0,
            'pm_purchased_electricity': 0,
            'tc_consumption': 0,
            'ec_consumption': 0
        }

    def step(self):
        if self.env.now % self.interval == 0:
            # calculate average values
            for key in ['bhkw_workload', 'plb_workload', 'hs_temperature', 'hs_max_temperature', 'hs_min_temperature']:
                self.data[key] /= self.interval

            if self.env.real_time:
                # send all data to all devices
                for device_id in [1, 2, 3, 4, 5, 6]:
                    try:
                        urlopen(
                            "http://localhost:8000/api/device/" +
                            str(device_id) + "/data/",
                            urlencode([('data', json.dumps(self.data))]))
                    except:
                        pass
            else:
                now = str(datetime.datetime.fromtimestamp(
                    self.env.now).replace(tzinfo=utc))
                if self.env.now % 86400 == 0:
                    print now
                with open("data.txt", "a") as f:
                    f.write(str(self.id + 1) + "\t1\t" + str(self.data['bhkw_consumption']) + "\t" + now + "\n" + str(self.id + 2) + "\t2\t" + str(self.data['bhkw_thermal_production']) + "\t" + now + "\n" + str(self.id + 3) + "\t3\t" + str(self.data['bhkw_electrical_production']) + "\t" + now + "\n" + str(self.id + 4) + "\t4\t" + str(self.data['bhkw_workload']) + "\t" + now + "\n" + str(self.id + 5) + "\t5\t" + str(self.data['plb_consumption']) + "\t" + now + "\n" + str(self.id + 6) + "\t6\t" + str(self.data['plb_thermal_production']) + "\t" + now + "\n" + str(self.id + 7) + "\t7\t" + str(self.data['plb_workload']) + "\t" + str(
                            now) + "\n" + str(self.id + 8) + "\t8\t" + str(self.data['hs_temperature']) + "\t" + now + "\n" + str(self.id + 9) + "\t9\t" + str(self.data['hs_max_temperature']) + "\t" + now + "\n" + str(self.id + 10) + "\t10\t" + str(self.data['hs_min_temperature']) + "\t" + now + "\n" + str(self.id + 11) + "\t11\t" + str(self.data['pm_feed_in']) + "\t" + now + "\n" + str(self.id + 12) + "\t12\t" + str(self.data['pm_purchased_electricity']) + "\t" + now + "\n" + str(self.id + 13) + "\t13\t" + str(self.data['tc_consumption']) + "\t" + now + "\n" + str(self.id + 14) + "\t14\t" + str(self.data['ec_consumption']) + "\t" + now + "\n")
                self.id += 14

            # reset data
            for key in self.data:
                self.data[key] = 0
        else:
            self.data['bhkw_consumption'] += self.cu.current_gas_consumption / \
                self.env.steps_per_measurement
            self.data['bhkw_thermal_production'] += self.cu.current_thermal_production / \
                self.env.steps_per_measurement
            self.data['bhkw_electrical_production'] += self.cu.current_electrical_production / \
                self.env.steps_per_measurement
            self.data['bhkw_workload'] += self.cu.workload
            self.data['plb_consumption'] += self.plb.current_gas_consumption / \
                self.env.steps_per_measurement
            self.data['plb_thermal_production'] += self.plb.current_thermal_production / \
                self.env.steps_per_measurement
            self.data['plb_workload'] += self.plb.workload
            self.data['hs_temperature'] += self.heat_storage.get_temperature()
            self.data[
                'hs_max_temperature'] += self.heat_storage.target_temperature
            self.data[
                'hs_min_temperature'] += self.heat_storage.min_temperature
            if self.power_meter.balance < 0:
                self.data[
                    'pm_purchased_electricity'] -= self.power_meter.balance
            else:
                self.data['pm_feed_in'] += self.power_meter.balance
            self.data['tc_consumption'] += self.thermal_consumer.get_consumption_energy(
            ) + self.thermal_consumer.get_warmwater_consumption_energy()
            self.data[
                'ec_consumption'] += self.electrical_consumer.get_consumption_energy()
