from urllib import urlopen, urlencode

def handle_post_data(data):
    if 'water_plants' in data:
        post_data = [('water_plants', "1")]
        urlopen("http://localhost:9002/set/", urlencode(post_data))