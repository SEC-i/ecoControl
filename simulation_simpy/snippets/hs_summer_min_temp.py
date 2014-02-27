if 'summer' not in locals():
    summer = False
    
if (env.get_day_of_year() == 120) and not summer: # 1st May
    heat_storage.min_temperature -= 20
    summer = True
elif (env.get_day_of_year() == 273) and summer: # 1st October
    heat_storage.min_temperature += 20
    summer = False

# Saves no money but 1500 power on's of bhkw
