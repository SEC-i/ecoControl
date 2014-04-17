from webscraping import download, xpath
from time import gmtime, strftime

day_values = []

def crawl(start, end):
      
    t0 = 1325376000 + 60 * 60 * 24 * start  # 1.1.2012
    D = download.Download()
    for i in range(start, end):
        start1 = gmtime(t0)
        
        url = "http://freemeteo.de/wetter/potsdam/Historie/taglicher-wetterruckblick/?gid=2852458&station=3306&date=%s&language=german&country=germany"
        
        html = D.get(url % strftime("%Y-%m-%d",start1))
        vals = []
        for row in xpath.search(html,"//table[@class='daily-history']/tbody/tr"):
            try:
                # temperature is in second column
                b_tag = xpath.search(row,"/td")[1]
                vals.append(int(b_tag[3:-7]))
            except ValueError:
                print "value error"
            except:
                print "error in xpath "
            

        t0 += 60 * 60 * 24
        if len(vals) < 24 and len(vals) != 0:
            print "error found %d values " %len(vals)
            vals += [vals[-1] for i in range(24 - len(vals))]
        if len(vals) > 24:
            vals = vals[:24]
        elif len(vals) == 0:
            print "no values found, use yesterday data"
            vals = day_values[-24:]
        day_values.extend(vals)



crawl(0,1)

print len(day_values)
print day_values
