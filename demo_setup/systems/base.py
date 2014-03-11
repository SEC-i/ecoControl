import traceback
import os
from urllib import urlopen, urlencode
import json


class CodeExecuter():

    def __init__(self, env, local_variables):
        self.env = env
        # split keys and values for performance reasons
        self.local_names = local_variables.keys()
        self.local_references = local_variables.values()

        # initialize code with names of local variables
        self.code = "#"
        for name in self.local_names:
            self.code += " " + name
        self.code += "\n"

        self.create_function(self.code)
        self.execution_successful = True

        parent_directory = os.path.dirname(
            os.path.dirname(os.path.abspath(__file__)))
        self.snippet_folder = parent_directory + "/snippets"

    def create_function(self, code):
        self.code = code

        lines = []
        lines.append("def user_function(%s):" %
                     (",".join(self.local_names)))

        for line in self.code.split("\n"):
            lines.append("\t" + line)
        lines.append("\tpass")  # make sure function is not empty

        source = "\n".join(lines)
        namespace = {}
        exec source in namespace  # execute code in namespace

        self._user_function = namespace['user_function']

    def step(self):
        try:
            self._user_function(*self.local_references)
            self.execution_successful = True
        except:
            if self.env.now % self.env.measurement_interval == 0:
                traceback.print_exc()
            self.execution_successful = False

    def snippets_list(self):
        output = []
        for filename in os.listdir(self.snippet_folder):
            if os.path.splitext(filename)[1] == ".py":
                output.append(filename)
        return output

    def get_snippet_code(self, snippet):
        if snippet in self.snippets_list():
            with open(self.snippet_folder + "/" + snippet, "r") as snippet_file:
                return snippet_file.read()
        return ""

    def save_snippet(self, snippet, code):
        if os.path.splitext(snippet)[1] == ".py" and code != "":
            with open(self.snippet_folder + "/" + snippet, "w") as snippet_file:
                snippet_file.write(code)
            return True

        return False


class UnitControlServer():

    def __init__(self, env, heat_storage, power_meter, cu, plb, thermal_consumer, electrical_consumer):
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
        if self.env.now % 3600 == 0:
            # calculate average values
            for key, val in self.data.iteritems():
                val /= 3600.0

            # send all data to all devices
            for device_id in [1, 2, 3, 4, 5, 6]:
                urlopen(
                    "http://localhost:8000/api/device/" +
                    str(device_id) + "/data/",
                    urlencode([('data', json.dumps(self.data))]))

            # reset data
            for key, val in self.data.iteritems():
                val = 0
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
