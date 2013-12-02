import logging
from urllib import urlopen, urlencode

logger = logging.getLogger('webapi')

def handle_post_data(data):
    if 'switch_number' in data:
        try:
            switch_number = data['switch_number']
            if int(switch_number) in range(1,5):
                if 'switch_state' in data:
                    if data['switch_state'] == "on":
                        # turn on
                        post_data = [('switch_number', switch_number), ('switch_state', "on"), ('api_key', "s3cr3t")]
                    else:
                        # turn off
                        post_data = [('switch_number', switch_number), ('switch_state', "off"), ('api_key', "s3cr3t")]
                else:
                    # toggle
                    post_data = [('switch_number', switch_number), ('api_key', "s3cr3t")]
            urlopen("http://localhost:9001/api/switches/", urlencode(post_data))
            logger.info("Send data to raspberrypi (" + urlencode(post_data) + ")")
        except ValueError:
            logger.error("ValueError in raspberrypi driver")
