import csv
import string

class DataLoader(object):
    cached_csv = {}
    
    @classmethod
    def load_from_file(cls,filepath, column_name, delim="\t"):
        if filepath not in cls.cached_csv:
            if filepath.endswith(".csv"):
                with open(filepath, "rb") as file_obj:
                    reader = csv.reader(file_obj)
                    header = reader.next()
                    if type(header)== list:
                        header = header[0]
                    
                    labels = [string.strip(label) for label in header.split(delim)]
                    columns = {}
                    for label in labels:
                        columns[label] = []
                    
                    for row in reader:
                        _row = row
                        if type(row) == list:
                            _row = row[0]
                        elements = [string.strip(label) for label in _row.split(delim)]
                        for index, element in enumerate(elements):
                            label = labels[index]
                            columns[label].append(element)
                              
                    cls.cached_csv[filepath] = columns
        
        return cls.cached_csv[filepath][column_name]

#print len(DataLoader.load_from_file("../tools/result.csv", "Datum", "\t"))
print len(DataLoader.load_from_file("result.csv", "Strom - Allgemeinstrom (Aktuell)", "\t"))
                        