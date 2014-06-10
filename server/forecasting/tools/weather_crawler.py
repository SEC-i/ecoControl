from webscraping import download, xpath
from time import gmtime, strftime
from urllib2 import urlopen

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
        # Follow Temp Redirect (307) to find right url
        request = urlopen(path)
        path = request.geturl()
        path = path.replace("Aktuelles-Wetter/Ort","Historie/taglicher-wetterruckblick")

        result[path] = {'country':country, 'name':name}

        if first_result is None:
            first_result = result.items()[0]
    return (first_result, result)

def crawl(url, start, end):

    t0 = 1325376000 + 60 * 60 * 24 * (start-1)  # 1.1.2012
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
    return day_values


cities =  find_location("Potsdam")
print "Found %s cities." % len(cities[1])

crawl(cities[0][0],1,3)

print "Found %s temperature values: %s" % (len(day_values), day_values)