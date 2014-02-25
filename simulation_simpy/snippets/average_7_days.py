# average of the next 7 days
sum = 0
for i in range(7):
    sum += thermal_consumer.get_outside_temperature(i + 1)

avg = sum / 7.0

if avg < 5.0:
    heat_storage.max_temperature = 82
else:
    heat_storage.max_temperature = 78
