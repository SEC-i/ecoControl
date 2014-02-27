# Turn off plb on 1'st April
if env.get_day_of_year() == 120:
    plb.overwrite_workload = 0
    
if ((env.get_day_of_year() > 120) and (env.get_day_of_year() < 240)):
    
    # Turn bhkw on lowest level if min_temperature is reached
    if (heat_storage.get_temperature() <= heat_storage.min_temperature + 5):
        cu.overwrite_workload = cu.minimal_workload
    # Turn off on max_temperature
    if (heat_storage.get_temperature() >= heat_storage.max_temperature - 2 ):
        cu.overwrite_workload = 0
        
# Normal from 1'st September
if (env.get_day_of_year() == 242):
    cu.overwrite_workload = None
    plb.overwrite_workload = None

# Saves 200 € and 9000 cu power-on's (some empty's)
