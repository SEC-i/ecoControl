import logging
from urllib import urlopen, urlencode

logger = logging.getLogger('webapi')

def handle_post_data(data):
    if 'workload' in data:
        post_data = [('workload', data['workload'])]
        urlopen("http://localhost:9000/device/0/set", urlencode(post_data))
        logger.info("Send data to bhkw (" + urlencode(post_data) + ")")
