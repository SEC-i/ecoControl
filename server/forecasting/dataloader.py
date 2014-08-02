import csv
import string
from datetime import timedelta, date, datetime
import os

class DataLoader(object):
    """ This class reads data from CSV formatted in a specific way. 
    The files are cached in memory to enable fast, re-reads"""
    cached_csv = {}
    
    @classmethod
    def load_from_file(cls,filepath, column_name, delim="\t",date_name="Datum", sampling_interval=600):
        """ load a time series from a csv file. This assumes, that the csv is formatted in the following way:

        ===========   ===========   =========== ============
        Date header   Row Header1   Row Header2 Row Header N
        ===========   ===========   =========== ============
        Timestamp0    Row1Value0    Row2Value0  RowNValue0
        Timestamp1    ...           ...         ...
        ===========   ===========   =========== ============
        If the values in the file isn't sampled evenly, because it contains skips, blackouts, etc.. the data will be sampled evenly by copying certain data (see :meth:`evenly_sampled`).

        :param string column_name: The name of the column (in the csv) to retrieve
        :param string delim: The delimiter between values of a row. Default is Tab.
        :param string date_name: The name of the Date header of the date row
        :param int sampling_interval: The interval the data in the file is sampled.
        """  
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
                              
                    cls.cached_csv[filepath] = cls.evenly_sampled(columns, date_name,sampling_interval)
        
        return cls.cached_csv[filepath][column_name]
    
    @classmethod
    def evenly_sampled(cls, data, date_name="Datum", sampling_interval=600):
        """ Will return a version of `data`, in which every value has a corresponding timestamp, 
        which  is roughly `sampling_interval` seconds away from the last value. This is a maximum interval,
        if the data contains closer values together than sampling_interval, no actions will be taken.

        The data which is used to fill up gaps is tried to gather intelligently. 
        It is specifically designed for electrical data and takes values from one week ago, if  present, else one day or the last value if everything else fails.


        :param dict data: dictionary with column names as keys and column data as values
        :param string date_name: name of the date row
        :param int sampling_interval: the number of seconds between each consecutive sample
        """
        samples_per_hour = (60 * 60) / sampling_interval
        epsilon = 59  # maximal 59 seconds deviatiation from samplinginterval
        dates = data[date_name]
        
        #empty copy
        output_data = {key : [] for key in data.keys()}
        
        for index, date in enumerate(dates):
            for key in data.keys():
                output_data[key].append(data[key][index])
            
            if index < len(dates) - 1:
                diff = int(dates[index+1]) - int(dates[index])
                time_passed = timedelta(seconds= int(date) - int(dates[0]))         
                
                if abs(diff - sampling_interval) > epsilon:
                    #read from back one week ago, if existent
                    if time_passed >= timedelta(days = 7):
                        back = 7 * 24 * samples_per_hour
                    #else only take last day
                    elif time_passed >= timedelta(days = 1):
                        back = 24 * samples_per_hour
                    else:
                        back = 1
                    
                    history_index = index - back
                    #stop at 10 minutes before next sample
                    stop = diff - sampling_interval + 1
                    for j in range(sampling_interval, stop, sampling_interval):
                        #repeat samples, if time difference is bigger than available data
                        adjusted_index = history_index + j % back
                        for key in data.keys():
                            if key == date_name:
                                output_data[key].append(int(date) + j)
                            else:
                                output_data[key].append(data[key][adjusted_index])
        return output_data