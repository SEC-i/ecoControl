from django.db import models


class Device(models.Model):
    HS = 0  # HeatStorage(self.env)
    PM = 1  # PowerMeter(self.env)
    CU = 2  # CogenerationUnit(self.env, self.hs, self.pm)
    PLB = 3  # PeakLoadBoiler(self.env, self.hs)
    TC = 4  # ThermalConsumer(self.env, self.hs)
    EC = 5  # ElectricalConsumer(self.env, self.pm)
    DEVICE_TYPES = (
        (HS, 'HeatStorage'),
        (PM, 'PowerMeter'),
        (CU, 'CogenerationUnit'),
        (PLB, 'PeakLoadBoiler'),
        (TC, 'ThermalConsumer'),
        (EC, 'ElectricalConsumer'),
    )

    name = models.CharField(max_length=100)
    device_type = models.PositiveSmallIntegerField(choices=DEVICE_TYPES)

    def __unicode__(self):
        return self.name + " (#" + str(self.pk) + ")"


class Configuration(models.Model):
    STR = 0
    INT = 1
    FLOAT = 2
    DATE = 3
    TYPES = (
        (STR, 'str'),
        (INT, 'int'),
        (FLOAT, 'float'),
        (DATE, 'date'),
    )

    key = models.CharField(max_length=100)
    value = models.CharField(max_length=255)
    value_type = models.PositiveSmallIntegerField(
        choices=TYPES, default=STR)
    unit = models.CharField(max_length=50)
    internal = models.BooleanField(default=False)


class DeviceConfiguration(models.Model):

    """
    Does not inherit from Configuration because of bulk creation
    """
    STR = 0
    INT = 1
    FLOAT = 2
    DATE = 3
    TYPES = (
        (STR, 'str'),
        (INT, 'int'),
        (FLOAT, 'float'),
        (DATE, 'date'),
    )

    device = models.ForeignKey('Device')
    key = models.CharField(max_length=100)
    value = models.CharField(max_length=255)
    value_type = models.PositiveSmallIntegerField(
        choices=TYPES, default=STR)
    unit = models.CharField(max_length=50)
    tunable = models.BooleanField(default=False)


class Sensor(models.Model):
    device = models.ForeignKey('Device')
    name = models.CharField(max_length=100)
    key = models.CharField(max_length=100)
    setter = models.CharField(max_length=100)
    unit = models.CharField(max_length=50)
    in_diagram = models.BooleanField(default=False)
    aggregate_sum = models.BooleanField(default=False)
    aggregate_avg = models.BooleanField(default=False)

    def __unicode__(self):
        return self.name + " (#" + str(self.pk) + ")"


class SensorValue(models.Model):
    sensor = models.ForeignKey('Sensor')
    value = models.FloatField()
    timestamp = models.DateTimeField(auto_now=False, db_index=True)

    def __unicode__(self):
        return str(self.pk) + " (" + self.sensor.name + ")"


class SensorValueHourly(models.Model):
    sensor = models.ForeignKey('Sensor')
    timestamp = models.DateTimeField(auto_now=False)
    value = models.FloatField()

    class Meta:
        managed = False


class SensorValueDaily(models.Model):
    sensor = models.ForeignKey('Sensor')
    date = models.DateField(auto_now=False)
    value = models.FloatField()

    class Meta:
        managed = False

    def __unicode__(self):
        return str(self.pk) + " (" + self.sensor.name + ")"


class SensorValueMonthlySum(models.Model):
    sensor = models.ForeignKey('Sensor')
    date = models.DateField(auto_now=False)
    sum = models.FloatField()

    class Meta:
        managed = False

    def __unicode__(self):
        return str(self.pk) + " (" + self.sensor.name + ")"


class SensorValueMonthlyAvg(models.Model):
    sensor = models.ForeignKey('Sensor')
    date = models.DateField(auto_now=False)
    avg = models.FloatField()

    class Meta:
        managed = False

    def __unicode__(self):
        return str(self.pk) + " (" + self.sensor.name + ")"


class Threshold(models.Model):
    Default = 0
    Primary = 1
    Success = 2
    Info = 3
    Warning = 4
    Danger = 5

    TYPES = (
        (Default, 'Default'),
        (Primary, 'Primary'),
        (Success, 'Success'),
        (Info, 'Info'),
        (Warning, 'Warning'),
        (Danger, 'Danger'),
    )

    sensor = models.ForeignKey('Sensor')
    name = models.CharField(max_length=100)
    category = models.PositiveSmallIntegerField(choices=TYPES, default=Default)
    show_manager = models.BooleanField(default=False)
    min_value = models.FloatField(null=True, blank=True)
    max_value = models.FloatField(null=True, blank=True)

    def __unicode__(self):
        return str(self.pk) + " (" + self.sensor.name + ")"


class Notification(models.Model):
    threshold = models.ForeignKey('Threshold')
    sensor_value = models.ForeignKey('SensorValue')
    read = models.BooleanField(default=False)

    def __unicode__(self):
        return str(self.pk) + " (" + self.threshold.name + ")"
