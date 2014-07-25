from server.settings import BASE_DIR
import os
from csv import writer
import dateutil
import calendar



def export_csv(sensordata_sets, name="evaluation.csv", plot_series="all"):
        try:
            import matplotlib.pyplot as plt
        except:
            pass
        with open(os.path.join(BASE_DIR,name), 'w') as csv:
            w = writer(csv, delimiter='\t')
            labels = ["date"]
            for sensordata in sensordata_sets:
                for index, dataset in enumerate(sensordata):
                    if plot_series == "all" or dataset["system"] + dataset["key"] in plot_series:
                        labels.append(dataset["system"] + " " + dataset["key"])
            w.writerow(labels)
                       
            dates = [dateutil.parser.parse(data_tuple[0]) for data_tuple in sensordata_sets[0][0]["data"]]
            for i,_date in enumerate(dates):
                row = []
                row.append(_date)
                for sensordata in sensordata_sets:
                    for dataset in sensordata:
                        if plot_series == "all" or dataset["system"] + dataset["key"] in plot_series:
                            try:
                                row.append(dataset["data"][i][1])
                            except:
                                print "error in row", i, "with dataset ", dataset["key"]
                w.writerow(row)


def export_rows(sensordata_sets,name="evaluation.txt", plot_series="all"):
    try:
        import matplotlib.pyplot as plt
    except:
        pass
    with open(os.path.join(BASE_DIR,name), 'w') as _file:   
        date_data = zip(*sensordata_sets[0][0]["data"])[0]                   
        dates = [calendar.timegm(dateutil.parser.parse(date).timetuple()) for date in date_data]
        output = "dates: "
        for d in dates:
            output += str(d) + ","
        
        for sensordata in sensordata_sets:
            for dataset in sensordata:
                if plot_series == "all" or dataset["system"] + dataset["key"] in plot_series:
                    output += dataset["system"] + " " + dataset["key"] + ": "
                    for t,v in dataset["data"]:
                        output += str(v) + ","
                    output += "\n\n\n"
        _file.write(output)
        print "finito"
        
        
