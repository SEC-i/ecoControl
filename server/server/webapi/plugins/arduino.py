import logging
from urllib import urlopen, urlencode

logger = logging.getLogger('webapi')

def handle_post_data(data):
    if 'water_plants' in data:
        post_data = [('water_plants', "1")]
        urlopen("http://localhost:9002/set/", urlencode(post_data))
        logger.info("Send data to arduino (" + urlencode(post_data) + ")")
