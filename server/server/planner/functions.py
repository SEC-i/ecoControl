import logging

from datetime import datetime, timedelta
from django.utils.timezone import utc
from server.models import  Sensor, SensorEntry, SensorRule, SensorDelta, Task, Device
from server.webapi.plugins import arduino,raspberrypi

logger = logging.getLogger('planner')

last_sensor_entries = []

def simple_moisture_check():
    sensor_ids = [1,2,18] #plant ids
    try:
        sensor_entries = SensorEntry.objects.filter(sensor__in = sensor_ids).order_by("-timestamp")[:3]
        summed_value = 0.0
        for sensor_entry in sensor_entries:
            summed_value += float(sensor_entry.value)
        summed_value /= 3.0

        if simple_sensor_check(sensor_entries) != 0:
            logger.warning("Sensor value changed quickly (maybe damaged)")
            raspberrypi.handle_post_data({'switch_number':2, 'switch_state':'on'})
            return

        if summed_value < 400:
            arduino.handle_post_data({'water_plants':1})
            logger.debug("Water plants")
    
    except SensorEntry.DoesNotExist:
        logger.warning("No SensorEntries found")

def simple_sensor_check(sensor_entries):
    global last_sensor_entries
    if last_sensor_entries:
        # compare last value with new one
        for new_sensor_entry in sensor_entries:
            if new_sensor_entry.value < 10:
                return -1
            for old_sensor_entry in last_sensor_entries:
                if new_sensor_entry.sensor == old_sensor_entry.sensor:
                    if abs(float(new_sensor_entry.value) - float(old_sensor_entry.value)) > 50:
                        return -2

    last_sensor_entries = sensor_entries
    return 0

def simple_battery_check():
    try:
        sensor_entries = SensorEntry.objects.filter(sensor_id = 4).order_by("-timestamp")[:3]
        summed_value = 0.0
        for sensor_entry in sensor_entries:
            summed_value += float(sensor_entry.value)
        summed_value /= 3.0

        if summed_value < 11.0:
            raspberrypi.handle_post_data({'switch_number':1, 'switch_state':'on'}) #switch on charger
        elif summed_value > 13.0:
            raspberrypi.handle_post_data({'switch_number':1, 'switch_state':'off'}) #switch off charger
    
    except SensorEntry.DoesNotExist:
        pass

# crawl data and save sensor entries
def update_delta():
    logger.debug("update delta")
    for sensor in Sensor.objects.all():
        try:
            sensor_delta = SensorDelta.objects.get(sensor_id = sensor.id)
        except SensorDelta.DoesNotExist:
            sensor_delta = SensorDelta()
            sensor_delta.sensor_id = sensor.id
            sensor_delta.interval = 60 * 5 # 5 minutes
            sensor_delta.delta = None

        try:
            latest_data =  SensorEntry.objects.filter(sensor_id= sensor.id).latest('timestamp')
            
            date_before_interval = datetime.utcnow().replace(tzinfo=utc) - timedelta(seconds=int(sensor_delta.interval))
            #get the first dataSet from the data before the interval
            intervall_ago_data = SensorEntry.objects.filter(sensor_id= sensor.id, timestamp__lte= date_before_interval).latest('timestamp')
 

            current_delta  = float(latest_data.value) - float(intervall_ago_data.value)
            print current_delta, sensor_delta.delta
            
            if sensor_delta.delta == None:
                sensor_delta.delta = current_delta
            else:
                #weight the deltas
                sensor_delta.delta = 0.3 * float(sensor_delta.delta) + 0.7 * current_delta

            sensor_delta.timestamp = datetime.utcnow().replace(tzinfo=utc)
            sensor_delta.save()
        except SensorEntry.DoesNotExist:
            continue

def check_rules():
    #normally 2 days
    max_prediction_time = timedelta(days = 2)

    sensor_rules = SensorRule.objects.all()
    for rule in sensor_rules:
        #get newest  value
        sensor_value = SensorEntry.objects.filter(sensor_id = rule.sensor_id).order_by('-timestamp')[0].value
        #for safety reasons
        if (str(rule.comparison) not in ['<','>','==','>=','<=','!=']):
            continue
        try:
            sensor_delta = SensorDelta.objects.filter(sensor_id = rule.sensor_id).order_by('-timestamp')[0]
        except SensorDelta.DoesNotExist:
            continue
        #build condition condition with comparison (f.e <,>,=,..)
        condition_string = str( estimate_value(max_prediction_time,sensor_delta) ) + str(rule.comparison) + str(rule.threshold)
        #eval is not save
        if eval(condition_string) == True:
            create_or_update_task(rule,sensor_delta)
            return True #just for test
    return False

def create_or_update_task(rule, sensor_delta):
    try:
        tasks = Task.objects.get(sensor_id = rule.sensor_id)
        for task in tasks:
            date = estimate_date(rule.threshold, sensor_delta, rule)
            if date == None:
                return False
            task.execution_timestamp = date
            task.save()
    except Task.DoesNotExist:
        # no task created yet
        task = Task()
        task.sensor_id = rule.sensor_id
        task.command = rule.target_function
        task.status = 0 #off
        date = estimate_date(rule.threshold, sensor_delta, rule)
        if date == None:
            return False
        task.execution_timestamp = date
        task.save()

    return True
    logger.debug("updating or creating task")

def estimate_value(time_from_now, sensor_delta):
    "time_from_now = a timedelta, sensor_delta = a sensor_delta model object"
    try:
        latest_entry = SensorEntry.objects.filter(sensor = sensor_delta.sensor).latest('timestamp')
        latest_value = float(latest_entry.value)
        #simple linear estimation
        return latest_value + float(sensor_delta.delta) * timedelta_to_seconds(time_from_now)/float(sensor_delta.interval)
    except SensorEntry.DoesNotExist:
        logger.debug("no sensor entries available for estimation")
        return None    

def estimate_date(threshold,sensor_delta, sensor_rule):
    sensor = Sensor.objects.get(id = sensor_delta.sensor_id)
    try:
        latest_entry = SensorEntry.objects.filter(sensor_id = sensor.id).latest('timestamp')
        latest_value = float(latest_entry.value)
        # thresh = current + delta*num_intervals
        num_intervals = (float(sensor_rule.threshold) -  latest_value ) / float(sensor_delta.delta)
        estimated_date = datetime.utcnow() + timedelta(seconds = (num_intervals * float(sensor_delta.interval)))
        return estimated_date.replace(tzinfo=utc)
    except SensorEntry.DoesNotExist:
        logger.debug("no sensor entries available for estimation")
        return None

        

def timedelta_to_seconds(time_delta):
    return float(time_delta.days * 3600 * 24 + time_delta.seconds + round(time_delta.microseconds / (10**6)))
