from webscraping import download, xpath
from time import gmtime, strftime

day_values = []

def find_location(name):

    url = "http://freemeteo.de/wetter/search/?q=%s&language=german&country=germany"
    D = download.Download()
    html = D.get(url % name)
    first_result = None
    result = {}
    for entry in xpath.search(html, "//div[@class='today table']//table/tbody/tr"):
        country = xpath.search(entry, "/td")[2]
        first_column = xpath.search(entry, "/td")[0]
        name = xpath.search(first_column,"//a[1]")[0]
        path = "http://freemeteo.de" + xpath.search(first_column,"//a[1]/@href")[0]
        path = path.replace("&amp;","&")
        path = path.replace("Aktuelles-Wetter/Ort","Historie/taglicher-wetterruckblick")

        result[path] = {'country':country, 'name':name}

        if first_result is None:
            first_result = result.items()[0]
    return (first_result, result)

def crawl(url, start, end):
      
    t0 = 1325376000 + 60 * 60 * 24 * start  # 1.1.2012
    D = download.Download()
    for i in range(start, end):
        start1 = gmtime(t0)
        
        #url = "http://freemeteo.de/wetter/potsdam/Historie/taglicher-wetterruckblick/?gid=2852458&station=3306&date=%s&language=german&country=germany"
        
        html = D.get(url + "&date=" + strftime("%Y-%m-%d",start1))
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


cities =  find_location("Potsdam")
print cities[0]

crawl(cities[0][0],3,5)

print len(day_values)
print day_values
