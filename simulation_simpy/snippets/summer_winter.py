if ((env.get_day_of_year() > 120) & (env.get_day_of_year() < 240)):
    cu.stop()
else:
    cu.start()

    if (heat_storage.get_temperature() >= heat_storage.max_temperature - 5):
        cu.workload = 40


# Sommer-Winter-regel. Funktioniert noch nicht so gut (etwa 200 Euro schlechter als ohne Regeln