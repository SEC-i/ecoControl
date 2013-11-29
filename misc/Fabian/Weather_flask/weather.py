from flask import Flask, render_template
import md5
import requests
import xml.etree.ElementTree as ElementTree

app = Flask(__name__)

apikey = "df7924a35131a1c7772038fd465be5ff"
project = "teeest"
berlin = "DE0001020"

@app.route("/")
def main():
    forecastData = requests.get("http://api.wetter.com/forecast/weather/city/" + berlin + "/project/" + project + "/cs/" + getDigest(berlin)).content
    forecastTree = ElementTree.XML(forecastData)
    tx = forecastTree.findall(".//tx")
    tn = forecastTree.findall(".//tn")
    w = forecastTree.findall(".//w")
    pc = forecastTree.findall(".//pc")
    return render_template('index.html', forecast = forecastData, minTemperatures = tn, maxTemperatures = tx, condition = w, rain = pc)
    
def getDigest(var):
    m = md5.new()
    m.update(project + apikey + var)
    return m.hexdigest()

if __name__ == "__main__":
    app.run(debug=True)
