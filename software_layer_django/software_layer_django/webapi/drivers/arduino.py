from urllib import urlopen, urlencode

def handle_post_data(data):
    if 'relay_state' in data:
        post_data = [('relay_state', "0")]
        if data['relay_state']=="1":
            post_data = [('relay_state', "1")]

        urlopen("http://localhost:9002/set/", urlencode(post_data))