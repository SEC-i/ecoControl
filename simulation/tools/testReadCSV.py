from datetime import datetime
import time
import csv
import string
 
#----------------------------------------------------------------------
def csv_reader(file_obj):
    """
    Read a csv file
    """
    reader = csv.reader(file_obj)
    for row in reader:
        datestr = string.strip(row[0].split("\t")[0])
        if datestr != "Datum":
            d = datetime.strptime(datestr, "%d.%m.%Y %H:%M:%S")
            print int(time.mktime(d.timetuple()))
#----------------------------------------------------------------------
if __name__ == "__main__":
    csv_path = "result.csv"
    with open(csv_path, "rb") as f_obj:
        csv_reader(f_obj)
        
        
        
        

