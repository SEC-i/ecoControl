import urllib2
from csv import writer
from sys import exit, argv
import string
from datetime import datetime
import time

#fpkeys = "146%2C119%2C120%2C193%2C121%2C178%2C122%2C194%2C195%2C190%2C189%2C123%2C192%2C187%2C124%2C181%2C125%2C126%2C197%2C127%2C199%2C200%2C201%2C245%2C244%2C243%2C182%2C196%2C185%2C188%2C183%2C184%2C179%2C130%2C131%2C186%2C132%2C133%2C147%2C148%2C134%2C135%2C136%2C137%2C138%2C139%2C180%2C149%2C128%2C141%2C142%2C144%2C145%2C143%2C113%2C191%2C114%2C115%2C150%2C116%2C111%2C112%2C117%2C198%2C118%2C242%2C241%2C240%2C239%2C238%2C237%2C236%2C235%2C99%2C100%2C101%2C102%2C103%2C104%2C105%2C106%2C107%2C108%2C109%2C110%2C153%2C206%2C154%2C151%2C205%2C152%2C176%2C202%2C177%2C160%2C207%2C161%2C162%2C208%2C163%2C164%2C209%2C165%2C166%2C210%2C167%2C168%2C211%2C169%2C170%2C212%2C171%2C172%2C213%2C173%2C174%2C214%2C175%2C215%2C217%2C216%2C218%2C219%2C220%2C222%2C221%2C224%2C223%2C225%2C227%2C226%2C229%2C228%2C230%2C232%2C231%2C234%2C233%2C91%2C92%2C93%2C94%2C95%2C96%2C97%2C98%2C83%2C84%2C85%2C86%2C87%2C82%2C88%2C89%2C90%2C71%2C72%2C73%2C74%2C80%2C81%2C79%2C78%2C75%2C76%2C77%2C60%2C61%2C62%2C63%2C67%2C68%2C69%2C70%2C64%2C65%2C66%2C49%2C50%2C51%2C52%2C56%2C57%2C58%2C59%2C53%2C54%2C55%2C38%2C39%2C40%2C41%2C45%2C46%2C47%2C48%2C42%2C43%2C44%2C27%2C28%2C29%2C30%2C34%2C35%2C36%2C37%2C31%2C32%2C33%2C16%2C18%2C17%2C26%2C22%2C23%2C24%2C25%2C19%2C20%2C21%2C"
fpkeys = "170%2C201%2C202%2C112%2C113%2C114%2C37%2C180%2C35%2C62%2C38%2C39%2C181%2C"

<<<<<<< Updated upstream
start = '1.1.2013'
end = '12.6.2014'
=======
start = '1.1.2012'
end = '12.6.2013'
>>>>>>> Stashed changes

unix_timestamps=True
if len(argv) > 2:
    start = argv[1]
    end = argv[2]
    unix_timestamps = argv[3]

#electric current
#values = ["fselect_176=44307"]
values = ["fselect_37=13952","fselect_35=49547"]

values = '&'.join(values)

#url = "https://smarthome.stahl-neuendorf.de/graphen/multigraph_holen.php?start=%s&stop=%s&anzeigen=SET&%s&fpkeys=%s" % (start, end, values, fpkeys)
url = "http://www.online-bhkw.de/graphen/multigraph_kat_holen.php?start=%s&stop=%s&anzeigen=SET&kat=Energie&%s&fpkeys=%s" % (start, end, values, fpkeys)

#passwd = urllib2.HTTPPasswordMgrWithDefaultRealm()
#passwd.add_password(None, url, 'Kirchdorf', 'Neuendorf')
#authhandler = urllib2.HTTPBasicAuthHandler(passwd)
#opener = urllib2.build_opener(authhandler)
try:
    result = urllib2.urlopen(url, timeout=1000000)
except urllib2.URLError:
    print "Could not open url"
    exit(-1)

chart_data = None
chart_settings = None
for line in result.read().split('\n'):
    if line.find('chart_data') >= 0:
        chart_data = line
    if line.find('chart_settings') >= 0:
        chart_settings = line
        # Furhter founds are duplicates
        if chart_data is not None:
            break

# Extract labels
# Bad formatting doesn't allow automatic xml parsing
settings = chart_settings.split('"')[1]
labels = []
for line in settings.split("title"):
    # Search for the real title tags
    if 4 < len(line) < 100:
        labels.append(line[1:-2])

# Formate csv data
data = chart_data.split('"')[1]
csv = open('Electricity_2013Reger.csv', 'w')
w = writer(csv, delimiter='\t')
w.writerow(['Datum'] + labels )
print labels
# Here you see the very bad encoding of the site!
for row in data.split("\\n"):
    if row != "":
        datestr = string.strip(row.split(";")[0])
        if datestr != "Datum":
            d = datetime.strptime(datestr, "%d.%m.%Y %H:%M:%S")
            timestamp = int(time.mktime(d.timetuple()))          
        row_values = row.split(';')
        if unix_timestamps:
            row_values[0] = timestamp
        w.writerow(row_values)
csv.close()