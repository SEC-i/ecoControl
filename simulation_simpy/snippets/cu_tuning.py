if (thermal_consumer.get_outside_temperature() > 10):
    cu.workload = 50

if (heat_storage.get_temperature() >= heat_storage.max_temperature - 5):
    cu.workload = 40
    
    
# BHKW wird hier nur noch 1 mal statt 8000 mal ausgeschaltet, etwa gleiche Kostenbilanz