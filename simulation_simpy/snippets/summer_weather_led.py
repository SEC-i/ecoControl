# thermal_consumer electrical_consumer plb env heat_storage power_meter cu
# thermal_consumer electrical_consumer plb env heat_storage power_meter cu
# average of the next 7 days
sum = 0
for i in range(7):
    sum += thermal_consumer.get_outside_temperature(i + 1)

avg = sum / 7.0
hs_temp = heat_storage.get_temperature()

if ((env.get_day_of_year() > 120) and (env.get_day_of_year() < 270)):
    plb.overwrite_workload = 0
    heat_storage.min_temperature = 50.0
    heat_storage.max_temperature = 70.0
    if hs_temp < heat_storage.max_temperature:
        if hs_temp < heat_storage.min_temperature and avg < 15.0:
            cu.overwrite_workload = 80.0
        elif hs_temp < heat_storage.min_temperature and avg > 15.0:
            cu.overwrite_workload = 60.0
        else:
            cu.overwrite_workload = 40.0
    else:
        cu.overwrite_workload = 0.0
                
        
else:
    cu.thermal_led = True
