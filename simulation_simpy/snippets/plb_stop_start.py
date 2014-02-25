# Peak-Load Boiler nur anschalten, sobald Heat Storage unter die Minimale
# Schwelle fällt UND das BHKW unter einer bestimmten Last X fährt.
plb.stop()

if ((heat_storage.get_temperature() < heat_storage.min_temperature) & (cu.workload >= 99) & (thermal_consumer.get_consumption() >= cu.current_thermal_production - 10)):
    plb.start()
else:
    plb.stop()
if ((heat_storage.get_temperature() < 20) & (cu.workload >= 80)):
    plb.start()
