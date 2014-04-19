import gzip
import functools
from cStringIO import StringIO as IO
from flask import after_this_request, request

from core.helpers import parse_hourly_demand_values


def gzipped(f):
    @functools.wraps(f)
    def view_func(*args, **kwargs):
        @after_this_request
        def zipper(response):
            accept_encoding = request.headers.get('Accept-Encoding', '')

            if 'gzip' not in accept_encoding.lower():
                return response

            response.direct_passthrough = False

            if (response.status_code < 200 or
                response.status_code >= 300 or
                'Content-Encoding' in response.headers):
                return response
            gzip_buffer = IO()
            gzip_file = gzip.GzipFile(mode='wb',
                                      fileobj=gzip_buffer)
            gzip_file.write(response.data)
            gzip_file.close()

            response.data = gzip_buffer.getvalue()
            response.headers['Content-Encoding'] = 'gzip'
            response.headers['Vary'] = 'Accept-Encoding'
            response.headers['Content-Length'] = len(response.data)

            return response

        return f(*args, **kwargs)

    return view_func


def update_simulation(simulation, settings_dict):
    general_config = cu_config = hs_config = plb_config = []
    for key, value in request.form.items():
        if key.startswith('general_'):
            general_config.append((key.replace('general_', ''), value))
        elif key.startswith('cu_'):
            cu_config.append((key.replace('cu_', ''), value))
        elif key.startswith('hs_'):
            hs_config.append((key.replace('hs_', ''), value))
        elif key.startswith('plb_'):
            plb_config.append((key.replace('plb_', ''), value))

    count = 0
    for (system, config) in [(simulation.cu, cu_config), (simulation.heat_storage, hs_config), (simulation.plb, plb_config), (simulation.thermal_consumer, [])]:
        for (variable, value) in config + general_config:
            if variable in dir(system):
                setattr(system, variable, parse_value(value))
                count += 1

    print count, len(cu_config) + len(plb_config) + len(hs_config) + len(general_config)

    # re-calculate values of thermal_consumer
    simulation.thermal_consumer.calculate()

    if 'password' in settings_dict and settings_dict['password'] == "InfoProfi" and 'code' in settings_dict:
        simulation.code_executer.create_function(settings_dict['code'])

    daily_thermal_demand = parse_hourly_demand_values(
        'daily_thermal_demand', settings_dict)
    if len(daily_thermal_demand) == 24:
        simulation.thermal_consumer.daily_demand = daily_thermal_demand

    daily_electrical_variation = parse_hourly_demand_values(
        'daily_electrical_variation', settings_dict)
    if len(daily_electrical_variation) == 24:
        simulation.electrical_consumer.demand_variation = daily_electrical_variation


def export_data(filename):
    if os.path.splitext(filename)[1] == ".json":
        data = main_simulation.get_main_measurements()
        for key in data:
            data[key] = data[key][-1]
        data = json.dumps(data, sort_keys=True, indent=4)
        with open(os.path.dirname(os.path.abspath(__file__)) + "/data/exports/" + filename, "w") as export_file:
            for line in data:
                export_file.write(line)
        return True
    return False


def parse_value(s):
    try:
        if s == 'True':
            return True
        elif s == 'False':
            return False
        elif s.count('.') == 1:
            return float(s)
        else:
            return int(s)
    except ValueError:
        return str(s)
