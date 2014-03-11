from webscraping import download, xpath
import re
import time
import threading




day_values = []

def iterate(start,end):
    t0 = 1325376000 + 60 * 60 * 24 * start #1.1.2013
    D = download.Download()
    for i in range(start,end):
        start1 = time.gmtime(t0)


        print (start1.tm_mday,start1.tm_mon,start1.tm_year)
        html = D.get("http://freemeteo.com/default.asp?pid=20&gid=2950159&la=3&sid=103850&lc=1&ndate=%s/%s/%s"%(start1.tm_mday,start1.tm_mon,start1.tm_year) )
        # temp_index =  html.find("<!-- Temperatur -->")
        # weather_index = html.find("<!-- Wetter -->")
        # html = html[temp_index:weather_index]

        vals = []
        for row in xpath.search(html, "//td[@class='tbl_stations_content_r']"):
            try:
                vals.append(int(row[:-11]))
            except:
                pass

        t0 += 60 * 60 * 24
        if len(vals) != 24 and len(vals) != 0:
            vals += [ vals[-1] for i in range(24 - len(vals))]
        elif len(vals) == 0:
            vals = day_values[-24:]
        day_values.extend(vals)



iterate(0,365)

print len(day_values)
print day_values
