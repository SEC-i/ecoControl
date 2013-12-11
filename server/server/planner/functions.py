import logging

from datetime import datetime, timedelta
from django.utils.timezone import utc
from server.models import  Sensor, SensorEntry, SensorRule, SensorDelta, Task, Device

logger = logging.getLogger('planner')

# crawl data and save sensor entries
def update_delta():
    logger.debug("update delta")
    for sensor in Sensor.objects.all():
        # all rules to the sensor
        sensor_delta_list = SensorDelta.objects.all().filter(sensor_id= sensor.id)

        if len(sensor_delta_list) == 0:
            sensor_delta = SensorDelta()
            sensor_delta.sensor_id = sensor.id
            sensor_delta.interval = 60 * 5 # 5 minutes
            sensor_delta.delta = None
        else:
            sensor_delta = sensor_delta_list[0]
        


        newest_data = SensorEntry.objects.filter(sensor_id= sensor.id).order_by('-timestamp')[0]
        date_before_interval = datetime.now().replace(tzinfo=utc) - timedelta(seconds=int(sensor_delta.interval))
        #get the first dataSet from the data before the interval
        intervall_ago_data = SensorEntry.objects.filter(sensor_id= sensor.id, timestamp__lte= date_before_interval).order_by('-timestamp')
        
        if len(intervall_ago_data) == 0:
            continue

        current_delta  = float(newest_data.value) - float(intervall_ago_data[0].value)
        print current_delta, sensor_delta.delta
        
        if sensor_delta.delta == None:
            sensor_delta.delta = current_delta
        else:
            #weight the deltas
            sensor_delta.delta = 0.3 * float(sensor_delta.delta) + 0.7 * current_delta


        sensor_delta.timestamp = datetime.now().replace(tzinfo=utc)
        sensor_delta.save()




def check_rules():
    #normally 2 days
    max_prediction_time = timedelta(days=2)

    sensor_rules = SensorRule.objects.all()
    for rule in sensor_rules:
        #get newest  value
        sensor_value = SensorEntry.objects.all().filter(sensor_id= rule.sensor_id).order_by('-timestamp')[0].value
        #for safety reasons
        if (str(rule.comparison) not in ['<','>','==','>=','<=','!=']):
            continue
        sensor_deltas = SensorDelta.objects.filter(sensor_id= rule.sensor_id).order_by('-timestamp')
        if len(sensor_deltas) == 0:
            continue
        sensor_delta = sensor_deltas[0]
        #build condition condition with comparison (f.e <,>,=,..)
        condition_string = str( estimate_value(max_prediction_time,sensor_delta) ) + str(rule.comparison) + str(rule.threshold)
        #eval is not save
        if eval(condition_string) == True:
            create_or_update_task(rule,sensor_delta)
            return True #just for test
    return False

def create_or_update_task(rule,sensor_delta):
    tasks = Task.objects.all().filter(sensor_id= rule.sensor_id)
    # no task created yet
    if len(tasks) == 0:
        task = Task()
        task.sensor_id = rule.sensor_id
        task.command = rule.target_function
        task.status = 0 #off
        date = estimate_date(rule.threshold, sensor_delta, rule)
        if date == None:
            return False
        task.execution_timestamp = date
        task.save()
    else:
        for task in tasks:
            date = estimate_date(rule.threshold, sensor_delta, rule)
            if date == None:
                return False
            task.execution_timestamp = date
            task.save()
    return True
    logger.debug("updating or creating task")

def estimate_value(time_from_now,sensor_delta):
    "time_from_now = a timedelta, sensor_delta = a sensor_delta model object"
    sensor = Sensor.objects.get(id=sensor_delta.sensor_id)
    newest_data = SensorEntry.objects.filter(sensor_id=sensor.id).order_by('-timestamp')
    if len(newest_data) == 0:
        logger.debug("no sensor entries available for estimation")
        return None

    current_value = float(newest_data[0].value)
    #simple linear estimation
    estimated = current_value + float(sensor_delta.delta) * timedelta_to_seconds(time_from_now)/float(sensor_delta.interval)
    return estimated

def estimate_date(threshold,sensor_delta, sensor_rule):
    sensor = Sensor.objects.get(id=sensor_delta.sensor_id)
    newest_data = SensorEntry.objects.filter(sensor_id=sensor.id).order_by('-timestamp')
    if len(newest_data) == 0:
        logger.debug("no sensor entries available for estimation")
        return None

    current_value = float(newest_data[0].value)
    # thresh = current + delta*num_intervals
    num_intervals = (float(sensor_rule.threshold) -  current_value ) / float(sensor_delta.delta)
    estimated_date = datetime.now() + timedelta(seconds=(num_intervals * float(sensor_delta.interval)))
    return estimated_date.replace(tzinfo=utc)





def timedelta_to_seconds(time_delta):
    return float(time_delta.days* 3600 * 24 + time_delta.seconds + round(time_delta.microseconds / (10**6)))

def get_tasks():
    return Task.objects.all()



# dev = Device()
# dev.name = "arduino"
# dev.data_source = u"http://172.16.19.114:9002/get/"
# dev.interval = 30
# dev.save()

# sens = Sensor()
# sens.key_name = "plant2_value"
# sens.device_id = 1
# sens.name = "Plant #2"
# sens.unit = "hpi"
# sens.group = 0
# sens.save()
# for rule in SensorRule.objects.all():
#     rule.delete()

# rule = SensorRule()
# rule.sensor_id = 1
# rule.threshold = 598
# rule.target_function = "water_plants"
# rule.comparison = "<"
# rule.save()

# delta = SensorDelta()
# delta.id = 1
# delta.sensor_id = 1
# delta.delta = 5.0
# delta.interval = 60 * 5
# delta.timestamp = datetime.now().replace(tzinfo=utc)
# delta.save()


# deltas = SensorDelta.objects.all().filter(sensor_id= 2)[0]
# deltas.delete()