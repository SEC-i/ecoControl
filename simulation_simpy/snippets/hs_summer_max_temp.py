# Initialize variable
if 'old_max_temp' not in locals():
    old_max_temp = heat_storage.max_temperature

if (env.get_day_of_year() > 120) and (env.get_day_of_year() < 273):
    # In summer the heat_storage can cool down to min_temperature if 
    # max_temperature is reached
    if abs(heat_storage.max_temperature - heat_storage.get_temperature()) < 5:
        if old_max_temp == heat_storage.max_temperature:
            old_max_temp = heat_storage.max_temperature
            heat_storage.max_temperature = heat_storage.min_temperature
        # min_temperature is reached and heating should start
        else:
            heat_storage.max_temperature = old_max_temp
# Set back in winter
elif old_max_temp != heat_storage.max_temperature:
    heat_storage.max_temperature = old_max_temp

# 2000 € more expensive (longer bhkw up-time) but 9000 power on's less of bhkw and 1000 more of plb
