if ((env.get_day_of_year() > 140) and (env.get_day_of_year() < 270)):
    cu.thermal_led = False
else:
    cu.thermal_led = True
    


# Sommer-Winter-regel. Funktioniert noch nicht so gut (etwa 200 Euro schlechter als ohne Regeln